#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# cron: 1 7-20 * * *
# const $ = new Env("微软积分");
"""
🎯 Bing Rewards 自动化脚本 - 多账号分离版-v2.1

变量名：
bing_ck_1、bing_ck_2、bing_ck_3、bing_ck_4... （必需）
bing_token_1、bing_token_2、bing_token_3、bing_token_4... （可选，用于阅读任务）

下面url抓取CK，必须抓取到 tifacfaatcs 和认证字段，否则cookie无效
1. 登录 https://cn.bing.com/
2. 点右侧的【查看仪表板】,会跳转到 https://rewards.bing.com/?ref=rewardspanel  
3. 确认两个地址登录的是同一个账号，抓CK

Cookie验证规则：
- tifacfaatcs: 影响账号信息获取（必需）
- 认证字段: 影响搜索任务是否加分（必须包含 .MSA.Auth）
- 以上字段缺失会导致cookie无效

🔑 阅读任务需要配置刷新令牌：
1. 安装"Bing Rewards 自动获取刷新令牌"油猴脚本
2. 访问 https://login.live.com/oauth20_authorize.srf?client_id=0000000040170455&scope=service::prod.rewardsplatform.microsoft.com::MBI_SSL&response_type=code&redirect_uri=https://login.live.com/oauth20_desktop.srf
3. 登录后，使用"Bing Rewards 自动获取刷新令牌"油猴脚本，自动获取刷新令牌
4. 设置环境变量 bing_token_1、bing_token_2、bing_token_3...

From:yaohuo28507

"""

import requests
import random
import re
import time
import json
import os
from datetime import datetime, date
from urllib.parse import urlparse, parse_qs, quote
import threading
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from functools import wraps
import traceback

# ==================== Bark 推送配置 ====================
# 添加自定义参数，也可以留空
CUSTOM_BARK_ICON = "https://gitee.com/hlt1995/BARK_ICON/raw/main/MicrosoftRewards.png"   # 自定义图标
CUSTOM_BARK_GROUP = "Microsoft Rewards"              # 自定义分组
# =======================================================

BARK_PUSH = os.getenv("BARK_PUSH")
BARK_ICON = CUSTOM_BARK_ICON or os.getenv("BARK_ICON", "")
BARK_GROUP = CUSTOM_BARK_GROUP or os.getenv("BARK_GROUP", "")

os.environ["BARK_ICON"] = BARK_ICON
os.environ["BARK_GROUP"] = BARK_GROUP

delay = random.randint(0, 1800)
print(f"⏳ 任务随机延迟 {delay} 秒后开始执行...")
time.sleep(delay)

# ==================== 用户配置区域 ====================
# 在这里修改您的配置参数
# 
# 📝 配置说明：
# 1. 推送配置：设置Telegram和企业微信推送参数
# 2. 任务执行配置：调整搜索延迟、重试次数等执行参数
# 3. 缓存配置：设置缓存文件相关参数
# 
# 💡 修改建议：
# - 搜索延迟建议保持在25-35秒之间，避免过于频繁
# - 任务延迟建议保持在2-4秒之间，给系统响应时间
# - 重试次数建议不超过5次，避免过度重试
# - 请求超时建议15-30秒，根据网络情况调整
# - 重复运行次数建议3-5次，避免过度重复执行


# 任务执行配置
TASK_CONFIG = {
    'SEARCH_CHECK_INTERVAL': 5,      # 搜索检查间隔次数
    'SEARCH_DELAY_MIN': 60,          # 搜索延迟最小值（秒）
    'SEARCH_DELAY_MAX': 80,          # 搜索延迟最大值（秒）
    'TASK_DELAY_MIN': 2,             # 任务延迟最小值（秒）
    'TASK_DELAY_MAX': 4,             # 任务延迟最大值（秒）
    'MAX_RETRIES': 3,                # 最大重试次数
    'RETRY_DELAY': 2,                # 重试延迟（秒）
    'REQUEST_TIMEOUT': 15,           # 请求超时时间（秒）
    'HOT_WORDS_MAX_COUNT': 30,       # 热搜词最大数量
    'MAX_REPEAT_COUNT': 2,           # 最大重复运行次数
}

# 缓存配置
CACHE_CONFIG = {
    'CACHE_FILE': "bing_cache.json",  # 缓存文件名
    'CACHE_ENABLED': True,            # 是否启用缓存
}

# 使用缓存配置
CACHE_ENABLED = CACHE_CONFIG['CACHE_ENABLED']



# ==================== 配置管理 ====================
@dataclass
class Config:
    """配置类，统一管理所有配置项"""
    # 搜索配置
    SEARCH_CHECK_INTERVAL: int = TASK_CONFIG['SEARCH_CHECK_INTERVAL']
    SEARCH_DELAY_MIN: int = TASK_CONFIG['SEARCH_DELAY_MIN']
    SEARCH_DELAY_MAX: int = TASK_CONFIG['SEARCH_DELAY_MAX']
    TASK_DELAY_MIN: int = TASK_CONFIG['TASK_DELAY_MIN']
    TASK_DELAY_MAX: int = TASK_CONFIG['TASK_DELAY_MAX']
    
    # 重试配置
    MAX_RETRIES: int = TASK_CONFIG['MAX_RETRIES']
    RETRY_DELAY: int = TASK_CONFIG['RETRY_DELAY']
    
    # 文件配置
    CACHE_FILE: str = CACHE_CONFIG['CACHE_FILE']
    
    # API配置
    REQUEST_TIMEOUT: int = TASK_CONFIG['REQUEST_TIMEOUT']
    HOT_WORDS_MAX_COUNT: int = TASK_CONFIG['HOT_WORDS_MAX_COUNT']
    
    # User-Agent池配置
    PC_USER_AGENTS: List[str] = None
    MOBILE_USER_AGENTS: List[str] = None
    
    # 热搜API配置
    HOT_WORDS_APIS: List[Tuple[str, List[str]]] = None
    DEFAULT_HOT_WORDS: List[str] = None
    
    def __post_init__(self):
        if self.HOT_WORDS_APIS is None:
            self.HOT_WORDS_APIS = [
                ("https://dailyapi.eray.cc/", ["weibo", "douyin", "baidu", "toutiao", "thepaper", "qq-news", "netease-news", "zhihu"]),
                ("https://hot.baiwumm.com/api/", ["weibo", "douyin", "baidu", "toutiao", "thepaper", "qq", "netease", "zhihu"]),
                ("https://cnxiaobai.com/DailyHotApi/", ["weibo", "douyin", "baidu", "toutiao", "thepaper", "qq-news", "netease-news", "zhihu"]),
                ("https://hotapi.nntool.cc/", ["weibo", "douyin", "baidu", "toutiao", "thepaper", "qq-news", "netease-news", "zhihu"]),
            ]
        
        if self.DEFAULT_HOT_WORDS is None:
            self.DEFAULT_HOT_WORDS = [
                "盛年不重来，一日难再晨", "千里之行，始于足下", "少年易学老难成，一寸光阴不可轻",
                "敏而好学，不耻下问", "海内存知已，天涯若比邻", "三人行，必有我师焉",
                "莫愁前路无知已，天下谁人不识君", "人生贵相知，何用金与钱", "天生我材必有用",
                '海纳百川有容乃大；壁立千仞无欲则刚', "穷则独善其身，达则兼济天下", "读书破万卷，下笔如有神",
            ]
        
        if self.PC_USER_AGENTS is None:
            self.PC_USER_AGENTS = [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.2478.131",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36 Edg/139.0.0.0",
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.2210.181",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36 Edg/139.0.0.0",
            ]
        
        if self.MOBILE_USER_AGENTS is None:
            self.MOBILE_USER_AGENTS = [
                "Mozilla/5.0 (Linux; Android 14; 2210132C Build/UP1A.231005.007) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.6422.52 Mobile Safari/537.36 EdgA/125.0.2535.51",
                "Mozilla/5.0 (iPad; CPU OS 16_7_8 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) EdgiOS/120.0.2210.150 Version/16.0 Mobile/15E148 Safari/604.1",
                "Mozilla/5.0 (iPhone; CPU iPhone OS 18_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) EdgiOS/123.0.2420.108 Version/18.0 Mobile/15E148 Safari/604.1",
                "Mozilla/5.0 (Linux; Android 12; Pixel 6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.6367.44 Mobile Safari/537.36 EdgA/124.0.2478.49",
                "Mozilla/5.0 (Linux; Android 14; Mi 10) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.6312.40 Mobile Safari/537.36 EdgA/123.0.2420.65",
                "Mozilla/5.0 (Linux; Android 9; ONEPLUS A5000 Build/PKQ1.180716.001; ) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36  BingSapphire/32.2.430730002",
                
            ]
    
    @staticmethod
    def generate_random_tnTID() -> str:
        """生成随机的tnTID参数"""
        # 生成32位随机十六进制字符串
        import secrets
        random_hex = secrets.token_hex(16).upper()
        return f"DSBOS_{random_hex}"
    
    @staticmethod
    def generate_random_tnCol() -> str:
        """生成1-50之间的随机数字"""
        return str(random.randint(1, 50))
    
    @staticmethod
    def get_random_pc_ua() -> str:
        """获取随机PC端User-Agent"""
        return random.choice(config.PC_USER_AGENTS)
    
    @staticmethod
    def get_random_mobile_ua() -> str:
        """获取随机移动端User-Agent"""
        return random.choice(config.MOBILE_USER_AGENTS)

config = Config()

# ==================== 账号管理 ====================
@dataclass
class AccountInfo:
    """账号信息类"""
    index: int
    alias: str
    cookies: str
    refresh_token: str = ""

class AccountManager:
    """账号管理器 - 读取环境变量中的账号配置"""
    
    @staticmethod
    def get_accounts() -> List[AccountInfo]:
        """获取所有账号配置"""
        accounts = []
        index = 1
        consecutive_empty = 0  # 连续空配置计数器
        max_consecutive_empty = 10  # 允许最多连续5个空配置
        max_check_index = 50  # 最大检查到第50个账号
        
        while index <= max_check_index:
            cookies = os.getenv(f"bing_ck_{index}")
            refresh_token = os.getenv(f"bing_token_{index}", "")
            
            # 如果既没有cookies也没有refresh_token
            if not cookies and not refresh_token:
                consecutive_empty += 1
                # 如果连续空配置超过限制，则停止搜索
                if consecutive_empty >= max_consecutive_empty:
                    break
                index += 1
                continue
            else:
                # 重置连续空配置计数器
                consecutive_empty = 0
            
            # 如果只有refresh_token没有cookies，跳过该账号
            if not cookies:
                print_log("账号配置", f"账号{index} 缺少cookies配置，跳过", index)
                # 发送缺少cookies配置的通知
                global_notification_manager.send_missing_cookies_config(index)
                index += 1
                continue
            
            # 验证cookie是否包含必需字段
            # 必须包含tifacfaatcs
            if 'tifacfaatcs=' not in cookies:
                print_log("账号配置", f"账号{index} 的cookie缺少必需字段: tifacfaatcs，cookie无效，请重新抓取", index)
                # 发送cookie失效通知
                global_notification_manager.send_cookie_missing_required_field(index, "tifacfaatcs")
                index += 1
                continue
            
            # 必须包含 .MSA.Auth
            auth_fields = ['.MSA.Auth=']
            has_auth_field = any(field in cookies for field in auth_fields)
            
            if not has_auth_field:
                print_log("账号配置", f"账号{index} 的cookie缺少认证字段（需要包含 .MSA.Auth），cookie无效，请重新抓取", index)
                # 发送cookie失效通知
                global_notification_manager.send_cookie_missing_auth_field(index)
                index += 1
                continue
            
            alias = f"账号{index}"
            accounts.append(AccountInfo(
                index=index,
                alias=alias,
                cookies=cookies,
                refresh_token=refresh_token
            ))
            
            index += 1
        
        # 从令牌缓存文件加载保存的令牌
        for account in accounts:
            cached_token = global_token_cache_manager.get_cached_token(account.alias, account.index)
            if cached_token:
                account.refresh_token = cached_token
        
        # 如果没有有效账号，发送总结性通知
        if not accounts:
            global_notification_manager.send_no_valid_accounts()
        
        return accounts


# ==================== 日志系统 ====================

class LogIcons:
    """日志状态图标"""
    # 基础状态
    INFO = "📊"
    SUCCESS = "✅"
    FAILED = "❌"
    WARNING = "⚠️"
    SKIP = "⏭️"
    START = "🚀"
    COMPLETE = "🎉"
    
    # 任务类型
    SEARCH_PC = "💻"
    SEARCH_MOBILE = "📱"
    SEARCH_PROGRESS = "🔍"
    DAILY_TASK = "📅"
    MORE_TASK = "🎯"
    READ_TASK = "📖"
    
    # 账号相关
    ACCOUNT = "👤"
    POINTS = "💰"
    EMAIL = "📧"
    
    # 系统相关
    INIT = "⚙️"
    CACHE = "💾"
    TOKEN = "🔑"
    NOTIFY = "📢"

class LogFormatter:
    """日志格式化器"""
    
    @staticmethod
    def create_progress_bar(current: int, total: int, width: int = 8) -> str:
        """创建进度条"""
        if total <= 0:
            return "░" * width + f" 0/0"
        
        filled = int((current / total) * width)
        filled = min(filled, width)  # 确保不超过宽度
        
        bar = "█" * filled + "░" * (width - filled)
        return f"{bar} {current}/{total}"
    
    @staticmethod
    def format_points_change(start: int, end: int) -> str:
        """格式化积分变化"""
        change = end - start
        if change > 0:
            return f"{start} → {end} (+{change})"
        elif change < 0:
            return f"{start} → {end} ({change})"
        else:
            return f"{start} (无变化)"

class LogLevel:
    """日志级别"""
    DEBUG = 0
    INFO = 1
    SUCCESS = 2
    WARNING = 3
    ERROR = 4

class EnhancedLogger:
    """增强的日志记录器 - 多线程安全版本"""
    
    def __init__(self, min_level: int = LogLevel.INFO):
        self.min_level = min_level
        self.formatter = LogFormatter()
        self.lock = threading.Lock()  # 添加线程锁
    
    def _get_timestamp(self) -> str:
        """获取时间戳"""
        return datetime.now().strftime("%H:%M:%S")
    
    def _format_account_prefix(self, account_index: Optional[int]) -> str:
        """格式化账号前缀"""
        if account_index is not None:
            return f"[账号{account_index}]"
        return "[系统]"
    
    def _log(self, level: int, icon: str, title: str, msg: str, account_index: Optional[int] = None):
        """内部日志方法 - 线程安全"""
        if level < self.min_level:
            return
            
        with self.lock:  # 确保线程安全
            timestamp = self._get_timestamp()
            account_prefix = self._format_account_prefix(account_index)
            log_message = f"{timestamp} {account_prefix} {icon} {title}: {msg or ''}"
            print(log_message, flush=True)
    
    # ==================== 基础日志方法 ====================
    def info(self, title: str, msg: str, account_index: Optional[int] = None):
        """信息日志"""
        self._log(LogLevel.INFO, LogIcons.INFO, title, msg, account_index)
    
    def success(self, title: str, msg: str, account_index: Optional[int] = None):
        """成功日志"""
        self._log(LogLevel.SUCCESS, LogIcons.SUCCESS, title, msg, account_index)
    
    def warning(self, title: str, msg: str, account_index: Optional[int] = None):
        """警告日志"""
        self._log(LogLevel.WARNING, LogIcons.WARNING, title, msg, account_index)
    
    def error(self, title: str, msg: str, account_index: Optional[int] = None):
        """错误日志"""
        self._log(LogLevel.ERROR, LogIcons.FAILED, title, msg, account_index)
    
    def skip(self, title: str, msg: str, account_index: Optional[int] = None):
        """跳过日志"""
        self._log(LogLevel.INFO, LogIcons.SKIP, title, msg, account_index)
    
    # ==================== 任务相关日志方法 ====================
    def account_start(self, email: str, initial_points: int, account_index: int):
        """账号开始处理"""
        # 邮箱脱敏显示：用户名前4位+**+完整域名
        if '@' in email:
            username, domain = email.split('@', 1)
            # 用户名显示前4位+**
            masked_username = username[:4] + "**" if len(username) > 4 else username + "**"
            # 保留完整域名
            masked_email = f"{masked_username}@{domain}"
        else:
            # 如果没有@符号，简单处理
            masked_email = email[:4] + "**" if len(email) > 4 else email
        
        msg = f"{masked_email} ({initial_points})"
        self._log(LogLevel.INFO, LogIcons.START, "初始化", msg, account_index)
    
    def account_complete(self, start_points: int, end_points: int, account_index: int):
        """账号处理完成"""
        msg = self.formatter.format_points_change(start_points, end_points)
        self._log(LogLevel.SUCCESS, LogIcons.COMPLETE, "处理完成", msg, account_index)
    

    
    # ==================== 搜索相关日志方法 ====================
    def search_start(self, search_type: str, required: int, max_attempts: int, account_index: int):
        """搜索开始"""
        icon = LogIcons.SEARCH_PC if search_type == "电脑" else LogIcons.SEARCH_MOBILE
        msg = f"理论需{required}次，预执行{max_attempts}次"
        self._log(LogLevel.INFO, icon, f"{search_type}搜索开始", msg, account_index)
    
    def search_progress(self, search_type: str, current: int, total: int, delay: int, account_index: int):
        """搜索进度"""
        progress_bar = self.formatter.create_progress_bar(current, total)
        # msg = f"{progress_bar} (第{current}次成功，等待{delay}秒...)"
        msg = f"{progress_bar}"
        self._log(LogLevel.INFO, LogIcons.SEARCH_PROGRESS, f"{search_type}搜索中", msg, account_index)
    
    def search_complete(self, search_type: str, attempts: int, account_index: int, success: bool = True):
        """搜索完成"""
        icon = LogIcons.SEARCH_PC if search_type == "电脑" else LogIcons.SEARCH_MOBILE
        if success:
            msg = f"任务已完成，执行了{attempts}次搜索"
            self._log(LogLevel.SUCCESS, LogIcons.SUCCESS, f"{search_type}搜索", msg, account_index)
        else:
            msg = f"任务未完成，执行了{attempts}次搜索"
            self._log(LogLevel.WARNING, LogIcons.WARNING, f"{search_type}搜索", msg, account_index)
    
    def search_progress_summary(self, search_type: str, count: int, start_progress: int, end_progress: int, account_index: int):
        """搜索进度总结"""
        msg = f"已完成{count}次，进度: {start_progress} → {end_progress}"
        self._log(LogLevel.INFO, LogIcons.SEARCH_PROGRESS, f"{search_type}搜索", msg, account_index)
    
    def search_skip(self, search_type: str, reason: str, account_index: int):
        """搜索跳过"""
        icon = LogIcons.SEARCH_PC if search_type == "电脑" else LogIcons.SEARCH_MOBILE
        self._log(LogLevel.INFO, LogIcons.SKIP, f"{search_type}搜索", f"跳过 ({reason})", account_index)
    


# 创建全局日志实例
logger = EnhancedLogger()

def print_log(title: str, msg: str, account_index: Optional[int] = None):
    """保持向后兼容的日志函数"""
    # 自动识别日志类型并使用对应的图标
    title_lower = title.lower()
    msg_lower = msg.lower() if msg else ""
    
    # 根据标题和消息内容选择合适的日志方法
    # 特殊处理：系统提示类消息优先识别为警告
    if ("提示" in title or "建议" in title or "提示" in msg_lower or "建议" in msg_lower):
        logger.warning(title, msg, account_index)
    # 优先检查失败/错误/未完成情况
    elif ("失败" in title or "错误" in title or "失败" in msg_lower or "错误" in msg_lower or "❌" in msg or 
        ("未完成" in msg_lower and "找到" not in msg_lower) or "终止" in msg_lower or "取消" in msg_lower):
        logger.error(title, msg, account_index)
    elif ("成功" in title or "完成" in title or "成功" in msg_lower or ("完成" in msg_lower and "未完成" not in msg_lower) or "✅" in msg):
        logger.success(title, msg, account_index)
    elif ("跳过" in title or "skip" in title_lower or "跳过" in msg_lower):
        logger.skip(title, msg, account_index)
    elif ("警告" in title or "warning" in title_lower or "警告" in msg_lower):
        logger.warning(title, msg, account_index)
    # 特殊处理：包含"找到"的消息通常是信息性的，使用信息图标
    elif "找到" in msg_lower:
        logger.info(title, msg, account_index)
    else:
        logger.info(title, msg, account_index)

# ==================== 异常处理装饰器 ====================
def retry_on_failure(max_retries: int = config.MAX_RETRIES, delay: int = config.RETRY_DELAY):
    """重试装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            # 获取更友好的函数名显示
            func_name = func.__name__
            if func_name == 'make_request':
                func_name = "网络请求"
            elif func_name == 'get_access_token':
                func_name = "令牌获取"
            elif func_name == 'get_read_progress':
                func_name = "阅读进度"
            elif func_name == 'submit_read_activity':
                func_name = "阅读提交"
            elif func_name == 'get_rewards_points':
                func_name = "积分查询"
            elif func_name == 'get_dashboard_data':
                func_name = "数据获取"
            
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        account_index = kwargs.get('account_index')
                        if account_index is not None:
                            print_log(f"{func_name}重试", f"第{attempt + 1}次尝试失败，{delay}秒后重试...", account_index)
                        else:
                            print_log(f"{func_name}重试", f"第{attempt + 1}次尝试失败，{delay}秒后重试...")
                        time.sleep(delay)
                    else:
                        account_index = kwargs.get('account_index')
                        if account_index is not None:
                            print_log(f"{func_name}失败", f"重试{max_retries}次后仍失败: {e}", account_index)
                        else:
                            print_log(f"{func_name}失败", f"重试{max_retries}次后仍失败: {e}")
            raise last_exception
        return wrapper
    return decorator

# ==================== 通知系统 ====================

class NotificationTemplates:
    """通知模板管理器 - 统一管理所有通知内容"""
    
    # Cookie获取地址
    COOKIE_URLS = "https://rewards.bing.com/welcome"
    
    @staticmethod
    def get_cookie_urls_text() -> str:
        """获取Cookie获取地址的格式化文本"""
        return f"   {NotificationTemplates.COOKIE_URLS}"
    
    @staticmethod
    def get_current_time() -> str:
        """获取当前时间格式化字符串"""
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    @classmethod
    def missing_cookies_config(cls, account_index: int) -> tuple[str, str]:
        """缺少cookies配置的通知模板"""
        title = "🚨 Microsoft Rewards 配置缺失"
        content = (
            f"账号{account_index} 缺少cookies配置\n\n"
            f"错误时间: {cls.get_current_time()}\n"
            f"需要处理: 为账号{account_index}添加环境变量 bing_ck_{account_index}\n\n"
            f"配置说明:\n"
            f"1. 设置环境变量: bing_ck_{account_index}=你的完整cookie字符串\n"
            f"2. Cookie获取地址:\n"
            f"{cls.get_cookie_urls_text()}"
        )
        return title, content
    
    @classmethod
    def cookie_missing_required_field(cls, account_index: int, field_name: str) -> tuple[str, str]:
        """Cookie缺少必需字段的通知模板"""
        title = "🚨 Microsoft Rewards Cookie配置错误"
        content = (
            f"账号{account_index} 的Cookie缺少必需字段: {field_name}\n\n"
            f"错误时间: {cls.get_current_time()}\n"
            f"需要处理: 重新获取账号{account_index}的完整Cookie\n\n"
            f"Cookie获取地址:\n"
            f"{cls.get_cookie_urls_text()}"
        )
        return title, content
    
    @classmethod
    def cookie_missing_auth_field(cls, account_index: int) -> tuple[str, str]:
        """Cookie缺少认证字段的通知模板"""
        title = "🚨 Microsoft Rewards Cookie认证字段缺失"
        content = (
            f"账号{account_index} 的Cookie缺少认证字段（需要包含 .MSA.Auth）\n\n"
            f"错误时间: {cls.get_current_time()}\n"
            f"需要处理: 重新获取账号{account_index}的完整Cookie\n\n"
            f"Cookie获取地址:\n"
            f"{cls.get_cookie_urls_text()}"
        )
        return title, content
    
    @classmethod
    def no_valid_accounts(cls) -> tuple[str, str]:
        """无有效账号配置的通知模板"""
        title = "🚨 Microsoft Rewards 无有效账号配置"
        content = (
            "所有账号配置均存在问题，无法启动任务！\n\n"
            f"检查时间: {cls.get_current_time()}\n\n"
            "常见问题及解决方案:\n"
            "1. 环境变量未设置: 检查 bing_ck_1, bing_ck_2 等\n"
            "2. Cookie格式错误: 确保包含 tifacfaatcs 字段\n"
            "3. 认证字段缺失: 确保包含 .MSA.Auth 字段\n\n"
            f"Cookie获取地址:\n"
            f"{cls.get_cookie_urls_text()}"
        )
        return title, content
    
    @classmethod
    def cookie_invalid(cls, account_index: Optional[int] = None) -> tuple[str, str]:
        """Cookie失效的通知模板"""
        account_info = f"账号{account_index} " if account_index else ""
        title = "🚨 Microsoft Rewards Cookie失效"
        content = (
            f"{account_info}Cookie已失效，无法获取积分和邮箱，请重新获取\n\n"
            f"失效时间: {cls.get_current_time()}\n"
            f"需要处理: 重新获取{account_info}的完整Cookie\n\n"
            f"Cookie获取地址:\n"
            f"{cls.get_cookie_urls_text()}"
        )
        return title, content
    
    @classmethod
    def token_invalid(cls, account_index: Optional[int] = None) -> tuple[str, str]:
        """Token失效的通知模板"""
        account_info = f"账号{account_index} " if account_index else ""
        title = "🚨 Microsoft Rewards Token失效"
        content = (
            f"{account_info}Refresh Token已失效，需要重新获取\n\n"
            f"失效时间: {cls.get_current_time()}\n"
            f"需要处理: 重新获取{account_info}的Refresh Token\n\n"
            "获取方法:\n"
            "1. 访问 https://login.live.com/oauth20_authorize.srf\n"
            "2. 使用Microsoft账号登录\n"
            "3. 获取授权码并换取Refresh Token"
        )
        return title, content
    
    @classmethod
    def task_summary(cls, summaries: List[str]) -> tuple[str, str]:
        """任务完成总结的通知模板"""
        title = "✅ Microsoft Rewards 任务完成"
        content = "\n\n".join(summaries)
        return title, content

class NotificationManager:
    """通知管理器"""
    
    def __init__(self):
        self.notify_client = self._init_notify_client()
    
    def _init_notify_client(self):
        """初始化通知客户端"""
        try:
            import notify
            return notify
        except ImportError:
            return self._create_mock_notify()
    
    def _create_mock_notify(self):
        """创建模拟通知客户端"""
        class MockNotify:
            def send(self, title, content):
                print("\n--- [通知] ---")
                print(f"标题: {title}")
                print(f"内容:\n{content}")
                print("-------------------------------")
        return MockNotify()
    
    def send(self, title: str, content: str):
        """发送通知"""
        self.notify_client.send(title, content)
    
    # 便捷的通知方法
    def send_missing_cookies_config(self, account_index: int):
        """发送缺少cookies配置的通知"""
        title, content = NotificationTemplates.missing_cookies_config(account_index)
        self.send(title, content)
    
    def send_cookie_missing_required_field(self, account_index: int, field_name: str):
        """发送Cookie缺少必需字段的通知"""
        title, content = NotificationTemplates.cookie_missing_required_field(account_index, field_name)
        self.send(title, content)
    
    def send_cookie_missing_auth_field(self, account_index: int):
        """发送Cookie缺少认证字段的通知"""
        title, content = NotificationTemplates.cookie_missing_auth_field(account_index)
        self.send(title, content)
    
    def send_no_valid_accounts(self):
        """发送无有效账号配置的通知"""
        title, content = NotificationTemplates.no_valid_accounts()
        self.send(title, content)
    
    def send_cookie_invalid(self, account_index: Optional[int] = None):
        """发送Cookie失效的通知"""
        title, content = NotificationTemplates.cookie_invalid(account_index)
        self.send(title, content)
    
    def send_token_invalid(self, account_index: Optional[int] = None):
        """发送Token失效的通知"""
        title, content = NotificationTemplates.token_invalid(account_index)
        self.send(title, content)
    
    def send_task_summary(self, summaries: List[str]):
        """发送任务完成总结的通知"""
        title, content = NotificationTemplates.task_summary(summaries)
        self.send(title, content)

global_notification_manager = NotificationManager()  # 全局通知管理器，用于账号验证阶段

# ==================== 缓存管理 ====================
class CacheManager:
    """缓存管理器"""
    
    def __init__(self, cache_file: str = config.CACHE_FILE):
        self.cache_file = cache_file
        self.lock = threading.Lock()
    
    def load_cache(self) -> Dict[str, Any]:
        """加载缓存数据（从统一缓存文件中提取推送相关数据和任务完成计数）"""
        all_data = self._load_unified_cache()
        
        # 过滤出推送相关的数据和任务完成计数
        cache_data = {}
        for key, value in all_data.items():
            if key.startswith('push_') or key.startswith('tasks_complete_'):
                cache_data[key] = value
        
        return cache_data
    
    def save_cache(self, data: Dict[str, Any]):
        """保存缓存数据到统一缓存文件"""
        try:
            with self.lock:
                # 读取现有的统一缓存数据
                all_cache_data = self._load_unified_cache()
                
                # 清理整个缓存文件中的过期推送记录
                today = date.today().isoformat()
                all_cache_data = self._clean_expired_data(all_cache_data, today)
                
                # 更新传入的数据
                for key, value in data.items():
                    all_cache_data[key] = value
                
                # 保存到统一缓存文件
                self._save_unified_cache(all_cache_data)
                
        except Exception as e:
            print_log("缓存错误", f"保存缓存失败: {e}")
    
    def _load_unified_cache(self) -> Dict[str, Any]:
        """加载统一缓存文件"""
        return global_token_cache_manager._load_all_cache_data()
    
    def _save_unified_cache(self, data: Dict[str, Any]):
        """保存到统一缓存文件"""
        global_token_cache_manager._save_all_cache_data(data)
    
    def _clean_expired_data(self, data: Dict[str, Any], today: str) -> Dict[str, Any]:
        """清理过期的缓存数据（只清理推送相关数据和任务完成计数）"""
        keys_to_keep = []
        for k in data:
            # 如果是推送相关的键，检查日期
            if k.startswith('push_'):
                date_part = k.replace('push_', '')
                # 只保留今天的推送记录，删除昨天及以前的
                if date_part == today:
                    keys_to_keep.append(k)
            # 如果是任务完成计数相关的键，检查日期
            elif k.startswith('tasks_complete_'):
                date_part = k.replace('tasks_complete_', '')
                # 只保留今天的任务完成计数，删除昨天及以前的
                if date_part == today:
                    keys_to_keep.append(k)
            else:
                # 非推送相关的键（如tokens等）全部保留
                keys_to_keep.append(k)
        
        return {k: data[k] for k in keys_to_keep}
    
    def has_pushed_today(self) -> bool:
        """检查今天是否已推送"""
        today = date.today().isoformat()
        data = self.load_cache()
        return data.get(f"push_{today}", False)
    
    def mark_pushed_today(self):
        """标记今天已推送"""
        today = date.today().isoformat()
        
        # 读取现有的统一缓存数据
        all_cache_data = self._load_unified_cache()
        
        # 检查是否已经有今天的推送记录
        if f"push_{today}" not in all_cache_data:
            # 如果没有今天的记录，先清理所有过期的推送记录
            all_cache_data = self._clean_expired_data(all_cache_data, today)
            print_log("缓存清理", "已清理过期的推送记录")
        
        # 添加今天的推送记录
        all_cache_data[f"push_{today}"] = True
        
        # 保存到统一缓存文件
        self._save_unified_cache(all_cache_data)
    
    def get_tasks_complete_count(self) -> int:
        """获取今天任务完成的次数"""
        today = date.today().isoformat()
        data = self.load_cache()
        return data.get(f"tasks_complete_{today}", 0)
    
    def increment_tasks_complete_count(self):
        """增加今天任务完成的次数"""
        today = date.today().isoformat()
        
        # 读取现有的统一缓存数据
        all_cache_data = self._load_unified_cache()
        
        # 检查是否已经有今天的任务完成计数记录
        if f"tasks_complete_{today}" not in all_cache_data:
            # 如果没有今天的记录，先清理所有过期的记录
            all_cache_data = self._clean_expired_data(all_cache_data, today)
            print_log("缓存清理", "已清理过期的任务完成计数记录")
        
        # 增加任务完成计数
        current_count = all_cache_data.get(f"tasks_complete_{today}", 0)
        new_count = current_count + 1
        
        # 限制最大计数为配置值
        if new_count > TASK_CONFIG['MAX_REPEAT_COUNT']:
            print_log("任务完成计数", f"计数已达到上限{TASK_CONFIG['MAX_REPEAT_COUNT']}次，不再增加", None)
            return
        
        all_cache_data[f"tasks_complete_{today}"] = new_count
        
        # 保存到统一缓存文件
        self._save_unified_cache(all_cache_data)
        
        print_log("重复运行", f"{new_count}/{TASK_CONFIG['MAX_REPEAT_COUNT']}", None)
        
        if new_count >= TASK_CONFIG['MAX_REPEAT_COUNT']:
            print_log("重复运行", "已达上限", None)
    
    def should_skip_execution(self) -> bool:
        """检查是否应该跳过脚本执行（任务已完成指定次数）"""
        return self.get_tasks_complete_count() >= TASK_CONFIG['MAX_REPEAT_COUNT']
    


global_cache_manager = CacheManager()  # 全局缓存管理器，用于推送状态检查

# ==================== Refresh Token 缓存管理 ====================
class TokenCacheManager:
    """Refresh Token 缓存管理器"""
    
    def __init__(self, token_file: str = config.CACHE_FILE):
        self.token_file = token_file
        self.lock = threading.Lock()
        self._cached_tokens = {}  # 内存缓存，避免重复保存
    
    def _load_all_cache_data(self) -> Dict[str, Any]:
        """加载统一缓存文件的所有数据"""
        if not os.path.exists(self.token_file):
            return {}
        
        try:
            with open(self.token_file, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if not content:  # 如果文件为空，返回空字典
                    return {}
                return json.loads(content)
        except json.JSONDecodeError as e:
            print_log("缓存错误", f"JSON格式错误: {e}，尝试修复文件")
            # 尝试修复损坏的JSON文件
            self._repair_json_file()
            return {}
        except Exception as e:
            print_log("缓存错误", f"读取失败: {e}")
            return {}
    
    def _save_all_cache_data(self, data: Dict[str, Any]):
        """保存数据到统一缓存文件"""
        try:
            # 使用线程安全的临时文件名（添加线程ID和随机数）
            thread_id = threading.get_ident()
            random_suffix = random.randint(1000, 9999)
            temp_file = f"{self.token_file}.tmp.{thread_id}.{random_suffix}"
            
            try:
                # 原子性保存到文件（先写临时文件，再重命名）
                with open(temp_file, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                
                # 原子性重命名
                import shutil
                shutil.move(temp_file, self.token_file)
                
            except Exception as file_error:
                # 清理临时文件
                try:
                    if os.path.exists(temp_file):
                        os.remove(temp_file)
                except:
                    pass
                raise file_error
                
        except Exception as e:
            print_log("缓存错误", f"保存失败: {e}")
    

    
    def save_token(self, account_alias: str, refresh_token: str, account_index: Optional[int] = None):
        """保存刷新令牌到统一缓存文件"""
        try:
            # 检查是否已经缓存过相同的令牌
            cache_key = f"{account_alias}_{refresh_token}"
            if cache_key in self._cached_tokens:
                return  # 已经缓存过，跳过
            
            with self.lock:
                # 确保目录存在
                os.makedirs(os.path.dirname(self.token_file) if os.path.dirname(self.token_file) else '.', exist_ok=True)
                
                # 读取现有缓存数据（包含推送状态等）
                all_cache_data = self._load_all_cache_data()
                
                # 获取或初始化tokens部分
                if 'tokens' not in all_cache_data:
                    all_cache_data['tokens'] = {}
                
                # 检查是否与现有令牌相同
                existing_token = all_cache_data['tokens'].get(account_alias, {}).get("refreshToken")
                if existing_token == refresh_token:
                    # 标记为已缓存，避免重复尝试
                    self._cached_tokens[cache_key] = True
                    return  # 令牌没有变化，跳过
                
                # 更新令牌
                all_cache_data['tokens'][account_alias] = {
                    "refreshToken": refresh_token,
                    "updatedAt": datetime.now().isoformat()
                }
                
                # 保存到统一缓存文件
                self._save_all_cache_data(all_cache_data)
                
                # 标记为已缓存
                self._cached_tokens[cache_key] = True
                
                print_log("令牌缓存", "更新成功", account_index)
                
        except Exception as e:
            print_log("令牌缓存", f"更新失败: {e}", account_index)
    
    def get_cached_token(self, account_alias: str, account_index: Optional[int] = None) -> Optional[str]:
        """获取缓存的刷新令牌"""
        try:
            all_cache_data = self._load_all_cache_data()
            tokens = all_cache_data.get('tokens', {})
            account_data = tokens.get(account_alias)
            if account_data and account_data.get("refreshToken"):
                return account_data["refreshToken"]
            return None
        except Exception as e:
            print_log("令牌缓存", f"读取失败: {e}", account_index)
            return None
    
    def _repair_json_file(self):
        """尝试修复损坏的JSON文件"""
        try:
            # 备份损坏的文件
            backup_file = self.token_file + f".backup_{int(time.time())}"
            if os.path.exists(self.token_file):
                import shutil
                shutil.copy2(self.token_file, backup_file)
                print_log("令牌缓存", f"已备份损坏文件到: {backup_file}")
            
            # 创建新的空文件
            with open(self.token_file, "w", encoding="utf-8") as f:
                json.dump({}, f, ensure_ascii=False, indent=2)
            
            print_log("令牌缓存", "已重新创建令牌缓存文件")
        except Exception as e:
            print_log("令牌缓存", f"修复文件失败: {e}")

global_token_cache_manager = TokenCacheManager()  # 全局令牌缓存管理器，用于账号验证阶段

# ==================== 热搜词管理 ====================
class HotWordsManager:
    """热搜词管理器"""
    
    def __init__(self):
        self.hot_words = self._fetch_hot_words()
    
    @retry_on_failure(max_retries=2, delay=1)
    def _fetch_hot_words(self, max_count: int = config.HOT_WORDS_MAX_COUNT) -> List[str]:
        """获取热搜词"""
        apis_shuffled = config.HOT_WORDS_APIS[:]
        random.shuffle(apis_shuffled)
        
        for base_url, sources in apis_shuffled:
            sources_shuffled = sources[:]
            random.shuffle(sources_shuffled)
            
            for source in sources_shuffled:
                api_url = base_url + source
                try:
                    resp = requests.get(api_url, timeout=10)
                    if resp.status_code == 200:
                        data = resp.json()
                        if isinstance(data, dict) and 'data' in data and data['data']:
                            all_titles = [item.get('title') for item in data['data'] if item.get('title')]
                            if all_titles:
                                print_log("热搜词", f"成功获取热搜词 {len(all_titles)} 条，来源: {api_url}")
                                random.shuffle(all_titles)
                                return all_titles[:max_count]
                except Exception:
                    continue
        
        print_log("热搜词", "全部热搜API失效，使用默认搜索词。")
        default_words = config.DEFAULT_HOT_WORDS[:max_count]
        random.shuffle(default_words)
        return default_words
    
    def get_random_word(self) -> str:
        """获取随机热搜词"""
        return random.choice(self.hot_words) if self.hot_words else random.choice(config.DEFAULT_HOT_WORDS)

hot_words_manager = HotWordsManager()

# ==================== HTTP请求管理 ====================
class RequestManager:
    """HTTP请求管理器 - 支持独立Session"""
    
    def __init__(self):
        """初始化请求管理器，创建独立的Session"""
        self.session = requests.Session()
    
    @staticmethod
    def get_browser_headers(cookies: str) -> Dict[str, str]:
        """获取浏览器请求头"""
        return {
            "user-agent": config.get_random_pc_ua(),
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "accept-encoding": "gzip, deflate, br, zstd",
            "sec-ch-ua": '"Not;A=Brand";v="99", "Microsoft Edge";v="139", "Chromium";v="139"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-site": "none",
            "sec-fetch-mode": "navigate",
            "sec-fetch-user": "?1",
            "sec-fetch-dest": "document",
            "upgrade-insecure-requests": "1",
            "x-edge-shopping-flag": "1",
            "referer": "https://rewards.bing.com/",
            "cookie": cookies
        }
    
    @staticmethod
    def get_mobile_headers(cookies: str) -> Dict[str, str]:
        """获取移动端请求头"""
        return {
            "user-agent": config.get_random_mobile_ua(),
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
            "accept-encoding": "gzip, deflate, br, zstd",
            "sec-ch-ua": '"Not;A=Brand";v="99", "Chromium";v="124"',
            "sec-ch-ua-mobile": "?1",
            "sec-ch-ua-platform": '"Android"',
            "sec-fetch-site": "none",
            "sec-fetch-mode": "navigate",
            "sec-fetch-user": "?1",
            "sec-fetch-dest": "document",
            "upgrade-insecure-requests": "1",
            "cookie": cookies
        }
    
    @retry_on_failure(max_retries=2)
    def make_request(self, method: str, url: str, headers: Dict[str, str], 
                    params: Optional[Dict] = None, data: Optional[str] = None,
                    timeout: int = config.REQUEST_TIMEOUT, account_index: Optional[int] = None) -> requests.Response:
        """统一的HTTP请求方法 - 使用独立Session"""
        if method.upper() == 'GET':
            return self.session.get(url, headers=headers, params=params, timeout=timeout)
        elif method.upper() == 'POST':
            # 判断是否为JSON数据
            if headers.get('Content-Type') == 'application/json' and data:
                return self.session.post(url, headers=headers, json=json.loads(data), timeout=timeout)
            elif isinstance(data, dict):
                # 表单数据
                return self.session.post(url, headers=headers, data=data, timeout=timeout)
            else:
                # 字符串数据
                return self.session.post(url, headers=headers, data=data, timeout=timeout)
        else:
            raise ValueError(f"不支持的HTTP方法: {method}")
    
    def close(self):
        """关闭Session"""
        if hasattr(self, 'session'):
            self.session.close()

# ==================== 主要业务逻辑类 ====================
class RewardsService:
    """Microsoft Rewards服务类 - 增强版本支持令牌缓存和独立Session"""
    
    # ==================== 1. 基础设施方法 ====================
    def __init__(self):
        """初始化服务，创建独立的请求管理器和通知管理器"""
        self.request_manager = RequestManager()
        self.notification_manager = NotificationManager()  # 每个实例独立的通知管理器
        # 为每个实例创建独立的缓存管理器，避免文件锁竞争
        self.cache_manager = CacheManager()
        self.token_cache_manager = TokenCacheManager()
    
    def __del__(self):
        """析构函数，确保Session被正确关闭"""
        if hasattr(self, 'request_manager'):
            self.request_manager.close()
    
    # ==================== 2. 核心数据获取方法 ====================
    @retry_on_failure()
    def get_rewards_points(self, cookies: str, account_index: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """查询当前积分、账号信息和获取token"""
        headers = self.request_manager.get_browser_headers(cookies)
        # 添加PC端特有的头部
        headers.update({
            'cache-control': 'max-age=0',
            'sec-ch-ua': '"Not;A=Brand";v="99", "Microsoft Edge";v="139", "Chromium";v="139"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-full-version': '139.0.3405.86',
            'sec-ch-ua-arch': 'x86',
            'sec-ch-ua-platform': '"Windows"',
            'sec-ch-ua-platform-version': '19.0.0',
            'sec-ch-ua-model': '""',
            'sec-ch-ua-bitness': '64',
            'sec-ch-ua-full-version-list': '"Not;A=Brand";v="99.0.0.0", "Microsoft Edge";v="139.0.3405.86", "Chromium";v="139.0.7258.67"',
            'upgrade-insecure-requests': '1',
            'x-edge-shopping-flag': '1',
            'sec-ms-gec': 'F4AE7EBFE1C688D0967DE661CC98B823383760340F7B0B42D9FFA10D74621BEA',
            'sec-ms-gec-version': '1-139.0.3405.86',
            'x-client-data': 'eyIxIjoiMCIsIjIiOiIwIiwiMyI6IjAiLCI0IjoiLTExNzg4ODc1Mjc3OTM5NTI1MDUiLCI2Ijoic3RhYmxlIiwiOSI6ImRlc2t0b3AifQ==',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-user': '?1',
            'sec-fetch-dest': 'document',
            'referer': 'https://rewards.bing.com/welcome'
        })
        
        url = 'https://rewards.bing.com'
        
        response = self.request_manager.make_request('GET', url, headers, account_index=account_index)
        response.raise_for_status()
        
        content = response.text
        
        # 提取积分和邮箱
        points_pattern = r'"availablePoints":(\d+)'
        email_pattern = r'email:\s*"([^"]+)"'
        
        points_match = re.search(points_pattern, content)
        email_match = re.search(email_pattern, content)
        
        available_points = int(points_match.group(1)) if points_match else None
        email = email_match.group(1) if email_match else None
        
        # 提取token
        token_match = re.search(r'name="__RequestVerificationToken".*?value="([^"]+)"', content)
        token = token_match.group(1) if token_match else None
        
        if available_points is None or email is None:
            print_log("账号信息", "Cookie可能已失效，无法获取积分和邮箱", account_index)
            # 立即推送Cookie失效通知
            self._send_cookie_invalid_notification(account_index)
            return None
        
        if token is None:
            print_log("账号信息", "无法获取RequestVerificationToken", account_index)
        
        return {
            'points': available_points,
            'email': email,
            'token': token
        }
    
    @retry_on_failure()
    def get_dashboard_data(self, cookies: str, account_index: Optional[int] = None, silent: bool = False) -> Optional[Dict[str, Any]]:
        """获取dashboard数据（从API接口）"""
        try:
            # 调用API获取dashboard数据
            import time
            timestamp = int(time.time() * 1000)
            api_headers = self.request_manager.get_browser_headers(cookies)
            api_headers.update({
                'sec-ch-ua-full-version-list': '"Not;A=Brand";v="99.0.0.0", "Microsoft Edge";v="139.0.3405.86", "Chromium";v="139.0.7258.67"',
                'sec-ch-ua-platform': '"Windows"',
                'sec-ch-ua': '"Not;A=Brand";v="99", "Microsoft Edge";v="139", "Chromium";v="139"',
                'sec-ch-ua-bitness': '64',
                'sec-ch-ua-model': '""',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-arch': 'x86',
                'correlation-context': 'v=1,ms.b.tel.market=zh-Hans',
                'sec-ch-ua-full-version': '139.0.3405.86',
                'accept': 'application/json, text/javascript, */*; q=0.01',
                'sec-ch-ua-platform-version': '19.0.0',
                'x-edge-shopping-flag': '1',
                'sec-ms-gec': 'F4AE7EBFE1C688D0967DE661CC98B823383760340F7B0B42D9FFA10D74621BEA',
                'sec-ms-gec-version': '1-139.0.3405.86',
                'x-client-data': 'eyIxIjoiMCIsIjIiOiIwIiwiMyI6IjAiLCI0IjoiLTExNzg4ODc1Mjc3OTM5NTI1MDUiLCI2Ijoic3RhYmxlIiwiOSI6ImRlc2t0b3AifQ==',
                'sec-fetch-site': 'same-origin',
                'sec-fetch-mode': 'cors',
                'sec-fetch-dest': 'empty',
                'referer': 'https://rewards.bing.com/',
                'X-Requested-With': 'XMLHttpRequest'
            })
            
            # api_url = f"https://rewards.bing.com/api/getuserinfo?type=1&X-Requested-With=XMLHttpRequest&_={timestamp}"
            api_url = f"https://rewards.bing.com/api/getuserinfo"
            api_resp = self.request_manager.make_request('GET', api_url, api_headers, timeout=30, account_index=account_index)
            api_resp.raise_for_status()
            
            dashboard_json = api_resp.json()
            
            if not dashboard_json or 'dashboard' not in dashboard_json:
                if not silent:
                    print_log('数据获取', "API返回的数据格式不正确", account_index)
                return None
            
            return dashboard_json
        except Exception as e:
            # 对于常见的服务器错误，使用静默模式减少日志噪音
            if not silent:
                error_msg = str(e)
                # 简化常见错误信息
                if "503" in error_msg:
                    print_log('数据获取', "服务器暂时不可用，稍后重试", account_index)
                elif "500" in error_msg:
                    print_log('数据获取', "服务器内部错误", account_index)
                elif "timeout" in error_msg.lower():
                    print_log('数据获取', "请求超时", account_index)
                else:
                    print_log('数据获取', f"获取失败: {error_msg}", account_index)
            return None

    def get_account_level(self, dashboard_data: Dict[str, Any]) -> str:
        """获取账号等级"""
        if not dashboard_data:
            return "Level1"
        dashboard = dashboard_data.get('dashboard', {})
        user_status = dashboard.get('userStatus', {})
        level_info = user_status.get('levelInfo', {})
        # 确保level_info不为None
        if not level_info:
            return "Level1"
        return level_info.get('activeLevel', 'Level1')

    # ==================== 3. 令牌相关方法 ====================
    @retry_on_failure()
    def get_access_token(self, refresh_token: str, account_alias: str = "", account_index: Optional[int] = None, silent: bool = False) -> Optional[str]:
        """获取访问令牌用于阅读任务 - 支持令牌自动更新"""
        try:
            data = {
                'client_id': '0000000040170455',
                'refresh_token': refresh_token,
                'scope': 'service::prod.rewardsplatform.microsoft.com::MBI_SSL',
                'grant_type': 'refresh_token'
            }
            
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'User-Agent': config.get_random_pc_ua(),
                'sec-ch-ua-platform': '"Windows"',
                'sec-ch-ua': '"Not;A=Brand";v="99", "Microsoft Edge";v="139", "Chromium";v="139"',
                'sec-ch-ua-mobile': '?0',
                'Accept': '*/*',
                'Origin': 'https://login.live.com',
                'X-Edge-Shopping-Flag': '1',
                'Sec-Fetch-Site': 'same-origin',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Dest': 'empty',
                'Referer': 'https://login.live.com/oauth20_desktop.srf',
                'Accept-Encoding': 'gzip, deflate, br, zstd',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6'
            }
            
            response = self.request_manager.make_request(
                'POST', 'https://login.live.com/oauth20_token.srf', 
                headers, data=data, account_index=account_index
            )
            
            if response.status_code == 200:
                token_data = response.json()
                if 'access_token' in token_data:
                    # print_log("令牌获取", "成功获取访问令牌", account_index)
                    
                    # 检查是否有新的refresh_token返回并启用了缓存（非静默模式）
                    if (not silent and CACHE_ENABLED and 'refresh_token' in token_data and 
                        token_data['refresh_token'] != refresh_token and account_alias):
                        # print_log("令牌更新", f"检测到新的刷新令牌，正在更新缓存", account_index)
                        # 保存新的refresh_token到缓存
                        self.token_cache_manager.save_token(account_alias, token_data['refresh_token'], account_index)
                    
                    return token_data['access_token']
            
            # 静默模式下不处理错误通知
            if silent:
                return None
            
            # 检查是否为令牌失效错误
            if response.status_code in [400, 401, 403]:
                try:
                    error_data = response.json()
                    error_description = error_data.get('error_description', '').lower()
                    error_code = error_data.get('error', '').lower()
                    
                    # 常见的令牌失效错误标识
                    token_invalid_indicators = [
                        'invalid_grant', 'expired_token', 'refresh_token', 
                        'invalid_request', 'unauthorized', 'invalid refresh token'
                    ]
                    
                    if any(indicator in error_description or indicator in error_code for indicator in token_invalid_indicators):
                        print_log("令牌获取", "刷新令牌已失效，尝试读取环境变量", account_index)
                        
                        # 尝试从环境变量重新读取令牌
                        new_token = os.getenv(f"bing_token_{account_index}")
                        if new_token and new_token.strip() and new_token != refresh_token:
                            print_log("令牌获取", f"从环境变量获取到新令牌，重试", account_index)
                            # 使用新令牌重试
                            return self.get_access_token(new_token.strip(), account_alias, account_index, silent)
                        else:
                            print_log("令牌获取", "环境变量中无新令牌，发送失效通知", account_index)
                            self._send_token_invalid_notification(account_index)
                            return None
                except:
                    pass
            
            print_log("令牌获取", f"获取访问令牌失败，状态码: {response.status_code}", account_index)
            return None
            
        except Exception as e:
            # 静默模式下不处理错误通知
            if silent:
                return None
                
            # 检查异常是否包含令牌失效的信息
            error_message = str(e).lower()
            token_invalid_indicators = [
                'invalid_grant', 'expired_token', 'refresh_token', 
                'unauthorized', '401', '403', 'invalid refresh token'
            ]
            
            if any(indicator in error_message for indicator in token_invalid_indicators):
                print_log("令牌获取", "刷新令牌已失效（异常检测），尝试读取环境变量", account_index)
                
                # 尝试从环境变量重新读取令牌
                new_token = os.getenv(f"bing_token_{account_index}")
                if new_token and new_token.strip() and new_token != refresh_token:
                    print_log("令牌获取", f"从环境变量获取到新令牌，重试", account_index)
                    # 使用新令牌重试
                    return self.get_access_token(new_token.strip(), account_alias, account_index, silent)
                else:
                    print_log("令牌获取", "环境变量中无新令牌，发送失效通知", account_index)
                    self._send_token_invalid_notification(account_index)
            else:
                print_log("令牌获取", f"获取访问令牌异常: {e}", account_index)
            return None
    
    @retry_on_failure()
    def get_read_progress(self, access_token: str, account_index: Optional[int] = None) -> Dict[str, int]:
        """获取阅读任务进度"""
        try:
            headers = {
                'Authorization': f'Bearer {access_token}',
                'User-Agent': config.get_random_mobile_ua(),
                'Accept-Encoding': 'gzip',
                'x-rewards-partnerid': 'startapp',
                'x-rewards-appid': 'SAAndroid/32.2.430730002',
                'x-rewards-country': 'cn',
                'x-rewards-language': 'zh-hans',
                'x-rewards-flights': 'rwgobig'
            }
            
            response = self.request_manager.make_request(
                'GET', 
                'https://prod.rewardsplatform.microsoft.com/dapi/me?channel=SAAndroid&options=613',
                headers, account_index=account_index
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'response' in data and 'promotions' in data['response']:
                    for promotion in data['response']['promotions']:
                        if (promotion.get('attributes', {}).get('offerid') == 
                            'ENUS_readarticle3_30points'):
                            # 获取max和progress值
                            max_value = promotion['attributes'].get('max')
                            progress_value = promotion['attributes'].get('progress')
                            
                            # 检查值是否有效
                            if max_value is not None and progress_value is not None:
                                try:
                                    return {
                                        'max': int(max_value),
                                        'progress': int(progress_value)
                                    }
                                except (ValueError, TypeError):
                                    # 如果转换失败，继续查找其他任务或抛出异常
                                    print_log("阅读进度", f"数据格式错误: max={max_value}, progress={progress_value}", account_index)
                                    continue
                            else:
                                # 如果值为空，记录日志并继续查找
                                print_log("阅读进度", f"数据为空: max={max_value}, progress={progress_value}", account_index)
                                continue
                    
                    # 如果没有找到有效的阅读任务数据，抛出异常让重试机制处理
                    print_log("阅读进度", "未找到有效的阅读任务数据，将重试", account_index)
                    raise ValueError("未找到有效的阅读任务数据")
                else:
                    # 如果响应结构不正确，抛出异常
                    print_log("阅读进度", "API响应结构不正确，将重试", account_index)
                    raise ValueError("API响应结构不正确")
            
            # 如果状态码不是200，抛出异常让重试机制处理
            print_log("阅读进度", f"获取阅读进度失败，状态码: {response.status_code}", account_index)
            raise Exception(f"HTTP状态码错误: {response.status_code}")
            
        except Exception as e:
            # 重新抛出异常，让重试装饰器处理
            print_log("阅读进度", f"获取阅读进度异常: {e}", account_index)
            raise

    # ==================== 4. 搜索任务相关方法 ====================
    def is_pc_search_complete(self, dashboard_data: Dict[str, Any]) -> bool:
        """检查电脑搜索是否完成"""
        if not dashboard_data:
            return False
        dashboard = dashboard_data.get('dashboard', {})
        user_status = dashboard.get('userStatus', {})
        counters = user_status.get('counters', {})
        pc_search_tasks = counters.get('pcSearch', [])
        
        # 如果没有任务数据，认为未完成
        if not pc_search_tasks:
            return False
            
        for task in pc_search_tasks:
            # 明确检查complete字段，默认为False（未完成）
            if not task.get('complete', False):
                return False
        return True

    def is_mobile_search_complete(self, dashboard_data: Dict[str, Any]) -> bool:
        """检查移动搜索是否完成"""
        if not dashboard_data:
            return False
        dashboard = dashboard_data.get('dashboard', {})
        user_status = dashboard.get('userStatus', {})
        counters = user_status.get('counters', {})
        mobile_search_tasks = counters.get('mobileSearch', [])
        
        # 如果没有任务数据，认为未完成
        if not mobile_search_tasks:
            return False
            
        for task in mobile_search_tasks:
            # 明确检查complete字段，默认为False（未完成）
            if not task.get('complete', False):
                return False
        return True

    def _enhance_mobile_cookies(self, cookies: str) -> str:
        """增强移动端cookies"""
        enhanced_cookies = cookies
        
        # 移除桌面端特有字段
        desktop_fields_to_remove = [
            r'_HPVN=[^;]+', r'_RwBf=[^;]+', r'USRLOC=[^;]+',
            r'BFBUSR=[^;]+', r'_Rwho=[^;]+', r'ipv6=[^;]+', r'_clck=[^;]+',
            r'_clsk=[^;]+', r'webisession=[^;]+', r'MicrosoftApplicationsTelemetryDeviceId=[^;]+',
            r'MicrosoftApplicationsTelemetryFirstLaunchTime=[^;]+', r'MSPTC=[^;]+', r'vdp=[^;]+'
        ]
        
        for pattern in desktop_fields_to_remove:
            enhanced_cookies = re.sub(pattern, '', enhanced_cookies)
        
        enhanced_cookies = re.sub(r';;+', ';', enhanced_cookies).strip('; ')
        
        # 添加移动端特有字段
        # 1. SRCHD字段 - 移动端必需
        if 'SRCHD=' not in enhanced_cookies:
            enhanced_cookies += '; SRCHD=AF=NOFORM'
        
        # 2. SRCHUSR字段 - 更新为移动端格式
        current_date = datetime.now().strftime('%Y%m%d')
        if 'SRCHUSR=' in enhanced_cookies:
            enhanced_cookies = re.sub(r'SRCHUSR=[^;]+', f'SRCHUSR=DOB={current_date}&DS=1', enhanced_cookies)
        else:
            enhanced_cookies += f'; SRCHUSR=DOB={current_date}&DS=1'
        
        return enhanced_cookies

    @retry_on_failure(max_retries=2, delay=1)
    def perform_pc_search(self, cookies: str, account_index: Optional[int] = None, 
                         email: Optional[str] = None) -> bool:
        """执行电脑搜索"""
        q = hot_words_manager.get_random_word()
        
        params = {
            "q": q,
            "qs": "HS",
            "form": "TSASDS"
        }
        
        headers = {
            "User-Agent": config.get_random_pc_ua(),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Referer": "https://rewards.bing.com/",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Cookie": cookies
        }

        try:
            # 第一步：执行搜索
            search_url = "https://cn.bing.com/search"
            final_search_url = None
            
            # 发送请求但不自动跟随重定向
            search_response = self.request_manager.session.get(search_url, headers=headers, params=params, timeout=config.REQUEST_TIMEOUT, allow_redirects=False)
            
            # 检查是否为重定向状态码
            redirect_status_codes = {301, 302, 303, 307, 308}
            if search_response.status_code in redirect_status_codes:
                print_log("电脑搜索", f"cn.bing.com 返回重定向状态码 {search_response.status_code}，切换到 www.bing.com", account_index)
                
                # 使用 www.bing.com
                search_url = "https://www.bing.com/search"
                search_response = self.request_manager.make_request('GET', search_url, headers, params)
                final_search_url = search_url
            else:
                # 如果不是重定向，检查是否成功
                if search_response.status_code != 200:
                    # 如果 cn.bing.com 返回其他错误状态码，也尝试 www.bing.com
                    print_log("电脑搜索", f"cn.bing.com 返回状态码 {search_response.status_code}，切换到 www.bing.com", account_index)
                    
                    search_url = "https://www.bing.com/search"
                    search_response = self.request_manager.make_request('GET', search_url, headers, params)
                    final_search_url = search_url
                else:
                    final_search_url = "https://cn.bing.com/search"
            
            if search_response.status_code != 200:
                print_log("电脑搜索", f"搜索失败，最终状态码: {search_response.status_code}", account_index)
                return False
            
            # 提取必要的参数
            html_content = search_response.text
            ig_match = re.search(r'IG:"([^"]+)"', html_content)
            iid_match = re.search(r'data_iid\s*=\s*"([^"]+)"', html_content)
            
            if not ig_match or not iid_match:
                print_log("电脑搜索", "无法从页面提取 IG 或 IID，跳过报告活动", account_index)
                return True  # 搜索成功但无法报告活动，仍然返回True
            
            # 延迟
            time.sleep(random.uniform(config.TASK_DELAY_MIN, config.TASK_DELAY_MAX))
            
            # 第二步：报告活动
            ig_value = ig_match.group(1)
            iid_value = iid_match.group(1)
            
            # 构建完整的搜索URL
            req = requests.Request('GET', final_search_url, params=params, headers=headers)
            prepared_req = req.prepare()
            full_search_url = prepared_req.url
            
            # 根据最终使用的域名构建报告URL
            if "www.bing.com" in final_search_url:
                report_url = (f"https://www.bing.com/rewardsapp/reportActivity?IG={ig_value}&IID={iid_value}"
                             f"&q={quote(q)}&qs=HS&form=TSASDS&ajaxreq=1")
            else:
                report_url = (f"https://cn.bing.com/rewardsapp/reportActivity?IG={ig_value}&IID={iid_value}"
                             f"&q={quote(q)}&qs=HS&form=TSASDS&ajaxreq=1")
            
            post_headers = {
                "User-Agent": headers["User-Agent"],
                "Accept": "*/*",
                "Origin": final_search_url.split('/search')[0],  # 提取域名部分
                "Referer": full_search_url,
                "Content-Type": "application/x-www-form-urlencoded",
                "Cookie": cookies
            }
            
            post_data = f"url={quote(full_search_url, safe='')}&V=web"
            report_response = self.request_manager.make_request('POST', report_url, post_headers, data=post_data)
            
            if 200 <= report_response.status_code < 400:
                return True
            else:
                print_log("电脑搜索", f"报告活动失败，状态码: {report_response.status_code}", account_index)
                return True  # 搜索成功但报告失败，仍然返回True
    
        except Exception as e:
            print_log("电脑搜索", f"搜索失败: {e}", account_index)
            return False
    
    @retry_on_failure(max_retries=2, delay=1)
    def perform_mobile_search(self, cookies: str, account_index: Optional[int] = None, 
                            email: Optional[str] = None) -> bool:
        """执行移动搜索"""
        q = hot_words_manager.get_random_word()
        
        # 生成随机的tnTID和tnCol参数
        random_tnTID = config.generate_random_tnTID()
        random_tnCol = config.generate_random_tnCol()
        
        # 处理cookie
        enhanced_cookies = self._enhance_mobile_cookies(cookies)

        params = {
            "q": q,
            "form": "NPII01",
            "filters": f'tnTID:"{random_tnTID}" tnVersion:"d1d6d5bcada64df7a0182f7bc3516b45" Segment:"popularnow.carousel" tnCol:"{random_tnCol}" tnScenario:"TrendingTopicsAPI" tnOrder:"4a2117a4-4237-4b9e-85d0-67fef7b5f2be"',
            "ssp": "1",
            "safesearch": "moderate",
            "setlang": "zh-hans",
            "cc": "CN",
            "ensearch": "0",
            "PC": "SANSAAND"
        }
        
        headers = {
            "user-agent": config.get_random_mobile_ua(),
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
            "x-search-market": "zh-CN",
            "upgrade-insecure-requests": "1",
            "accept-encoding": "gzip, deflate",
            "accept-language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
            "x-requested-with": "com.microsoft.bing",            
            "cookie": enhanced_cookies
        }

        try:
            # 第一步：执行搜索
            search_url = "https://cn.bing.com/search"
            final_search_url = None
            final_headers = headers.copy()
            
            # 发送请求但不自动跟随重定向
            search_response = self.request_manager.session.get(search_url, headers=headers, params=params, timeout=config.REQUEST_TIMEOUT, allow_redirects=False)
            
            # 检查是否为重定向状态码
            redirect_status_codes = {301, 302, 303, 307, 308}
            if search_response.status_code in redirect_status_codes:
                print_log("移动搜索", f"cn.bing.com 返回重定向状态码 {search_response.status_code}，切换到 www.bing.com", account_index)
                
                # 使用 www.bing.com，添加必要的请求头
                search_url = "https://www.bing.com/search"
                
                # 添加重定向相关参数
                params.update({
                    "rdr": "1",
                    "rdrig": config.generate_random_tnTID()[:32]  # 使用随机IG值
                })
                
                search_response = self.request_manager.make_request('GET', search_url, final_headers, params)
                final_search_url = search_url
            else:
                # 如果不是重定向，检查是否成功
                if search_response.status_code != 200:
                    # 如果 cn.bing.com 返回其他错误状态码，也尝试 www.bing.com
                    print_log("移动搜索", f"cn.bing.com 返回状态码 {search_response.status_code}，切换到 www.bing.com", account_index)
                    
                    search_url = "https://www.bing.com/search"
                    
                    search_response = self.request_manager.make_request('GET', search_url, final_headers, params)
                    final_search_url = search_url
                else:
                    final_search_url = "https://cn.bing.com/search"
            
            if search_response.status_code != 200:
                print_log("移动搜索", f"搜索失败，最终状态码: {search_response.status_code}", account_index)
                return False
            
            # 延迟
            time.sleep(random.uniform(config.TASK_DELAY_MIN, config.TASK_DELAY_MAX))
            
            # 第二步：报告活动
            req = requests.Request('GET', final_search_url, headers=final_headers, params=params)
            prepared_req = req.prepare()
            full_search_url = prepared_req.url
            
            # 根据最终使用的域名构建报告URL
            if "www.bing.com" in final_search_url:
                report_url = "https://www.bing.com/rewardsapp/reportActivity"
            else:
                report_url = "https://cn.bing.com/rewardsapp/reportActivity"
            
            post_data_str = f"url={quote(full_search_url, safe='')}&V=web"
            
            # 构建报告活动的请求头
            post_headers = {
                "user-agent": final_headers["user-agent"],
                "accept": "*/*",
                "content-type": "application/x-www-form-urlencoded; charset=utf-8",
                "cookie": enhanced_cookies
            }
            
            # 根据域名设置不同的referer
            if "www.bing.com" in final_search_url:
                post_headers.update({
                    "referer": "https://www.bing.com/",
                    "request_user_info": "true",
                    "accept-encoding": "gzip",
                    "x-search-market": "zh-CN"
                })
            else:
                post_headers["referer"] = "https://cn.bing.com/"
            
            report_response = self.request_manager.make_request('POST', report_url, post_headers, data=post_data_str)
            
            if 200 <= report_response.status_code < 400:
                return True
            else:
                print_log("移动搜索", f"报告活动失败，状态码: {report_response.status_code}", account_index)
                return True  # 搜索成功但报告失败，仍然返回True

        except Exception as e:
            print_log("移动搜索", f"搜索失败: {e}", account_index)
            return False

    # ==================== 5. 阅读任务相关方法 ====================
    @retry_on_failure()
    def submit_read_activity(self, access_token: str, account_index: Optional[int] = None) -> bool:
        """提交阅读活动"""
        try:
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {access_token}',
                'User-Agent': config.get_random_mobile_ua(),
                'Accept-Encoding': 'gzip',
                'x-rewards-partnerid': 'startapp',
                'x-rewards-appid': 'SAAndroid/32.2.430730002',
                'x-rewards-country': 'cn',
                'x-rewards-language': 'zh-hans',
                'x-rewards-flights': 'rwgobig'
            }
            
            payload = {
                'amount': 1,
                'country': 'cn',
                'id': '',
                'type': 101,
                'attributes': {
                    'offerid': 'ENUS_readarticle3_30points'
                }
            }
            
            response = self.request_manager.make_request(
                'POST',
                'https://prod.rewardsplatform.microsoft.com/dapi/me/activities',
                headers,
                data=json.dumps(payload), account_index=account_index
            )
            
            if response.status_code == 200:
                # print_log("阅读提交", "文章阅读提交成功", account_index)
                return True
            else:
                print_log("阅读提交", f"文章阅读提交失败，状态码: {response.status_code}", account_index)
                return False
                
        except Exception as e:
            if hasattr(e, 'response') and e.response:
                try:
                    error_data = e.response.json()
                    if (error_data.get('error', {}).get('description', '').find('already') != -1):
                        print_log("阅读提交", "文章阅读任务已完成", account_index)
                        return True
                except:
                    pass
            
            print_log("阅读提交", f"文章阅读提交异常: {e}", account_index)
            return False
    
    def complete_read_tasks(self, refresh_token: str, account_alias: str = "", account_index: Optional[int] = None) -> int:
        """完成阅读任务 - 支持令牌缓存"""
        if not refresh_token:
            print_log("阅读任务", "未提供刷新令牌，跳过阅读任务", account_index)
            return 0
        
        try:
            # 获取访问令牌（支持令牌自动更新）
            access_token = self.get_access_token(refresh_token, account_alias, account_index)
            if not access_token:
                print_log("阅读任务", "无法获取访问令牌，跳过阅读任务", account_index)
                return 0
            
            # 获取阅读进度
            try:
                progress_data = self.get_read_progress(access_token, account_index)
                max_reads = progress_data['max']
                current_progress = progress_data['progress']
            except Exception as e:
                print_log("阅读任务", f"获取阅读进度失败: {e}，跳过阅读任务", account_index)
                return 0
            
            
            if current_progress >= max_reads:
                # print_log("阅读任务", "阅读任务已完成", account_index)
                return current_progress
            else:
                print_log("阅读任务", f"当前阅读进度: {current_progress}/{max_reads}", account_index)

            # 执行阅读任务
            read_attempts = 0
            max_attempts = max_reads - current_progress
            
            for i in range(max_attempts):
                print_log("阅读任务", f"执行第 {i + 1} 次阅读任务", account_index)
                
                if self.submit_read_activity(access_token, account_index):
                    read_attempts += 1
                    
                    # 延迟一段时间
                    delay = random.uniform(5, 10)
                    print_log("阅读任务", f"阅读任务提交成功，等待 {delay:.1f} 秒", account_index)
                    time.sleep(delay)
                    
                    # 再次检查进度
                    try:
                        progress_data = self.get_read_progress(access_token, account_index)
                        new_progress = progress_data['progress']
                    except Exception as e:
                        print_log("阅读任务", f"重新获取进度失败: {e}，继续执行", account_index)
                        # 如果重新获取进度失败，继续执行但不更新进度
                        continue
                    
                    if new_progress > current_progress:
                        current_progress = new_progress
                        print_log("阅读任务", f"阅读进度更新: {current_progress}/{max_reads}", account_index)
                        
                        if current_progress >= max_reads:
                            # print_log("阅读任务", "所有阅读任务已完成", account_index)
                            break
                else:
                    print_log("阅读任务", f"第 {i + 1} 次阅读任务提交失败", account_index)
                    time.sleep(random.uniform(2, 5))
            
            print_log("阅读任务", f"阅读任务执行完成，最终进度: {current_progress}/{max_reads}", account_index)
            return current_progress
            
        except Exception as e:
            print_log("阅读任务", f"阅读任务执行异常: {e}", account_index)
            return 0

    # ==================== 6. 活动任务相关方法 ====================
    def complete_daily_set_tasks(self, cookies: str, token: str, account_index: Optional[int] = None) -> int:
        """完成每日活动任务"""
        completed_count = 0
        try:
            # 获取dashboard数据
            dashboard_data = self.get_dashboard_data(cookies, account_index)
            if not dashboard_data:
                return completed_count
            
            # 提取每日任务
            today_str = date.today().strftime('%m/%d/%Y')
            dashboard = dashboard_data.get('dashboard', {})
            if not dashboard:
                return completed_count
            daily_set_promotions = dashboard.get('dailySetPromotions', {})
            if not daily_set_promotions:
                daily_set_promotions = {}
            daily_tasks = daily_set_promotions.get(today_str, [])
            
            if not daily_tasks:
                # 检查是否所有任务都已完成
                dashboard = dashboard_data.get('dashboard', {})
                if dashboard:
                    all_daily_promotions = dashboard.get('dailySetPromotions', {})
                    if all_daily_promotions and today_str in all_daily_promotions:
                        # 有任务数据但为空，说明可能已完成或其他原因
                        pass  # 不输出"没有找到任务"的日志，让状态检查方法处理
                    else:
                        print_log("每日活动", "没有找到今日的每日活动任务", account_index)
                return completed_count
            
            # 过滤未完成的任务
            incomplete_tasks = [task for task in daily_tasks if not task.get('complete')]
            
            if not incomplete_tasks:
                return completed_count
            
            print_log("每日活动", f"找到 {len(incomplete_tasks)} 个未完成的每日活动任务", account_index)
            
            # 执行任务
            for i, task in enumerate(incomplete_tasks, 1):
                print_log("每日活动", f"⏳ 执行任务 {i}/{len(incomplete_tasks)}: {task.get('title', '未知任务')}", account_index)
                
                if self._execute_task(task, token, cookies, account_index):
                    completed_count += 1
                    print_log("每日活动", f"✅ 任务完成: {task.get('title', '未知任务')}", account_index)
                else:
                    print_log("每日活动", f"❌ 任务失败: {task.get('title', '未知任务')}", account_index)
                
                # 随机延迟
                time.sleep(random.uniform(config.TASK_DELAY_MIN, config.TASK_DELAY_MAX))
            
            # print_log("每日活动", f"每日活动执行完成，成功完成 {completed_count} 个任务", account_index)
            
        except Exception as e:
            print_log('每日活动出错', f"异常: {e}", account_index)
        
        return completed_count

    def get_daily_tasks_status(self, cookies: str, account_index: Optional[int] = None) -> tuple:
        """获取每日活动任务状态"""
        try:
            # 获取dashboard数据
            dashboard_data = self.get_dashboard_data(cookies, account_index)
            if not dashboard_data:
                return 0, 0
            
            # 提取每日任务
            today_str = date.today().strftime('%m/%d/%Y')
            dashboard = dashboard_data.get('dashboard', {})
            if not dashboard:
                return 0, 0
            daily_set_promotions = dashboard.get('dailySetPromotions', {})
            if not daily_set_promotions:
                daily_set_promotions = {}
            daily_tasks = daily_set_promotions.get(today_str, [])
            
            if not daily_tasks:
                return 0, 0
            
            # 统计已完成和总任务数
            total_tasks = len(daily_tasks)
            completed_tasks = len([task for task in daily_tasks if task.get('complete')])
            
            return completed_tasks, total_tasks
            
        except Exception as e:
            print_log('每日活动状态获取出错', f"异常: {e}", account_index)
            return 0, 0

    def complete_more_activities_with_filtering(self, cookies: str, token: str, account_index: Optional[int] = None) -> int:
        """完成更多活动任务（带智能筛选）"""
        try:
            # 获取dashboard数据
            dashboard_data = self.get_dashboard_data(cookies, account_index)
            if not dashboard_data:
                print_log("更多活动", "无法获取dashboard数据，跳过更多活动", account_index)
                return 0
            
            # 提取更多活动任务（已内置筛选逻辑）
            dashboard = dashboard_data.get('dashboard', {})
            if not dashboard:
                return 0
            
            # 获取morePromotions和promotionalItems两个数组
            more_promotions = dashboard.get('morePromotions', [])
            promotional_items = dashboard.get('promotionalItems', [])
            
            # 合并两个数组并提取任务
            all_promotions = more_promotions + promotional_items
            valuable_tasks = self._extract_tasks(all_promotions)
            
            if not valuable_tasks:
                return 0
            
            print_log("更多活动", f"找到 {len(valuable_tasks)} 个有价值的更多活动任务", account_index)
            
            # 执行筛选后的任务
            completed_count = 0
            for i, task in enumerate(valuable_tasks, 1):
                print_log("更多活动", f"⏳ 执行任务 {i}/{len(valuable_tasks)}: {task.get('title', '未知任务')}", account_index)
                
                if self._execute_task(task, token, cookies, account_index):
                    completed_count += 1
                    print_log("更多活动", f"✅ 任务完成: {task.get('title', '未知任务')}", account_index)
                else:
                    print_log("更多活动", f"❌ 任务失败: {task.get('title', '未知任务')}", account_index)
                
                # 随机延迟
                time.sleep(random.uniform(config.TASK_DELAY_MIN, config.TASK_DELAY_MAX))
            
            return completed_count
            
        except Exception as e:
            print_log("更多活动出错", f"异常: {e}", account_index)
            return 0

    def get_more_activities_status(self, cookies: str, account_index: Optional[int] = None) -> tuple:
        """获取更多活动任务状态"""
        try:
            # 获取dashboard数据
            dashboard_data = self.get_dashboard_data(cookies, account_index)
            if not dashboard_data:
                return 0, 0
            
            # 提取更多活动任务
            dashboard = dashboard_data.get('dashboard', {})
            if not dashboard:
                return 0, 0
            
            # 获取morePromotions和promotionalItems两个数组
            more_promotions = dashboard.get('morePromotions', [])
            promotional_items = dashboard.get('promotionalItems', [])
            
            # 合并两个数组
            all_promotions = more_promotions + promotional_items
            if not all_promotions:
                return 0, 0
            
            # 统计所有有价值任务（包括已完成和未完成的）
            valuable_tasks = []
            completed_count = 0
            
            for promotion in all_promotions:
                complete = promotion.get('complete')
                priority = promotion.get('priority')
                attributes = promotion.get('attributes', {})
                is_unlocked = attributes.get('is_unlocked')
                max_points = promotion.get('pointProgressMax', 0)
                
                # 跳过没有积分奖励的任务
                if max_points <= 0:
                    continue
                
                # 跳过明确被锁定的任务
                if is_unlocked == 'False':
                    continue
                
                # 统计所有有积分奖励且未明确锁定的任务
                # 优先级检查：-30到7都是有效优先级，None值视为无效
                if priority is not None and -30 <= priority <= 7:
                    valuable_tasks.append(promotion)
                    if complete:  # 已完成的有价值任务
                        completed_count += 1
            
            total_valuable_tasks = len(valuable_tasks)
            
            return completed_count, total_valuable_tasks
            
        except Exception as e:
            print_log('更多活动状态获取出错', f"异常: {e}", account_index)
            return 0, 0

    # ==================== 7. 内部辅助方法 ====================
    def _extract_tasks(self, more_promotions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """提取任务"""
        tasks = []
        for promotion in more_promotions:
            complete = promotion.get('complete')
            priority = promotion.get('priority')
            attributes = promotion.get('attributes', {})
            is_unlocked = attributes.get('is_unlocked')
            
            # 任务必须未完成
            if complete == False:
                # 严格检查解锁状态，排除明确被锁定的任务
                if is_unlocked == 'False':
                    continue  # 跳过明确被锁定的任务
                
                # 跳过没有积分奖励的任务
                max_points = promotion.get('pointProgressMax', 0)
                if max_points <= 0:
                    continue
                
                # 只执行解锁的任务或解锁状态未知但优先级合适的任务
                if (priority is not None and -30 <= priority <= 7 and (is_unlocked == 'True' or is_unlocked is None)):
                    tasks.append(promotion)
        return tasks

    def _execute_task(self, task: Dict[str, Any], token: str, cookies: str, account_index: Optional[int] = None) -> bool:
        """执行单个任务"""
        try:
            destination_url = task.get('destinationUrl') or task.get('attributes', {}).get('destination')
            if not destination_url:
                print_log("任务执行", f"❌ 任务 {task.get('name')} 没有目标URL", account_index)
                return False
            
            # 设置任务执行请求头
            headers = {
                'User-Agent': config.get_random_pc_ua(),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'Cookie': cookies
            }
            
            # 发送请求
            response = self.request_manager.make_request('GET', destination_url, headers, timeout=config.REQUEST_TIMEOUT, account_index=account_index)
            
            if response.status_code == 200:
                # # 添加延时，让系统有时间更新任务状态
                # delay_time = random.uniform(7, 10)
                # # print_log("任务执行", f"⏳ 任务访问成功，等待 {delay_time:.1f} 秒让系统更新状态...", account_index)
                # time.sleep(delay_time)
                
                # 报告活动
                if self._report_activity(task, token, cookies, account_index):
                    return True
                else:
                    print_log("任务执行", f"⚠️ 任务执行成功但活动报告失败", account_index)
                    return False
            else:
                print_log("任务执行", f"❌ 任务执行失败，状态码: {response.status_code}", account_index)
                return False
                
        except Exception as e:
            print_log("任务执行", f"❌ 执行任务时出错: {e}", account_index)
            return False

    def _report_activity(self, task: Dict[str, Any], token: str, cookies: str, account_index: Optional[int] = None) -> bool:
        """报告任务活动，真正完成任务"""
        if not token:
            print_log("活动报告", "❌ 缺少token", account_index)
            return False
        
        try:
            post_url = 'https://rewards.bing.com/api/reportactivity?X-Requested-With=XMLHttpRequest'
            post_headers = {
                'User-Agent': config.get_random_pc_ua(),
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'X-Requested-With': 'XMLHttpRequest',
                'Origin': 'https://rewards.bing.com',
                'Referer': 'https://rewards.bing.com/',
                'Cookie': cookies
            }
            payload = f"id={task.get('offerId', task.get('name'))}&hash={task.get('hash', '')}&timeZone=480&activityAmount=1&dbs=0&form=&type=&__RequestVerificationToken={token}"
            response = self.request_manager.make_request('POST', post_url, post_headers, data=payload, timeout=config.REQUEST_TIMEOUT, account_index=account_index)
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    # print_log("活动报告", f"API响应: {result}", account_index)  # 添加详细日志
                    if result.get("activity") and result["activity"].get("points", 0) >= 0:
                        print_log("任务奖励", f"✅ 获得{result['activity']['points']}积分", account_index)
                        return True
                    else:
                        print_log("活动报告", f"❌ 响应中没有积分信息: {result}", account_index)
                        return False
                except json.JSONDecodeError as e:
                    print_log("活动报告", f"❌ JSON解析失败: {e}, 响应内容: {response.text}", account_index)
                    return False
            else:
                print_log("活动报告", f"❌ API状态码: {response.status_code}, 响应: {response.text}", account_index)
                return False
        except Exception as e:
            print_log("活动报告", f"❌ 异常: {e}", account_index)
            return False

    # ==================== 8. 通知方法 ====================
    def _send_cookie_invalid_notification(self, account_index: Optional[int] = None):
        """发送Cookie失效的独立通知"""
        try:
            self.notification_manager.send_cookie_invalid(account_index)
            print_log("Cookie通知", f"已发送账号{account_index}的Cookie失效通知", account_index)
        except Exception as e:
            print_log("Cookie通知", f"发送Cookie失效通知失败: {e}", account_index)
    
    def _send_token_invalid_notification(self, account_index: Optional[int] = None):
        """发送刷新令牌失效的独立通知"""
        try:
            title = f"🚨 Microsoft Rewards 刷新令牌失效警告"
            content = f"账号{account_index} 的刷新令牌已失效，阅读任务无法执行！\n\n"
            content += f"失效时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            content += f"需要处理: 重新获取账号{account_index}的刷新令牌\n\n"
            content += f"刷新令牌获取步骤:\n"
            content += f"1. 安装 <Bing Rewards 自动获取刷新令牌> 油猴脚本\n"
            content += f"2. 访问 https://login.live.com/oauth20_authorize.srf?client_id=0000000040170455&scope=service::prod.rewardsplatform.microsoft.com::MBI_SSL&response_type=code&redirect_uri=https://login.live.com/oauth20_desktop.srf\n"
            content += f"3. 登录后，使用 <Bing Rewards 自动获取刷新令牌> 油猴脚本，自动获取刷新令牌\n"
            content += f"4. 更新环境变量 bing_token_{account_index} 为获取到的刷新令牌\n"
            content += f"5. 重新运行脚本\n"
            self.notification_manager.send(title, content)
            print_log("令牌通知", f"已发送账号{account_index}的刷新令牌失效通知", account_index)
        except Exception as e:
            print_log("令牌通知", f"发送刷新令牌失效通知失败: {e}", account_index)
    
    def get_today_earned_points(self, dashboard_data: Dict[str, Any], account_index: Optional[int] = None) -> int:
        """从dashboard数据中获取今日总共获得的积分"""
        if not dashboard_data:
            return 0
        
        # 尝试从不同位置获取pointsSummary
        points_summary = None
        
        # 如果根级别没有，尝试从status获取
        if not points_summary:
            status = dashboard_data.get('status', {})
            if status and 'pointsSummary' in status:
                points_summary = status.get('pointsSummary', [])
        
        if not points_summary:
            return 0
        
        # 获取今天是周几 (0=周日, 1=周一, ..., 6=周六)
        import datetime
        today_weekday = datetime.datetime.now().weekday()
        # Python的weekday(): 0=周一, 6=周日
        # API的dayOfWeek: 0=周日, 1=周一, ..., 6=周六
        api_today = (today_weekday + 1) % 7
        
        # 查找今日的积分记录
        for day_record in points_summary:
            if day_record.get('dayOfWeek') == api_today:
                return day_record.get('pointsEarned', 0)
        
        return 0

# ==================== 主程序类 ====================
class RewardsBot:
    """Microsoft Rewards 自动化机器人主类 - 多账号分离版本"""
    
    def __init__(self):
        self.accounts = AccountManager.get_accounts()
        
        if not self.accounts:
            print_log("启动错误", "没有检测到任何账号配置，程序退出")
            print_log("配置提示", "请设置环境变量: bing_ck_1, bing_ck_2... 和可选的 bing_token_1, bing_token_2...")
            exit(1)
        
        # 检查是否应该跳过执行（在获取账号后检查，避免在账号配置错误时也跳过）
        current_complete_count = global_cache_manager.get_tasks_complete_count()
        
        # 强制检查计数是否超过设定次数
        if current_complete_count >= TASK_CONFIG['MAX_REPEAT_COUNT']:
            print_log("脚本跳过", f"已重复运行{current_complete_count}次，跳过执行")
            exit(0)
        elif current_complete_count > 0:
            print_log("系统提示", f"已重复运行{current_complete_count}/{TASK_CONFIG['MAX_REPEAT_COUNT']}次", None)
        
        print_log("初始化", f"检测到 {len(self.accounts)} 个账号，即将开始...")
        
        # 统计有效刷新令牌数量
        valid_tokens = sum(1 for account in self.accounts if account.refresh_token)
        if valid_tokens > 0:
            print_log("初始化", f"检测到 {valid_tokens} 个令牌，启用APP阅读...")

    def _calculate_required_searches(self, dashboard_data: Dict[str, Any], search_type: str) -> int:
        """根据dashboard数据精确计算需要的搜索次数"""
        if not dashboard_data:
            return 0
        
        dashboard = dashboard_data.get('dashboard', {})
        user_status = dashboard.get('userStatus', {})
        counters = user_status.get('counters', {})
        search_tasks = counters.get(search_type, [])
        
        if not search_tasks:
            return 0
        
        task = search_tasks[0]  # 通常只有一个搜索任务
        if task.get('complete', False):
            return 0
        
        max_points = task.get('pointProgressMax', 0)
        current_points = task.get('pointProgress', 0)
        points_needed = max_points - current_points
        
        # 每次搜索3积分，但从第3次搜索开始计分
        if points_needed <= 0:
            return 0
        
        # 计算需要的搜索次数（向上取整）
        searches_needed = (points_needed + 2) // 3  # +2是为了向上取整
        return max(0, searches_needed)

    def _get_account_level_details(self, dashboard_data: Dict[str, Any]) -> Dict[str, Any]:
        """获取详细的账号等级信息"""
        if not dashboard_data:
            return {'level': 'Level1', 'name': '一级', 'progress': 0, 'max': 0}
        
        dashboard = dashboard_data.get('dashboard', {})
        user_status = dashboard.get('userStatus', {})
        level_info = user_status.get('levelInfo', {})
        
        # 确保level_info不为None
        if not level_info:
            return {'level': 'Level1', 'name': '一级', 'progress': 0, 'max': 0}
        
        return {
            'level': level_info.get('activeLevel', 'Level1'),
            'name': level_info.get('activeLevelName', '一级'),
            'progress': level_info.get('progress', 0),
            'max': level_info.get('progressMax', 0),
            'last_month_level': level_info.get('lastMonthLevel', 'Level1')
        }

    def process_single_account(self, account: AccountInfo, service: RewardsService, stop_event: threading.Event) -> Optional[str]:
        """处理单个账号的完整流程"""
        try:
            account_index = account.index
            cookies = account.cookies
            
            # 获取账号信息
            initial_data = service.get_rewards_points(cookies, account_index)
            if not initial_data:
                print_log("账号处理", "获取账号信息失败，跳过此账号", account_index)
                return None
            
            email = initial_data.get('email', '未知邮箱')
            token = initial_data.get('token')
            current_points = initial_data['points']  # 当前即时积分
            

            
            logger.account_start(email, current_points, account_index)

            # 执行阅读任务
            read_completed = 0
            if account.refresh_token:
                read_completed = service.complete_read_tasks(account.refresh_token, account.alias, account_index)
                logger.success("阅读任务", f"已完成 ({read_completed}/30)", account_index)
            else:
                logger.skip("阅读任务", "未配置刷新令牌", account_index)

            # 初始化变量，避免未定义错误
            daily_completed = 0
            daily_total = 0
            more_completed = 0
            more_total = 0

            # 执行每日任务
            if token:
                # 先执行任务
                new_daily_completed = service.complete_daily_set_tasks(cookies, token, account_index)
                # 然后获取总的完成状态
                daily_completed, daily_total = service.get_daily_tasks_status(cookies, account_index)
                logger.success("每日活动", f"已完成 ({daily_completed}/{daily_total})", account_index)
            else:
                logger.skip("每日活动", "无法获取token", account_index)
            
            # 执行更多任务
            if token:
                # 先执行任务
                new_more_completed = service.complete_more_activities_with_filtering(cookies, token, account_index)
                # 然后获取总的完成状态
                more_completed, more_total = service.get_more_activities_status(cookies, account_index)
                logger.success("更多活动", f"已完成 ({more_completed}/{more_total})", account_index)
            else:
                logger.skip("更多活动", "无法获取token", account_index)
            

            
            # 执行搜索任务
            self._perform_search_tasks(cookies, account_index, email, service, stop_event)
            
            # 获取最终积分
            final_data = service.get_rewards_points(cookies, account_index)
            if final_data and final_data['points'] is not None:
                final_points = final_data['points']
                
                # 获取dashboard数据来显示今日总积分
                final_dashboard_data = service.get_dashboard_data(cookies, account_index)
                today_total_earned = service.get_today_earned_points(final_dashboard_data, account_index) if final_dashboard_data else 0
                
                # 使用新的日志格式：任务完成 + 今日积分
                self._log_account_complete(final_points, today_total_earned, account_index)
                
                # 生成详细的任务摘要
                summary = self._format_account_summary(
                    email, current_points, final_points, 
                    daily_completed, more_completed, read_completed, account_index, cookies, account, service,
                    today_total_earned
                )
                return summary
            else:
                print_log("脚本完成", "无法获取最终积分", account_index)
                return None
        
        except SystemExit:
            # 搜索任务未完成，线程被终止
            #print_log("账号处理", f"搜索任务未完成，账号处理被终止", account_index)
            return None
        except Exception as e:
            error_details = traceback.format_exc()
            print_log("账号处理错误", f"处理账号时发生异常: {e}", account_index)
            print_log("错误详情", f"详细错误信息: {error_details}", account_index)
            return None
    
    def _perform_search_tasks(self, cookies: str, account_index: int, email: str, service: RewardsService, stop_event: threading.Event):
        """执行搜索任务"""
        
        # 获取初始dashboard数据检查任务状态
        dashboard_data = service.get_dashboard_data(cookies, account_index)
        
        # 获取账号等级
        account_level = service.get_account_level(dashboard_data)
        # print_log("账号等级", f"当前账号等级: {account_level}", account_index)
        
        # 电脑搜索
        if dashboard_data:
            # 获取搜索状态
            pc_current, pc_max = self._get_search_status(dashboard_data, 'pcSearch')
            
            # 使用双重检查确保准确性
            is_complete_by_flag = service.is_pc_search_complete(dashboard_data)
            is_complete_by_progress = pc_current >= pc_max and pc_max > 0
            
            if is_complete_by_flag or is_complete_by_progress:
                # 任务已完成
                logger.success("电脑搜索", f"已完成 ({pc_current}/{pc_max})", account_index)
            else:
                # 任务确实未完成，开始执行搜索
                required_searches = self._calculate_required_searches(dashboard_data, 'pcSearch')
                logger.search_start("电脑", required_searches, config.SEARCH_CHECK_INTERVAL, account_index)
                
                # 记录初始进度
                last_progress = self._get_search_progress_sum(dashboard_data, 'pcSearch')
                
                # 执行搜索，如果任务完成则提前终止
                count = 0
                for i in range(config.SEARCH_CHECK_INTERVAL):
                    count += 1
                    if service.perform_pc_search(cookies, account_index, email):
                        delay = random.randint(config.SEARCH_DELAY_MIN, config.SEARCH_DELAY_MAX)
                        logger.search_progress("电脑", i+1, config.SEARCH_CHECK_INTERVAL, delay, account_index)
                        time.sleep(delay)
                    else:
                        print_log("电脑搜索", f"第{i+1}次搜索失败", account_index)
                    
                    # 每次搜索后检查进度（静默模式，避免错误日志干扰）
                    dashboard_data = service.get_dashboard_data(cookies, account_index, silent=True)
                    current_progress = self._get_search_progress_sum(dashboard_data, 'pcSearch') if dashboard_data else last_progress
                    
                    # 第6次搜索完成后输出进度变化
                    if count == config.SEARCH_CHECK_INTERVAL:
                        logger.search_progress_summary("电脑", count, last_progress, current_progress, account_index)
                    
                    # 检查任务是否完成，如果完成则提前终止
                    if dashboard_data and service.is_pc_search_complete(dashboard_data):
                        logger.search_complete("电脑", i+1, account_index, True)
                        break
                
                # 如果循环正常结束（没有break），检查任务是否真正完成
                else:
                    if dashboard_data and not service.is_pc_search_complete(dashboard_data):
                        # print_log("电脑搜索", f"执行完{config.SEARCH_CHECK_INTERVAL}次搜索后任务未完成，停止线程", account_index)
                        stop_event.set()
                        raise SystemExit()
        else:
            logger.warning("电脑搜索", "无法获取状态", account_index)
        
        # 移动搜索 - 只有非1级账号才执行
        if account_level != "Level1":
            # 重新获取dashboard数据，因为电脑搜索可能已经改变了状态
            dashboard_data = service.get_dashboard_data(cookies, account_index)
            
            if dashboard_data:
                # 获取搜索状态
                mobile_current, mobile_max = self._get_search_status(dashboard_data, 'mobileSearch')
                
                # 使用双重检查确保准确性
                is_complete_by_flag = service.is_mobile_search_complete(dashboard_data)
                is_complete_by_progress = mobile_current >= mobile_max and mobile_max > 0
                
                if is_complete_by_flag or is_complete_by_progress:
                    # 任务已完成
                    logger.success("移动搜索", f"已完成 ({mobile_current}/{mobile_max})", account_index)
                else:
                    # 任务确实未完成，开始执行搜索
                    required_searches = self._calculate_required_searches(dashboard_data, 'mobileSearch')
                    logger.search_start("移动", required_searches, config.SEARCH_CHECK_INTERVAL, account_index)
                    
                    # 执行搜索逻辑
                    last_progress = self._get_search_progress_sum(dashboard_data, 'mobileSearch')
                    count = 0
                    for i in range(config.SEARCH_CHECK_INTERVAL):
                        count += 1
                        if service.perform_mobile_search(cookies, account_index, email):
                            delay = random.randint(config.SEARCH_DELAY_MIN, config.SEARCH_DELAY_MAX)
                            logger.search_progress("移动", i+1, config.SEARCH_CHECK_INTERVAL, delay, account_index)
                            time.sleep(delay)
                        else:
                            print_log("移动搜索", f"第{i+1}次搜索失败", account_index)
                        
                        # 检查进度
                        dashboard_data = service.get_dashboard_data(cookies, account_index, silent=True)
                        current_progress = self._get_search_progress_sum(dashboard_data, 'mobileSearch') if dashboard_data else last_progress
                        
                        if count == config.SEARCH_CHECK_INTERVAL:
                            logger.search_progress_summary("移动", count, last_progress, current_progress, account_index)
                        
                        # 检查是否完成
                        if dashboard_data and service.is_mobile_search_complete(dashboard_data):
                            logger.search_complete("移动", i+1, account_index, True)
                            break
                    else:
                        # 循环结束但任务未完成
                        if dashboard_data and not service.is_mobile_search_complete(dashboard_data):
                            stop_event.set()
                            raise SystemExit()
            else:
                logger.warning("移动搜索", "无法获取状态", account_index)
        else:
            logger.search_skip("移动", "1级账号无此任务", account_index)

    def _get_search_progress_sum(self, dashboard_data: Dict[str, Any], search_type: str) -> int:
        """获取搜索进度总和"""
        if not dashboard_data:
            return 0
        dashboard = dashboard_data.get('dashboard', {})
        user_status = dashboard.get('userStatus', {})
        counters = user_status.get('counters', {})
        search_tasks = counters.get(search_type, [])
        return sum(task.get('pointProgress', 0) for task in search_tasks)
    
    def _get_search_progress_max(self, dashboard_data: Dict[str, Any], search_type: str) -> int:
        """获取搜索进度最大值"""
        if not dashboard_data:
            return 0
        dashboard = dashboard_data.get('dashboard', {})
        user_status = dashboard.get('userStatus', {})
        counters = user_status.get('counters', {})
        search_tasks = counters.get(search_type, [])
        return sum(task.get('pointProgressMax', 0) for task in search_tasks)
    
    def _get_search_status(self, dashboard_data: Dict[str, Any], search_type: str) -> tuple:
        """获取搜索状态 (当前进度, 最大值)"""
        current = self._get_search_progress_sum(dashboard_data, search_type)
        maximum = self._get_search_progress_max(dashboard_data, search_type)
        return current, maximum
    
    def _log_account_complete(self, final_points: int, today_earned: int, account_index: int):
        """记录账号任务完成日志"""
        msg = f"{final_points} ({today_earned})"
        logger._log(2, "🎉", "任务完成", msg, account_index)  # 2 = LogLevel.SUCCESS

    def _format_account_summary(self, email: str, start_points: int, final_points: int, 
                               daily_completed: int, more_completed: int, read_completed: int, 
                               account_index: int, cookies: str, account: AccountInfo, service: RewardsService,
                               today_total_earned: int = 0) -> str:
        """格式化账号摘要"""
        lines = [
            f"账号{account_index} - {email}",
            f"📊当前积分: {final_points} ({today_total_earned})"
        ]
        
        # 获取dashboard数据
        try:
            dashboard_data = service.get_dashboard_data(cookies, account_index)
            if dashboard_data and dashboard_data.get('dashboard'):
                dashboard = dashboard_data.get('dashboard', {})
                user_status = dashboard.get('userStatus', {})
                counters = user_status.get('counters', {})
                
                # 每日活动统计
                today_str = date.today().strftime('%m/%d/%Y')
                daily_set_promotions = dashboard.get('dailySetPromotions', {})
                if not daily_set_promotions:
                    daily_set_promotions = {}
                daily_tasks = daily_set_promotions.get(today_str, [])
                daily_completed_count = 0
                daily_total_count = 0
                if daily_tasks:
                    daily_completed_count = sum(1 for task in daily_tasks if task.get('complete'))
                    daily_total_count = len(daily_tasks)
                lines.append(f"📅每日活动: {daily_completed_count}/{daily_total_count}")
                
                # 更多活动统计 - 使用与日志相同的筛选逻辑
                more_tasks = dashboard.get('morePromotions', [])
                if not more_tasks:
                    more_tasks = []
                
                more_completed_count = 0
                more_total_count = 0
                if more_tasks:
                    for task in more_tasks:
                        complete = task.get('complete')
                        priority = task.get('priority')
                        attributes = task.get('attributes', {})
                        is_unlocked = attributes.get('is_unlocked')
                        max_points = task.get('pointProgressMax', 0)
                        
                        # 跳过没有积分奖励的任务
                        if max_points <= 0:
                            continue
                        
                        # 跳过明确被锁定的任务
                        if is_unlocked == 'False':
                            continue
                        
                        # 统计所有有积分奖励且未明确锁定的任务
                        # 优先级检查：-1到7都是有效优先级，None值视为无效
                        if priority is not None and -30 <= priority <= 7:
                            more_total_count += 1
                            if complete:  # 已完成的有价值任务
                                more_completed_count += 1
                lines.append(f"🎯更多活动: {more_completed_count}/{more_total_count}")
                
                # 阅读任务进度 - 获取真实进度，但避免重复缓存
                read_progress_text = f"📖阅读任务: {read_completed}/30"
                if account.refresh_token:
                    try:
                        # 静默获取access_token，不触发缓存
                        access_token = service.get_access_token(account.refresh_token, account.alias, account_index, silent=True)
                        if access_token:
                            progress_data = service.get_read_progress(access_token, account_index)
                            if progress_data and isinstance(progress_data, dict):
                                read_progress_text = f"📖阅读任务: {progress_data.get('progress', 0)}/{progress_data.get('max', 3)}"
                    except:
                        pass  # 如果获取失败，使用默认格式
                lines.append(read_progress_text)

                # 搜索任务进度
                # 获取详细账号等级信息
                level_details = self._get_account_level_details(dashboard_data)
                account_level = level_details.get('level', 'Level1') if level_details else 'Level1'
                
                # 电脑搜索进度
                pc_search_tasks = counters.get("pcSearch", [])
                if pc_search_tasks:
                    for task in pc_search_tasks:
                        if task:  # 确保task不为None
                            title = task.get('title', "电脑搜索")
                            progress = f"{task.get('pointProgress', 0)}/{task.get('pointProgressMax', 0)}"
                            lines.append(f"💻电脑搜索: {progress}")
                else:
                    lines.append("💻电脑搜索: 无数据")
                
                # 移动搜索进度 - 只有非1级账号才显示
                if account_level != "Level1":
                    mobile_search_tasks = counters.get("mobileSearch", [])
                    if mobile_search_tasks:
                        for task in mobile_search_tasks:
                            if task:  # 确保task不为None
                                title = task.get('title', "移动搜索")
                                progress = f"{task.get('pointProgress', 0)}/{task.get('pointProgressMax', 0)}"
                                lines.append(f"📱移动搜索: {progress}")
                    else:
                        lines.append("📱移动搜索: 无数据")
                else:
                    lines.append("📱移动搜索: 1级账号无此任务")
            else:
                # 如果无法获取dashboard数据，使用简化格式
                lines.extend([
                    f"📅每日活动: 完成 {daily_completed} 个任务",
                    f"🎯更多活动: 完成 {more_completed} 个任务",
                    f"📖阅读任务: 完成 {read_completed} 个任务",
                    f"🔍搜索任务: 电脑搜索和移动搜索已执行"
                ])
        except Exception as e:
            # 异常情况下使用简化格式
            lines.extend([
                f"📅每日活动: 完成 {daily_completed} 个任务",
                f"🎯更多活动: 完成 {more_completed} 个任务",
                f"📖阅读任务: 完成 {read_completed} 个任务",
                f"🔍搜索任务: 电脑搜索和移动搜索已执行"
            ])
        
        return '\n'.join(lines)
    
    def run(self):
        """运行主程序"""
        account_summaries = {}  # 使用字典保存账号摘要，key为账号索引
        threads = []
        summaries_lock = threading.Lock()
        # 为每个线程创建独立的停止事件，避免全局共享
        thread_stop_events = {}
        
        def thread_worker(account: AccountInfo):
            # 为每个线程创建独立的RewardsService实例，避免共享状态
            service = RewardsService()
            # 为每个线程创建独立的停止事件
            thread_stop_events[account.index] = threading.Event()
            try:
                summary = self.process_single_account(account, service, thread_stop_events[account.index])
                if summary:
                    with summaries_lock:
                        account_summaries[account.index] = summary
            except SystemExit:
                # 搜索任务失败导致的线程终止，不记录为错误
                pass
            except Exception as e:
                print_log(f"账号{account.index}错误", f"处理账号时发生异常: {e}", account.index)
            finally:
                # 确保Service实例被正确清理
                if hasattr(service, 'request_manager'):
                    service.request_manager.close()
        
        # 启动所有账号的处理线程
        for account in self.accounts:
            t = threading.Thread(target=thread_worker, args=(account,))
            threads.append(t)
            t.start()
        
        # 等待所有线程完成
        for t in threads:
            t.join()
        
        # 按账号索引排序并转换为列表
        sorted_summaries = []
        if account_summaries:
            # 按账号索引排序
            for account_index in sorted(account_summaries.keys()):
                sorted_summaries.append(account_summaries[account_index])
        
        # 检查是否有线程因搜索失败而停止
        any_search_failed = any(event.is_set() for event in thread_stop_events.values())
        
        # 推送结果
        self._send_notification(sorted_summaries, any_search_failed)
    
    def _send_notification(self, summaries: List[str], any_search_failed: bool):
        """发送通知"""
        if any_search_failed:
            print(f"\n\n{'='*17} [任务未全部完成] {'='*17}")
            print_log(f"系统提示", f"搜索任务未全部完成")
            print_log(f"系统提示", f"建议每 30+ 分钟重新运行一次")
            print_log(f"统一推送", "任务未全部完成，取消推送")
            print(f"{'='*17} [任务未全部完成] {'='*17}")
            return
        else:   
            print(f"\n\n{'='*17} [全部任务完成] {'='*17}")
            
            # 增加任务完成计数
            global_cache_manager.increment_tasks_complete_count()
            
            if summaries:
                content = "\n\n".join(summaries)
                
                if global_cache_manager.has_pushed_today():
                    print_log("统一推送", "今天已经推送过，取消本次推送。")
                else:
                    print_log("统一推送", "准备发送所有账号的总结报告...")
                    try:
                        title = f"Microsoft Rewards 任务总结 ({date.today().strftime('%Y-%m-%d')})"
                        global_notification_manager.send(title, content)
                        print_log("推送成功", "总结报告已发送。")
                        global_cache_manager.mark_pushed_today()
                    except Exception as e:
                        print_log("推送失败", f"发送总结报告时出错: {e}")
            else:
                print_log("统一推送", "没有可供推送的账号信息。")
                return
            
            # 无论是否推送，都在日志末尾打印内容摘要
            print(f"{'='*17} [全部任务完成] {'='*17}")

# ==================== 主程序入口 ====================
def main():
    """主程序入口"""
    try:
        bot = RewardsBot()
        bot.run()
    except KeyboardInterrupt:
        print_log("程序中断", "用户中断程序执行")
    except Exception as e:
        print_log("程序错误", f"程序执行出错: {e}")

if __name__ == "__main__":
    main() 