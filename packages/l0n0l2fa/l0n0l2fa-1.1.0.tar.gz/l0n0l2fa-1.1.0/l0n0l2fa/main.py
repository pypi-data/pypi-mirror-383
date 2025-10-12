from aiohttp import web
import pyotp
import qrcode
import io
import base64
import os
import json
import secrets
import time
import argparse
import ssl
TOKENS_FILE = "tokens_otp.json"

# ========== Token/Secret 管理 ==========


def load_or_create_tokens(path: str, num_users: int = 1):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            users = json.load(f)
    else:
        users = []
        for i in range(num_users):
            users.append({
                "token": secrets.token_hex(16),
                "user": f"user{i+1}@example.com",
                "secrets": [{"name": "default", "secret": pyotp.random_base32()}]
            })
        with open(path, "w", encoding="utf-8") as f:
            json.dump(users, f, indent=2, ensure_ascii=False)
    return users


USERS = []


def get_user_by_token(token: str):
    for u in USERS:
        if u["token"] == token:
            return u
    return None

# ========== API: 返回 OTP ==========


async def otp_api(request: web.Request) -> web.Response:
    token = request.query.get("token", "")
    user = get_user_by_token(token)
    if not user:
        return web.json_response({"error": "Invalid token"}, status=403)

    results = []
    for entry in user["secrets"]:
        name = entry["name"]
        secret = entry["secret"]
        totp = pyotp.TOTP(secret)
        results.append({
            "name": name,
            "otp": totp.now(),
            "valid_for": 30 - (int(time.time()) % 30)
        })

    return web.json_response({
        "user": user["user"],
        "otps": results
    })


# ========== API: 返回二维码 ==========
async def qrcode_handler(request: web.Request) -> web.Response:
    token = request.query.get("token", "")
    index = int(request.query.get("index", "0"))
    user = get_user_by_token(token)
    if not user or index >= len(user["secrets"]):
        return web.Response(text="Invalid token or index", status=403)

    entry = user["secrets"][index]
    name = entry["name"]
    secret = entry["secret"]

    totp = pyotp.TOTP(secret)
    uri = totp.provisioning_uri(
        name=f"{user['user']} ({name})", issuer_name="MyAiohttpApp")
    img = qrcode.make(uri)
    buf = io.BytesIO()
    img.save(buf, "PNG")
    img_bytes = buf.getvalue()
    b64 = base64.b64encode(img_bytes).decode("utf-8")
    html = f"<h3>扫描绑定 {user['user']} - {name}</h3><img src='data:image/png;base64,{b64}'>"
    return web.Response(text=html, content_type="text/html")

# ========== 网页 OTP 管理器 ==========


async def web_page(request: web.Request) -> web.Response:
    html = """
    <html>
    <head>
      <meta charset="utf-8"/>
      <title>多用户动态 OTP 页面</title>
      <style>
        .otp-box {
          margin: 10px 0;
          padding: 8px;
          border: 1px solid #ccc;
          width: 360px;
        }
        .progress {
          width: 300px;
          height: 20px;
          border: 1px solid #333;
          margin-top: 5px;
          position: relative;
        }
        .bar {
          height: 100%;
          width: 100%;
          transition: width 1s linear, background-color 0.5s;
        }
        .copy-btn, .qr-btn {
          margin-left: 10px;
          padding: 2px 6px;
          font-size: 12px;
          cursor: pointer;
        }
        #qr-modal {
          display: none;
          position: fixed;
          top: 50%; left: 50%;
          transform: translate(-50%, -50%);
          background: #fff;
          padding: 20px;
          border: 1px solid #333;
          box-shadow: 0 0 10px rgba(0,0,0,0.5);
        }
        #qr-modal img {
          max-width: 200px;
        }
      </style>
      <script>
        let intervalId = null;
        function copyToClipboard(text, btn) {
            if (navigator.clipboard && window.isSecureContext) {
                // 现代浏览器
                navigator.clipboard.writeText(text).then(() => {
                btn.innerText = "已复制!";
                setTimeout(() => btn.innerText = "复制", 1500);
                }).catch(err => {
                alert("复制失败: " + err);
                });
            } else {
                // 兼容旧浏览器
                const textarea = document.createElement("textarea");
                textarea.value = text;
                textarea.style.position = "fixed";  // 避免滚动
                document.body.appendChild(textarea);
                textarea.focus();
                textarea.select();
                try {
                document.execCommand("copy");
                btn.innerText = "已复制!";
                setTimeout(() => btn.innerText = "复制", 1500);
                } catch (err) {
                alert("复制失败: " + err);
                }
                document.body.removeChild(textarea);
            }
        }

        async function fetchOtp() {
          const token = document.getElementById("token").value.trim();
          if (!token) return;
          try {
            const resp = await fetch("/otp?token=" + token);
            if (!resp.ok) {
              document.getElementById("otp-list").innerHTML = "<p>无效 Token</p>";
              return;
            }
            const data = await resp.json();
            const container = document.getElementById("otp-list");
            container.innerHTML = "";

            data.otps.forEach((item, idx) => {
                const div = document.createElement("div");
                div.className = "otp-box";

                const otpLine = document.createElement("div");
                otpLine.innerHTML = "<b>" + data.user + " - " + item.name + ":</b> " + item.otp;

                const copyBtn = document.createElement("button");
                copyBtn.className = "copy-btn";
                copyBtn.innerText = "复制";
                copyBtn.onclick = () => copyToClipboard(item.otp, copyBtn);

                const qrBtn = document.createElement("button");
                qrBtn.className = "qr-btn";
                qrBtn.innerText = "显示二维码";
                qrBtn.onclick = async () => {
                    const qrResp = await fetch("/qrcode?token=" + token + "&index=" + idx);
                    if (qrResp.ok) {
                    const html = await qrResp.text();
                    document.getElementById("qr-modal").innerHTML = html + "<br><button onclick='closeQr()'>关闭</button>";
                    document.getElementById("qr-modal").style.display = "block";
                    }
                };
                const delBtn = document.createElement("button");
                delBtn.className = "del-btn";
                delBtn.innerText = "删除";
                delBtn.onclick = async () => {
                    if (!confirm("确定要删除 " + item.name + " 吗？")) return;
                    const resp = await fetch("/delete_secret", {
                        method: "POST",
                        headers: {"Content-Type": "application/json"},
                        body: JSON.stringify({token: token, index: idx})
                    });
                    const data = await resp.json();
                    if (resp.ok) {
                        alert("删除成功: " + data.message);
                        fetchOtp(); // 刷新列表
                    } else {
                        alert("删除失败: " + data.error);
                    }
                };

                otpLine.appendChild(delBtn);
                otpLine.appendChild(copyBtn);
                otpLine.appendChild(qrBtn);
                div.appendChild(otpLine);

                const span = document.createElement("span");
                span.innerText = "剩余 " + item.valid_for + " 秒";
                div.appendChild(span);

                const progress = document.createElement("div");
                progress.className = "progress";
                const bar = document.createElement("div");
                bar.className = "bar";
                const percent = (item.valid_for / 30) * 100;
                bar.style.width = percent + "%";

                if (item.valid_for > 20) {
                    bar.style.backgroundColor = "#4caf50";
                } else if (item.valid_for > 10) {
                    bar.style.backgroundColor = "#ff9800";
                } else {
                    bar.style.backgroundColor = "#f44336";
                }

                progress.appendChild(bar);
                div.appendChild(progress);
                container.appendChild(div);
            });
          } catch (e) {
                document.getElementById("otp-list").innerHTML = "<p>请求失败</p>";
          }
        }

        function start() {
            if (intervalId) clearInterval(intervalId);
            fetchOtp();
            intervalId = setInterval(fetchOtp, 1000);
        }

        function closeQr() {
            document.getElementById("qr-modal").style.display = "none";
        }

        function showAddForm() {
            document.getElementById("add-form").style.display = "block";
        }
        function hideAddForm() {
            document.getElementById("add-form").style.display = "none";
        }

        async function addPassword() {
            const token = document.getElementById("token").value.trim();
            const name = document.getElementById("new-name").value.trim();
            const secret = document.getElementById("new-secret").value.trim();

            if (!token || !name || !secret) {
                alert("请输入 Token、名称和秘钥");
                return;
            }

            const resp = await fetch("/add_secret", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({token, name, secret})
            });

            const data = await resp.json();
            if (resp.ok) {
                alert("添加成功: " + data.message);
                hideAddForm();
                fetchOtp(); // 刷新 OTP 列表
            } else {
                alert("添加失败: " + data.error);
            }
        }        
      </script>
    </head>
    <body>
        <h3>输入 Token 查看动态 OTP</h3>
        <input type="password" id="token" name="token" size="40" placeholder="请输入 Token" autocomplete="current-password"/>
        <button onclick="start()">确认</button>
        <button onclick="showAddForm()">➕ 添加密码</button>
        <div id="add-form" style="display:none; margin-top:10px; border:1px solid #ccc; padding:10px; width:300px;">
            <h4>添加新密码</h4>
            名称: <input type="text" id="new-name"/><br>
            秘钥: <input type="text" id="new-secret"/><br>
            <button onclick="addPassword()">确认添加</button>
            <button onclick="hideAddForm()">取消</button>
        </div>

        <div id="otp-list"></div>
        <div id="qr-modal"></div>
    </body>
    </html>
    """
    return web.Response(text=html, content_type="text/html")

# ========== 添加新密码接口 ==========


async def add_secret(request: web.Request) -> web.Response:
    try:
        data = await request.json()
    except:
        return web.json_response({"error": "Invalid JSON"}, status=400)

    token = data.get("token", "").strip()
    name = data.get("name", "").strip()
    secret = data.get("secret", "").strip()

    if not token or not name or not secret:
        return web.json_response({"error": "Missing fields"}, status=400)

    user = get_user_by_token(token)
    if not user:
        return web.json_response({"error": "Invalid token"}, status=403)

    # 添加新秘钥
    user["secrets"].append({"name": name, "secret": secret})

    # 写回文件
    with open(TOKENS_FILE, "w", encoding="utf-8") as f:
        json.dump(USERS, f, indent=2, ensure_ascii=False)

    return web.json_response({"status": "ok", "message": f"已为 {user['user']} 添加密码 {name}"})


# ========== 删除密码接口 ==========
async def delete_secret(request: web.Request) -> web.Response:
    try:
        data = await request.json()
    except:
        return web.json_response({"error": "Invalid JSON"}, status=400)

    token = data.get("token", "").strip()
    index = data.get("index")
    if token == "" or index is None:
        return web.json_response({"error": "Missing fields"}, status=400)

    user = get_user_by_token(token)
    if not user:
        return web.json_response({"error": "Invalid token"}, status=403)

    try:
        index = int(index)
    except:
        return web.json_response({"error": "Invalid index"}, status=400)

    if index < 0 or index >= len(user["secrets"]):
        return web.json_response({"error": "Index out of range"}, status=400)

    removed = user["secrets"].pop(index)

    # 写回文件
    with open(TOKENS_FILE, "w", encoding="utf-8") as f:
        json.dump(USERS, f, indent=2, ensure_ascii=False)

    return web.json_response({"status": "ok", "message": f"已删除 {user['user']} 的密码 {removed['name']}"})


# ========== 应用入口 ==========
def create_app():
    app = web.Application()
    app.router.add_get("/otp", otp_api)
    app.router.add_get("/qrcode", qrcode_handler)
    app.router.add_get("/web", web_page)
    app.router.add_post("/add_secret", add_secret)
    app.router.add_post("/delete_secret", delete_secret)

    return app

def main():
    parser = argparse.ArgumentParser(description="OTP 管理服务")
    parser.add_argument("--host", default="127.0.0.1", help="监听地址 (默认: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8080, help="监听端口 (默认: 8080)")
    parser.add_argument("--certfile", help="SSL 证书文件路径 (可选)")
    parser.add_argument("--keyfile", help="SSL 私钥文件路径 (可选)")
    parser.add_argument("--tokens", default="tokens_otp.json", help="Token 配置文件路径 (默认: tokens_otp.json)")
    args = parser.parse_args()

    # 使用指定的 token 配置文件
    global TOKENS_FILE
    TOKENS_FILE = args.tokens
    global USERS
    USERS = load_or_create_tokens(TOKENS_FILE)
    print("有效用户配置已加载：")
    for u in USERS:
        print(f"  user={u['user']} token={u['token']} secrets={len(u['secrets'])}")

    ssl_context = None
    if args.certfile and args.keyfile:
        ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        ssl_context.load_cert_chain(certfile=args.certfile, keyfile=args.keyfile)
        print(f"🔒 启用 HTTPS: https://{args.host}:{args.port}/web")
    else:
        print(f"🌐 启用 HTTP: http://{args.host}:{args.port}/web")

    web.run_app(create_app(), host=args.host, port=args.port, ssl_context=ssl_context)

if __name__ == "__main__":
    main()
