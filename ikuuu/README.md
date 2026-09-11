# ikuuu 青龙面板签到脚本

自动登录 ikuuu.top 并完成每日签到，支持多账号。

## 文件
- `ikuuu_checkin.py` — 主脚本（Playwright 浏览器过极验验证码 + 签到）
- `requirements.txt` — 依赖
- `.env.example` — 环境变量模板

> 极验(GeeTest V4)验证码用 **Playwright 无头浏览器真实点击「点我开始验证」** 通过（旧版伪造 token 会被服务端拒绝）。

## 部署

1. 上传 `ikuuu_checkin.py`、`requirements.txt` 到青龙 `ikuuu` 目录。
2. 安装依赖（容器内执行）：
   ```bash
   cd /ql/data/scripts/ikuuu/
   pip3 install -r requirements.txt
   playwright install chromium
   playwright install-deps        # 安装系统库，缺则加
   ```
3. 配置环境变量 `IKUUU_ACCOUNTS`：`邮箱:密码`，多账号逗号分隔。
4. 配置定时任务。

## 环境变量
| 变量 | 说明 |
|---|---|
| `IKUUU_ACCOUNTS` | `email1:pass1,email2:pass2`（必填） |
| `IKUUU_DOMAIN` | 域名，默认 `ikuuu.top`（可选，脚本自动尝试备用域名） |
| `IKUUU_BROWSER` | `chrome`/`msedge` 指定系统浏览器（可选，默认用 Playwright chromium） |

## 常见问题
- **浏览器启动失败 / 缺系统库**：执行 `playwright install-deps`（或 `playwright install --with-deps chromium`）。
- **No module named 'playwright'**：未装内核，执行 `playwright install chromium`。
- **过验证码超时 / 登录未进用户中心**：确认容器可访问 `gcaptcha4.geevisit.com`；如长期不稳可改用 `Backup/` 旧版 Cookie 直签。
- **登录失败**：检查邮箱密码是否正确、账号是否被封。
