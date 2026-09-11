#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =============================================================================
# ikuuu.win 青龙面板签到脚本
# =============================================================================

import os
import sys
import time
import random
import json
import requests
from urllib.parse import urlparse, unquote

# ==================== 配置 ====================
# 可用域名列表（按优先级排序）
DOMAINS = [
    "ikuuu.top",      # 主要域名
    "ikuuu.pw",       # 备用域名 1
    "ikuuu.org",      # 备用域名 2
    "ikuuu.me",       # 备用域名 3
]

# 环境变量获取域名，优先使用环境变量
BASE_DOMAIN = os.getenv("IKUUU_DOMAIN", "").strip()
if not BASE_DOMAIN:
    BASE_DOMAIN = DOMAINS[0]  # 默认使用第一个域名

BASE_URL = f"https://{BASE_DOMAIN}"
LOGIN_URL = f"{BASE_URL}/auth/login"
CHECKIN_URL = f"{BASE_URL}/user/checkin"

# 浏览器登录最大重试次数
LOGIN_MAX_RETRIES = 3


def load_accounts():
    """从环境变量加载账号信息"""
    accounts_env = os.getenv("IKUUU_ACCOUNTS", "")
    if not accounts_env:
        print("❌ 未找到 IKUUU_ACCOUNTS 环境变量")
        print("📝 格式: email1:password1,email2:password2")
        sys.exit(1)

    accounts = []
    for account_str in accounts_env.split(","):
        if ":" not in account_str:
            continue
        email, password = account_str.split(":", 1)
        accounts.append({
            "email": email.strip(),
            "password": password.strip()
        })

    if not accounts:
        print("❌ 没有有效的账号配置")
        sys.exit(1)

    return accounts


def sleep_random(min_ms=500, max_ms=1500):
    """随机延迟"""
    time.sleep(random.randint(min_ms, max_ms) / 1000)


# ==================== Playwright 浏览器登录 ====================
def _import_playwright():
    """延迟导入 Playwright"""
    try:
        from playwright.sync_api import sync_playwright
        return sync_playwright
    except ImportError as e:
        raise ImportError(
            "未安装 playwright。请执行: pip install playwright && playwright install chromium"
        ) from e


def _launch_browser(playwright):
    """启动浏览器"""
    launch_args = [
        "--disable-blink-features=AutomationControlled",
        "--no-sandbox",
        "--disable-dev-shm-usage",
    ]
    browser = playwright.chromium.launch(headless=True, args=launch_args)
    print("🔍 浏览器启动成功")
    return browser


def _cookie_header_from_context(context, base_url):
    """从浏览器上下文提取 Cookie"""
    host = urlparse(base_url).hostname or ""
    cookies = context.cookies()
    parts = []
    seen = set()
    for c in cookies:
        name = c.get("name")
        if not name:
            continue
        domain = (c.get("domain") or "").lstrip(".")
        if host and domain and host != domain and not host.endswith("." + domain) and not domain.endswith(host):
            if "ikuuu" not in domain and "ikuuu" not in host:
                continue
        if name in seen:
            continue
        value = unquote(c.get('value', ''))
        parts.append(f"{name}={value}")
        seen.add(name)
    return "; ".join(parts)


def _wait_and_pass_geetest(page, timeout_sec=45):
    """等待 Geetest 验证"""
    deadline = time.time() + timeout_sec
    clicked = False
    check_count = 0

    while time.time() < deadline:
        check_count += 1
        
        try:
            state = page.evaluate(
                """() => {
                    const ready = !!(window.Captcha && window.Captcha.isReady && window.Captcha.isReady());
                    const loaded = !!(window.Captcha && window.Captcha.isLoaded && window.Captcha.isLoaded());
                    const err = (window.Captcha && window.Captcha.getError) ? window.Captcha.getError() : null;
                    return {ready, loaded, err};
                }"""
            )
        except Exception:
            state = {"ready": False, "loaded": False, "err": None}

        if state.get("ready"):
            print(f"✅ Geetest 验证已通过 (尝试 {check_count} 次)")
            return True

        if state.get("err"):
            print(f"⚠️  Geetest 错误: {state['err']}")

        if state.get("loaded"):
            print(f"🔍 Geetest 已加载 (尝试 {check_count} 次)")

        if not clicked:
            selectors = [
                ".geetest_radar_btn",
                ".geetest_btn_click",
                ".geetest_btn",
                "text=点我开始验证",
            ]
            for sel in selectors:
                try:
                    loc = page.locator(sel).first
                    if loc.count() > 0 and loc.is_visible():
                        loc.click(timeout=2000)
                        clicked = True
                        print(f"🔍 已点击 Geetest 控件: {sel}")
                        page.wait_for_timeout(1500)
                        break
                except:
                    continue

        page.wait_for_timeout(500)

    print(f"❌ 等待 Geetest 通过超时")
    return False


def login_with_browser(email, password, base_url):
    """用浏览器完成登录"""
    if not email or not password:
        print("❌ 缺少邮箱或密码")
        return None

    sync_playwright = _import_playwright()
    browser = None
    
    try:
        with sync_playwright() as p:
            browser = _launch_browser(p)
            context = browser.new_context(
                locale="zh-CN",
                viewport={"width": 1280, "height": 800},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
            )
            context.add_init_script(
                "Object.defineProperty(navigator, 'webdriver', {get: () => undefined});"
            )
            page = context.new_page()
            
            login_url = f"{base_url}/auth/login"
            print(f"🔍 访问登录页: {login_url}")
            page.goto(login_url, wait_until="networkidle", timeout=60000)
            page.wait_for_timeout(2000)
            
            # 填写邮箱密码
            page.wait_for_selector("#email, input[name='email']", state="visible", timeout=15000)
            page.fill("#email, input[name='email']", email)
            page.fill("#password, input[name='passwd']", password)
            page.wait_for_timeout(1000)
            
            # 处理验证码
            if not _wait_and_pass_geetest(page, timeout_sec=45):
                print("⚠️  Geetest 验证超时，尝试直接登录...")
                page.wait_for_timeout(500)
            
            # 点击登录
            page.click("button.login, button[type='submit']", timeout=2000)
            page.wait_for_timeout(3000)
            
            final_url = page.url
            if "/user" not in final_url:
                print(f"❌ 登录失败，URL: {final_url}")
                browser.close()
                return None
            
            cookie = _cookie_header_from_context(context, base_url)
            browser.close()
            print(f"✅ 浏览器登录成功")
            return cookie
            
    except Exception as e:
        print(f"❌ 浏览器登录失败: {e}")
        if browser:
            try:
                browser.close()
            except:
                pass
        return None





def checkin(cookie):
    """执行签到"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": f"{BASE_URL}/user",
        "X-Requested-With": "XMLHttpRequest",
    }
    
    try:
        # 解析 cookie
        cookie_dict = {}
        for item in cookie.split(';'):
            item = item.strip()
            if '=' in item:
                k, v = item.split('=', 1)
                cookie_dict[k.strip()] = v.strip()
        
        response = requests.post(
            CHECKIN_URL,
            headers=headers,
            cookies=cookie_dict,
            timeout=30
        )
        
        print(f"🔍 签到响应状态: {response.status_code}")
        print(f"🔍 签到响应内容: {response.text[:200]}")
        
        # 检查是否是 JSON
        if not response.text.strip().startswith('{'):
            # 尝试继续尝试其他域名
            print("⚠️  签到返回非 JSON，尝试切换域名...")
            return False, "切换域名重试"
        
        result = response.json()
        ret = result.get("ret")
        msg = result.get("msg", "")
        
        if ret == 1:
            print(f"✅ 签到成功: {msg}")
            return True, msg
        elif "已经签到" in msg or "今日已签到" in msg:
            print(f"✅ 今日已签到: {msg}")
            return True, msg
        else:
            print(f"⚠️  签到失败: {msg or '未知错误'}")
            return False, msg or "签到失败"
            
    except Exception as e:
        print(f"❌ 签到请求异常: {str(e)}")
        return False, str(e)


def login_with_retry(email, password):
    """登录并重试域名（直接使用浏览器登录）"""
    print(f"🔐 [{email}] 正在登录...")
    
    # 尝试多个域名
    for i, domain in enumerate(DOMAINS):
        if i > 0:
            print(f"🔄 尝试备用域名: {domain}")
            global BASE_URL, LOGIN_URL, CHECKIN_URL
            BASE_URL = f"https://{domain}"
            LOGIN_URL = f"{BASE_URL}/auth/login"
            CHECKIN_URL = f"{BASE_URL}/user/checkin"
        
        # 直接使用浏览器登录（更可靠，支持 Geetest 验证码）
        cookie = login_with_browser(email, password, BASE_URL)
        if cookie:
            return cookie
    
    print(f"❌ [{email}] 登录失败（已尝试所有域名）")
    return None


def main():
    print("=" * 50)
    print("🚀 ikuuu 青龙面板签到脚本")
    print("=" * 50)

    accounts = load_accounts()
    total = len(accounts)
    success_count = 0
    fail_count = 0

    for i, account in enumerate(accounts, 1):
        email = account["email"]
        password = account["password"]

        print(f"\n📋 [{i}/{total}] 处理账号: {email}")

        # 登录
        cookie = login_with_retry(email, password)
        if not cookie:
            fail_count += 1
            continue

        # 签到
        if i > 1:
            sleep_random(2000, 3000)

        success, msg = checkin(cookie)
        if success:
            success_count += 1
        else:
            fail_count += 1

    # 汇总
    print("\n" + "=" * 50)
    print(f"📊 签到完成: 成功 {success_count}/{total}, 失败 {fail_count}/{total}")
    print("=" * 50)
    print(f"\n📢 ikuuu签到结果\n成功: {success_count}/{total}\n失败: {fail_count}/{total}")


if __name__ == "__main__":
    main()
