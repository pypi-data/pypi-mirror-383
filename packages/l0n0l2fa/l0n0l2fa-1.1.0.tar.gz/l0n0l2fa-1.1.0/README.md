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
# 5. 用例
1. [github配置方法(pypi需点击HomePage再访问)](docs/github.md)
