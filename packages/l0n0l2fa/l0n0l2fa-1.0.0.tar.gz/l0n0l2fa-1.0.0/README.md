# 1. 介绍
TOTP 2FA动态密码服务器

# 2. 安装
```bash
pip install l0n0l2fa
```

# 3. 配置文件介绍(tokens_otp.json)
```json
[
  {
    "token": "token", // 自定义, 唯一访问凭证
    "user": "动态密码", // 用户名
    "secrets": [
      {
        "name": "user1", // 密码的标签, 自定义
        "secret": "user1密码" // 密码, 由需要2fa的服务提供(github, pypi ...)
      },
      {
        "name": "user2", // 密码的标签, 自定义
        "secret": "user2密码" // 密码, 由需要2fa的服务提供(github, pypi ...)
      }
    ]
  }
]
```
# 4. 命令介绍
```bash
l0n0l2fa -h
usage: l0n0l2fa [-h] [--host HOST] [--port PORT] [--certfile CERTFILE] [--keyfile KEYFILE] [--tokens TOKENS]

OTP 管理服务

options:
  -h, --help           show this help message and exit
  --host HOST          监听地址 (默认: 127.0.0.1)
  --port PORT          监听端口 (默认: 8080)
  --certfile CERTFILE  SSL 证书文件路径 (可选)
  --keyfile KEYFILE    SSL 私钥文件路径 (可选)
  --tokens TOKENS      Token 配置文件路径 (默认: tokens_otp.json)
```

# 5. 实例
## 1. 编辑好配置文件到运行目录(比如 /path/l0n0l2fa/tokens_otp.json)
### 1.1 打开github (https://github.com)并登录账号

### 1.2 进入设置
![](https://gitee.com/l00n00l/l0n0l2fa/blob/master/imgs/1.png)

### 1.3 进入 `Password and Authentication`
![](https://gitee.com/l00n00l/l0n0l2fa/blob/master/imgs/2.png)

### 1.4 进入编辑
![](https://gitee.com/l00n00l/l0n0l2fa/blob/master/imgs/3.png)

### 1.5 获取`密码`
![](https://gitee.com/l00n00l/l0n0l2fa/blob/master/imgs/4.png)

## 2. 编辑配置文件(/path/tokens_otp.json)
```json
[
  {
    "token": "kjasldjflkasjdfiwieijwruowejrikasdjfkl",
    "user": "动态密码",
    "secrets": [
      {
        "name": "github",
        "secret": "AMIOEQ2C2QH4NEIT"
      }
    ]
  }
]
```
## 3. 启动服务器
```bash
l0n0l2fa --tokens /path/tokens_otp.json
有效用户配置已加载：
  user=动态密码 token=kjasldjflkasjdfiwieijwruowejrikasdjfkl secrets=1
🌐 启用 HTTP: http://127.0.0.1:8080/web
======== Running on http://127.0.0.1:8080 ========
(Press CTRL+C to quit)
```
## 4.访问  http://127.0.0.1:8080/web 并输入token
![](https://gitee.com/l00n00l/l0n0l2fa/blob/master/imgs/6.png)

## 5.复制动态密码
![](https://gitee.com/l00n00l/l0n0l2fa/blob/master/imgs/7.png)

## 6. 将动态密码填入github并保存
![](https://gitee.com/l00n00l/l0n0l2fa/blob/master/imgs/8.png)

