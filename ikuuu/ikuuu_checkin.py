#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =============================================================================
# ikuuu.win 青龙面板签到脚本
# =============================================================================
# Author: deer
# GitHub: https://github.com/deerwan
#
# Copyright (c) deer. All rights reserved.
#
# 转载要求：
#   任何形式的转载、分发、二次开发，都必须完整保留以下版权信息，
#   不得修改或删除本声明的任何内容，且必须明确标注原作者及原出处。
#
#   作者: deer
#   官方地址: https://github.com/deerwan
#   来源项目: ikuuu-checkin
#
# 免责声明：
#   本项目仅供学习交流使用，请勿用于商业用途。
#   使用者需自行遵守 ikuuu.win 的服务条款及相关法律法规。
# =============================================================================
#
# 环境变量: IKUUU_ACCOUNTS (格式: email1:password1,email2:password2)
# 支持多账号，每个账号独立签到

import os
import sys
import time
import random
import json
import requests
import httpx
from pathlib import Path

# ==================== 配置 ====================
LOGIN_URL = "https://ikuuu.win/auth/login"
CHECKIN_URL = "https://ikuuu.win/user/checkin"
CAPTCHA_ID = "cc96d05ba8b60f9112f76e18526fcb73"

# 从环境变量读取账号
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


# ==================== 极验 V4 验证码 ====================
def random_callback():
    """生成随机回调函数名"""
    return f"geetest_{int(random.random() * 10000) + int(time.time() * 1000)}"


def sleep_random(min_ms=500, max_ms=1500):
    """随机延迟"""
    time.sleep(random.randint(min_ms, max_ms) / 1000)


def solve_captcha():
    """
    解决极验 V4 验证码，返回验证结果
    """
    from uuid import uuid4
    
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    })
    
    try:
        for attempt in range(10):
            sleep_random(800, 1500)
            
            callback = random_callback()
            challenge = str(uuid4())
            
            resp = session.get(
                "https://gcaptcha4.geevisit.com/load",
                params={
                    "captcha_id": CAPTCHA_ID,
                    "challenge": challenge,
                    "client_type": "web",
                    "lang": "zh-cn",
                    "callback": callback,
                },
            )
            
            # 解析 JSONP 响应
            jsonp_data = resp.text.split(f"{callback}(", 1)[1].rstrip(")")
            data = json.loads(jsonp_data)["data"]
            
            lot_number = data["lot_number"]
            
            sleep_random(2000, 4000)
            
            pow_detail = data["pow_detail"]
            pt = data.get("pt", "1")
            
            # 导入 signer 模块
            from signer import Signer, lotParser
            
            base = {
                **Signer.generate_pow(
                    lot_number,
                    CAPTCHA_ID,
                    pow_detail["hashfunc"],
                    pow_detail["version"],
                    pow_detail["bits"],
                    pow_detail["datetime"],
                    "",
                ),
                **lotParser.get_dict(lot_number),
                "biht": "1426265548",
                "device_id": "",
                "em": {
                    "cp": 0,
                    "ek": "11",
                    "nt": 0,
                    "ph": 0,
                    "sc": 0,
                    "si": 0,
                    "wd": 1,
                },
                "gee_guard": {
                    "roe": {
                        "auh": "3",
                        "aup": "3",
                        "cdc": "3",
                        "egp": "3",
                        "res": "3",
                        "rew": "3",
                        "sep": "3",
                        "snh": "3",
                    }
                },
                "ep": "123",
                "geetest": "captcha",
                "lang": "zh",
                "lot_number": lot_number,
                "passtime": random.randint(3000, 5000),
            }
            
            w = Signer.encrypt_w(json.dumps(base), pt)
            
            callback = random_callback()
            resp = session.get(
                "https://gcaptcha4.geevisit.com/verify",
                params={
                    "callback": callback,
                    "captcha_id": CAPTCHA_ID,
                    "client_type": "web",
                    "lot_number": lot_number,
                    "payload": data["payload"],
                    "process_token": data["process_token"],
                    "payload_protocol": "1",
                    "pt": pt,
                    "w": w,
                },
            )
            
            result = json.loads(resp.text.split(f"{callback}(", 1)[1].rstrip(")"))
            
            if result.get("status") == "success":
                result_data = result.get("data", {})
                if "seccode" in result_data:
                    return result_data
        
        return None
    finally:
        session.close()


# ==================== 登录 ====================
def login(email, password):
    """
    登录 ikuuu.win
    返回 cookies 字典
    """
    print(f"🔐 [{email}] 正在登录...")
    
    captcha_result = solve_captcha()
    if not captcha_result:
        print(f"❌ [{email}] 验证码解决失败")
        return None
    
    seccode = captcha_result["seccode"]
    
    with httpx.Client(follow_redirects=True, timeout=60) as client:
        resp = client.post(
            LOGIN_URL,
            data={
                "host": "ikuuu.win",
                "email": email,
                "passwd": password,
                "code": "",
                "remember_me": "on",
                "pageLoadedAt": str(int(time.time() * 1000)),
                "captcha_result[lot_number]": captcha_result["lot_number"],
                "captcha_result[captcha_output]": seccode["captcha_output"],
                "captcha_result[pass_token]": seccode["pass_token"],
                "captcha_result[gen_time]": seccode["gen_time"],
            },
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "X-Requested-With": "XMLHttpRequest",
            },
        )
        
        result = resp.json()
        if result.get("ret") == 1:
            cookies = {}
            for k, v in resp.cookies.items():
                cookies[k] = v
            print(f"✅ [{email}] 登录成功")
            return cookies
        else:
            print(f"❌ [{email}] 登录失败: {result.get('msg', '未知错误')}")
            return None


# ==================== 签到 ====================
def checkin(cookies):
    """
    执行签到
    返回 (success, msg)
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36",
    }
    
    try:
        response = requests.post(
            CHECKIN_URL,
            headers=headers,
            cookies=cookies,
            timeout=30
        )
        result = response.json()
        ret = result.get("ret")
        msg = result.get("msg", "")
        
        if ret == 1:
            print(f"✅ 签到成功: {msg}")
            return True, msg
        else:
            print(f"⚠️  签到失败: {msg or '未知错误'}")
            return False, msg or "签到失败"
    except Exception as e:
        print(f"❌ 请求异常: {str(e)}")
        return False, str(e)


# ==================== 主流程 ====================
def main():
    print("=" * 50)
    print("🚀 ikuuu.win 青龙面板签到脚本")
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
        cookies = login(email, password)
        if not cookies:
            fail_count += 1
            continue
        
        # 签到（等待 2-3 秒避免限流）
        if i > 1:
            sleep_random(2000, 3000)
        
        success, msg = checkin(cookies)
        if success:
            success_count += 1
        else:
            fail_count += 1
    
    # 汇总
    print("\n" + "=" * 50)
    print(f"📊 签到完成: 成功 {success_count}/{total}, 失败 {fail_count}/{total}")
    print("=" * 50)
    
    # 青龙面板通知
    notify_text = f"ikuuu签到结果\n成功: {success_count}/{total}\n失败: {fail_count}/{total}"
    print(f"\n📢 {notify_text}")


if __name__ == "__main__":
    main()
