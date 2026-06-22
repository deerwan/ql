#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
脚本名称  : 花木仓(share.huamucang.top) 每日签到
功能说明  : 青龙面板自动签到，支持用户名密码登录 + Token 签到两种方式
插件作者  : Deer
更新时间  : 2026-06-22

环境变量  :
  HUAMUCANG_COOKIE  - 花木仓 Cookie（推荐，从浏览器复制完整 Cookie）
  HUAMUCANG_TOKEN   - 花木仓 Token（备选，优先级低于 COOKIE）
  HUAMUCANG_USERNAME - 花木仓用户名（当没有 Cookie/Token 时使用）
  HUAMUCANG_PASSWORD - 花木仓密码（当没有 Cookie/Token 时使用）

使用说明  :
  1. 推荐方式：登录花木仓网站，从浏览器开发者工具复制完整 Cookie 填入 HUAMUCANG_COOKIE
  2. 备选方式：填入用户名和密码，脚本会自动登录获取 Token 后签到
  3. 签到接口: POST https://share.huamucang.top/api/app/checkin/do/
  4. 统计接口: GET  https://share.huamucang.top/api/app/checkin/stats/

通知渠道  : 支持青龙面板内置通知（推送到微信、QQ、邮件等）
"""

import os
import re
import sys
import json
import time
import hmac
import hashlib
import logging
import requests
from datetime import datetime
from typing import Optional, Dict, Any

# ==================== 配置区域 ====================

# 花木仓基础地址
BASE_URL = "https://share.huamucang.top"

# 请求超时时间（秒）
REQUEST_TIMEOUT = 30

# 重试次数
MAX_RETRIES = 3

# 重试间隔（秒）
RETRY_INTERVAL = 3

# 日志级别（调试时改为 DEBUG）
LOG_LEVEL = logging.INFO

# ==================== 日志配置 ====================

logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


# ==================== 青龙面板通知 ====================

def send_qinglong_notification(text: str, summary: str = "花木仓签到") -> None:
    """
    发送青龙面板通知
    
    Args:
        text: 通知详细内容
        summary: 通知摘要
    """
    try:
        qlog_path = os.environ.get("QL_DIR", "")
        if not qlog_path:
            ql_dir = os.path.expanduser("~/.ql")
            if os.path.exists(ql_dir):
                qlog_path = ql_dir
            else:
                return
        
        log_file = os.path.join(qlog_path, "log", "sendNotify.js")
        if os.path.exists(log_file):
            script_dir = os.path.dirname(os.path.abspath(__file__))
            env = os.environ.copy()
            env["QL_LOG"] = text
            env["QL_SUBJECT"] = summary
            os.system(
                f'cd "{os.path.dirname(log_file)}" && node sendNotify.js "{summary}" "{text}"'
            )
    except Exception as e:
        logger.debug(f"青龙通知发送失败: {e}")


def send_notification(text: str, summary: str = "花木仓签到") -> None:
    """
    发送通知（优先使用青龙面板通知，降级到服务器端通知）
    
    Args:
        text: 通知详细内容
        summary: 通知摘要
    """
    # 尝试青龙面板通知
    send_qinglong_notification(text, summary)
    
    # 尝试服务器端 push 通知
    push_key = os.environ.get("PUSH_KEY", "")
    if push_key and push_key != "":
        try:
            requests.post(
                f"https://sctapi.ftqq.com/{push_key}.send",
                data={"title": summary, "content": text},
                timeout=REQUEST_TIMEOUT,
            )
        except Exception as e:
            logger.debug(f"Server 酱推送失败: {e}")
    
    # 打印到日志
    logger.info(f"[{summary}] {text}")


# ==================== Cookie/Token 管理 ====================

class HuamucangSession:
    """花木仓会话管理器"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/125.0.0.0 Safari/537.36"
            ),
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Referer": f"{BASE_URL}/",
            "Origin": BASE_URL,
        })
        self.csrf_token = ""
        self.user_token = ""
        self.is_authenticated = False
    
    def set_cookie(self, cookie_str: str) -> bool:
        """
        设置 Cookie
        
        Args:
            cookie_str: 完整 Cookie 字符串
            
        Returns:
            bool: 是否成功设置
        """
        try:
            # 解析 Cookie 字符串为字典
            cookies = {}
            for item in cookie_str.split(";"):
                item = item.strip()
                if "=" in item:
                    key, value = item.split("=", 1)
                    cookies[key.strip()] = value.strip()
            
            # 提取 CSRF Token
            self.csrf_token = cookies.get("csrftoken", "")
            
            # 提取用户 Token（如果存在）
            user_token = cookies.get("app_user_token", "")
            if user_token:
                self.user_token = user_token
                self.session.headers["X-App-User-Token"] = user_token
            
            # 设置 Session Cookie
            for key, value in cookies.items():
                self.session.cookies.set(key, value)
            
            self.is_authenticated = True
            logger.debug("Cookie 设置成功")
            return True
        except Exception as e:
            logger.error(f"Cookie 设置失败: {e}")
            return False
    
    def set_token(self, token: str) -> bool:
        """
        直接设置 Token
        
        Args:
            token: 用户 Token
            
        Returns:
            bool: 是否成功设置
        """
        try:
            self.user_token = token
            self.session.headers["X-App-User-Token"] = token
            self.is_authenticated = True
            logger.debug("Token 设置成功")
            return True
        except Exception as e:
            logger.error(f"Token 设置失败: {e}")
            return False
    
    def set_credentials(self, username: str, password: str) -> bool:
        """
        使用用户名密码登录
        
        Args:
            username: 用户名
            password: 密码
            
        Returns:
            bool: 是否登录成功
        """
        if not username or not password:
            logger.error("用户名或密码为空")
            return False
        
        # 登录（不需要预先获取 CSRF，Django 会自动处理）
        login_data = {
            "username": username,
            "password": password,
        }
        
        try:
            # 先访问首页获取 CSRF Cookie
            self.session.get(
                BASE_URL,
                timeout=REQUEST_TIMEOUT,
            )
            
            # 获取 CSRF Token
            csrf_response = self.session.get(
                f"{BASE_URL}/api/csrf/",
                timeout=REQUEST_TIMEOUT,
            )
            csrf_token = ""
            if csrf_response.status_code == 200:
                csrf_cookie = self.session.cookies.get("csrftoken", "")
                if csrf_cookie:
                    csrf_token = csrf_cookie
                    self.session.headers["X-CSRFToken"] = csrf_token
            
            # 登录
            response = self.session.post(
                f"{BASE_URL}/api/app/login/",
                json=login_data,
                timeout=REQUEST_TIMEOUT,
            )
            
            response.raise_for_status()
            result = response.json()
            
            # 提取 Token（响应结构可能是 {"token": "..."} 或 {"data": {"token": "..."}}）
            token = ""
            if isinstance(result, dict):
                token = result.get("token", "")
                if not token:
                    data = result.get("data", {})
                    if isinstance(data, dict):
                        token = data.get("token", "")
            
            if token:
                self.set_token(token)
                # 同步 Cookie
                self.session.cookies.set("app_user_token", token, domain="share.huamucang.top", path="/")
                logger.info("登录成功")
                return True
            else:
                logger.error(f"登录响应中未找到 Token: {result}")
                return False
                
        except requests.exceptions.HTTPError as e:
            if e.response is not None:
                error_msg = e.response.text
                logger.error(f"登录失败 (HTTP {e.response.status_code}): {error_msg}")
            else:
                logger.error(f"登录失败: {e}")
            return False
        except Exception as e:
            logger.error(f"登录异常: {e}")
            return False
    
    def request_with_retry(
        self,
        method: str,
        url: str,
        **kwargs
    ) -> Optional[requests.Response]:
        """
        带重试的请求方法
        
        Args:
            method: 请求方法 (GET/POST/PUT/DELETE)
            url: 请求 URL
            **kwargs: 其他请求参数
            
        Returns:
            requests.Response 或 None
        """
        kwargs.setdefault("timeout", REQUEST_TIMEOUT)
        
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                response = self.session.request(method, url, **kwargs)
                
                # 401 表示 Token 过期
                if response.status_code == 401:
                    logger.warning("Token 已过期，需要重新登录")
                    return None
                
                # 400 错误不要立即抛异常，记录下来方便调试
                if response.status_code == 400:
                    logger.error(f"HTTP 400 错误 (尝试 {attempt}/{MAX_RETRIES}): {response.text[:500]}")
                
                response.raise_for_status()
                return response
                
            except requests.exceptions.Timeout:
                logger.warning(f"请求超时 (尝试 {attempt}/{MAX_RETRIES})")
            except requests.exceptions.HTTPError as e:
                if e.response is not None:
                    logger.error(f"HTTP 错误详情 (尝试 {attempt}/{MAX_RETRIES}): 状态码={e.response.status_code}, 响应={e.response.text[:500]}")
                logger.warning(f"HTTP 错误 (尝试 {attempt}/{MAX_RETRIES}): {e}")
            except Exception as e:
                logger.warning(f"请求异常 (尝试 {attempt}/{MAX_RETRIES}): {e}")
            
            if attempt < MAX_RETRIES:
                logger.info(f"等待 {RETRY_INTERVAL} 秒后重试...")
                time.sleep(RETRY_INTERVAL)
        
        logger.error(f"请求失败，已达到最大重试次数 {MAX_RETRIES}")
        return None
    
    def get(self, path: str, **kwargs) -> Optional[requests.Response]:
        """GET 请求"""
        url = f"{BASE_URL}{path}"
        return self.request_with_retry("GET", url, **kwargs)
    
    def post(self, path: str, skip_400: bool = False, **kwargs) -> Optional[requests.Response]:
        """POST 请求
        
        Args:
            path: 请求路径
            skip_400: 是否跳过 400 错误的 raise_for_status（用于签到接口）
            **kwargs: 其他参数
        """
        url = f"{BASE_URL}{path}"
        # 确保 POST 请求包含 CSRF Token
        if "headers" not in kwargs:
            kwargs["headers"] = {}
        if self.csrf_token:
            kwargs["headers"]["X-CSRFToken"] = self.csrf_token
        kwargs["headers"]["X-Requested-With"] = "XMLHttpRequest"
        
        # 执行请求（不使用 retry，因为签到接口 400 是正常状态）
        kwargs.setdefault("timeout", REQUEST_TIMEOUT)
        try:
            response = self.session.request("POST", url, **kwargs)
            
            if response.status_code == 401:
                logger.warning("Token 已过期，需要重新登录")
                return None
            
            # 对于签到接口，400 可能是"已签到"的正常响应，不抛异常
            if skip_400 and response.status_code == 400:
                logger.debug(f"签到接口返回 400（可能是已签到）: {response.text[:200]}")
                return response
            
            response.raise_for_status()
            return response
            
        except requests.exceptions.HTTPError as e:
            if e.response is not None:
                logger.error(f"HTTP 错误详情: 状态码={e.response.status_code}, 响应={e.response.text[:500]}")
            return None
        except Exception as e:
            logger.error(f"请求异常: {e}")
            return None


# ==================== 签到逻辑 ====================

def checkin(session: HuamucangSession) -> Dict[str, Any]:
    """
    执行签到操作
    
    Args:
        session: 会话对象
        
    Returns:
        dict: 签到结果
    """
    result = {
        "success": False,
        "message": "",
        "data": None,
    }
    
    try:
        # 执行签到（skip_400=True 因为已签到也会返回 400）
        response = session.post("/api/app/checkin/do/", skip_400=True)
        
        if response is None:
            result["message"] = "签到请求失败，Token 可能已过期"
            return result
        
        data = response.json()
        result["data"] = data
        
        # 解析响应
        message = data.get("message", data.get("detail", ""))
        
        # 检查是否已签到
        if "已经签到" in message or "已签到" in message or "already" in message.lower():
            result["success"] = True
            result["message"] = f"今日已签到: {message}"
            return result
        
        # 检查签到成功
        if data.get("status") == "success" or response.status_code == 200:
            reward = data.get("data", {})
            points = reward.get("points", reward.get("reward_points", ""))
            result["success"] = True
            result["message"] = f"签到成功: {message}"
            if points:
                result["message"] += f" (获得 {points} 积分)"
            return result
        
        # 其他情况视为失败
        result["message"] = f"签到失败: {message or data}"
        return result
        
    except json.JSONDecodeError as e:
        result["message"] = f"解析签到响应失败: {e}"
        logger.error(result["message"])
    except Exception as e:
        result["message"] = f"签到异常: {e}"
        logger.error(result["message"])
    
    return result


def get_stats(session: HuamucangSession) -> Dict[str, Any]:
    """
    获取签到统计信息
    
    Args:
        session: 会话对象
        
    Returns:
        dict: 统计信息
    """
    stats = {
        "success": False,
        "message": "",
        "data": None,
    }
    
    try:
        response = session.get("/api/app/checkin/stats/")
        
        if response is None:
            stats["message"] = "获取统计信息失败，Token 可能已过期"
            return stats
        
        data = response.json()
        stats["data"] = data
        
        if data.get("status") == "success" or response.status_code == 200:
            stats["success"] = True
            stats["message"] = "获取统计信息成功"
            return stats
        
        stats["message"] = f"获取统计信息失败: {data.get('message', '')}"
        return stats
        
    except Exception as e:
        stats["message"] = f"获取统计信息异常: {e}"
        logger.error(stats["message"])
    
    return stats


# ==================== 主流程 ====================

def get_env_value(key: str, default: str = "") -> str:
    """
    获取环境变量值
    
    Args:
        key: 环境变量名
        default: 默认值
        
    Returns:
        str: 环境变量值
    """
    return os.environ.get(key, default).strip()


def main() -> int:
    """
    主函数
    
    Returns:
        int: 0 表示成功，非 0 表示失败
    """
    print("=" * 60)
    print("花木仓(share.huamucang.top) 每日签到脚本")
    print(f"运行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 获取配置
    cookie = get_env_value("HUAMUCANG_COOKIE")
    token = get_env_value("HUAMUCANG_TOKEN")
    username = get_env_value("HUAMUCANG_USERNAME")
    password = get_env_value("HUAMUCANG_PASSWORD")
    
    # 创建会话
    session = HuamucangSession()
    
    # 认证方式选择
    authenticated = False
    
    if cookie:
        logger.info("使用 Cookie 方式进行认证")
        authenticated = session.set_cookie(cookie)
    elif token:
        logger.info("使用 Token 方式进行认证")
        authenticated = session.set_token(token)
    elif username and password:
        logger.info("使用用户名密码方式进行认证")
        authenticated = session.set_credentials(username, password)
    else:
        logger.error("未配置任何认证信息！")
        logger.error("请设置以下环境变量之一：")
        logger.error("  1. HUAMUCANG_COOKIE - 完整 Cookie（推荐）")
        logger.error("  2. HUAMUCANG_TOKEN  - 用户 Token")
        logger.error("  3. HUAMUCANG_USERNAME + HUAMUCANG_PASSWORD - 用户名密码")
        notification_text = (
            "❌ 花木仓签到失败\n"
            "原因：未配置认证信息\n"
            "请设置 HUAMUCANG_COOKIE 或 HUAMUCANG_TOKEN 环境变量"
        )
        send_notification(notification_text, "花木仓签到")
        return 1
    
    if not authenticated:
        logger.error("认证失败，请检查配置的凭证是否正确")
        notification_text = (
            "❌ 花木仓签到失败\n"
            "原因：认证失败\n"
            "请检查 Cookie/Token/用户名密码是否正确"
        )
        send_notification(notification_text, "花木仓签到")
        return 1
    
    logger.info("认证成功，开始签到...")
    
    # 执行签到
    checkin_result = checkin(session)
    
    # 构建通知文本
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if checkin_result["success"]:
        logger.info(f"签到结果: {checkin_result['message']}")
        
        # 获取统计信息
        stats_result = get_stats(session)
        stats_text = ""
        if stats_result["success"] and stats_result["data"]:
            data = stats_result["data"].get("data", stats_result["data"])
            stats_text = f"\n\n📊 签到统计:\n"
            stats_text += f"  今日签到: {data.get('today', '未知')}\n"
            stats_text += f"  今日状态: {'已完成' if data.get('checked_today') else '未完成'}\n"
            stats_text += f"  今日奖励: {data.get('reward_points', 0)} 积分\n"
            stats_text += f"  累计签到: {data.get('my_total_days', 0)} 天\n"
            stats_text += f"  今日签到人数: {data.get('today_checkin_count', 0)}\n"
        
        notification_text = (
            f"✅ 花木仓签到成功\n"
            f"时间: {now}\n"
            f"结果: {checkin_result['message']}\n"
            f"{stats_text}"
        )
        send_notification(notification_text, "花木仓签到")
        return 0
    else:
        logger.error(f"签到失败: {checkin_result['message']}")
        
        # 判断是否需要重新登录
        if "过期" in checkin_result["message"] or "401" in checkin_result["message"]:
            notification_text = (
                f"❌ 花木仓签到失败\n"
                f"时间: {now}\n"
                f"原因: 登录凭证已过期，请更新 Cookie 或 Token\n"
                f"详情: {checkin_result['message']}"
            )
        else:
            notification_text = (
                f"❌ 花木仓签到失败\n"
                f"时间: {now}\n"
                f"原因: {checkin_result['message']}"
            )
        
        send_notification(notification_text, "花木仓签到")
        return 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        logger.info("\n脚本被用户中断")
        sys.exit(1)
    except Exception as e:
        logger.error(f"脚本运行异常: {e}", exc_info=True)
        notification_text = (
            f"❌ 花木仓签到脚本异常\n"
            f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"异常: {str(e)}"
        )
        send_notification(notification_text, "花木仓签到")
        sys.exit(1)
