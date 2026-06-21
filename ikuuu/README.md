# ikuuu 青龙面板签到脚本

自动登录 ikuuu.win 并完成每日签到，支持多账号批量运行。

## 文件说明

```
ikuuu/
├── ikuuu_checkin.py    # 主脚本（登录 + 签到）
├── signer.py           # 极验 V4 验证码加密模块
├── requirements.txt    # Python 依赖列表
└── .env.example        # 环境变量配置模板
```

## 部署步骤

### 1. 上传文件到青龙面板

在青龙面板 → **文件管理** 中新建文件夹 `ikuuu`，上传以下 3 个文件：

- `ikuuu_checkin.py`
- `signer.py`
- `requirements.txt`

### 2. 安装依赖

打开青龙面板 → **终端**，执行：

```bash
cd /ql/data/scripts/ikuuu/
pip3 install -r requirements.txt
```

或使用青龙面板的 **依赖管理**，新建依赖时命令类型选择 **pip3**，分别添加：

- `requests`
- `httpx`
- `pycryptodome`
- `curl_cffi`

验证安装是否成功：

```bash
python3 -c "import requests; print('ok')"
```

输出 `ok` 即表示成功。

### 3. 配置账号

在青龙面板 → **配置文件** 中添加环境变量：

**变量名：** `IKUUU_ACCOUNTS`

**变量值：** 邮箱:密码

### 4. 添加定时任务

青龙面板 → **定时任务** → **添加任务**：

| 项 | 值 |
|---|---|
| 名称 | ikuuu签到 |
| 命令 | `python3 /ql/data/scripts/ikuuu/ikuuu_checkin.py` |
| 定时规则 | `0 8 * * *`（每天 8:00） |
| 时区 | Asia/Shanghai |

### 5. 手动测试

在终端中运行：

```bash
python3 /ql/data/scripts/ikuuu/ikuuu_checkin.py
```

观察输出是否有登录成功和签到成功的提示。

## 多账号配置

支持批量配置多个 ikuuu 账号，用逗号分隔：

```
IKUUU_ACCOUNTS=email1@example.com:password1,email2@example.com:password2,email3@example.com:password3
```

### 注意事项

- 每个账号之间会自动间隔 2~3 秒，防止被限流
- 所有账号共用同一个环境变量，无需额外配置
- 脚本会依次处理每个账号，最后输出汇总结果
- 建议每个账号的邮箱和密码用冒号 `:` 分隔

### 示例

单账号：
```
IKUUU_ACCOUNTS=user@gmail.com:mypassword
```

多账号：
```
IKUUU_ACCOUNTS=user1@gmail.com:pass1,user2@qq.com:pass2,user3@yahoo.com:pass3
```

## 输出示例

```
==================================================
🚀 ikuuu.win 青龙面板签到脚本
==================================================

📋 [1/2] 处理账号: user1@gmail.com
🔐 [user1@gmail.com] 正在登录...
✅ [user1@gmail.com] 登录成功
✅ 签到成功: 签到成功

📋 [2/2] 处理账号: user2@qq.com
🔐 [user2@qq.com] 正在登录...
✅ [user2@qq.com] 登录成功
✅ 签到成功: 签到成功

==================================================
📊 签到完成: 成功 2/2, 失败 0/2
==================================================
```

## 常见问题

**Q: 提示 No module named 'requests'**

A: 依赖未安装成功，重新在终端执行 `pip3 install -r requirements.txt`

**Q: 验证码解决失败**

A: 网络问题，检查服务器是否能访问 `gcaptcha4.geevisit.com`

**Q: 登录失败**

A: 检查邮箱和密码是否正确，确认账号没有被封禁
