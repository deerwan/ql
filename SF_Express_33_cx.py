"""
顺丰33周年活动 - 奖品查询
查询所有账号的周年活动奖品，统计高价值奖品
"""
# 扫码获取ck地址：https://sm.9999.blue/
import hashlib
import os
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from urllib.parse import unquote
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# ==================== 配置常量 ====================
PROXY_TIMEOUT = 15
MAX_PROXY_RETRIES = 5
CONCURRENT_NUM = int(os.getenv('SFBF', '1'))
if CONCURRENT_NUM > 20:
    CONCURRENT_NUM = 20
elif CONCURRENT_NUM < 1:
    CONCURRENT_NUM = 1

output_lock = Lock()

TOKEN = 'wwesldfs29aniversaryvdld29'
SYS_CODE = 'MCS-MIMP-CORE'

# 高价值奖品类型（非寄件券类）
HIGH_VALUE_TYPES = {'SFM'}  # 实物奖品
# 高价值奖品名称关键词
HIGH_VALUE_KEYWORDS = [
    '金条', '金贴', 'iPhone', '大疆', '相机', '水杯', '冰霸', '环保袋',
    '挂件', '小马', '黄金',
]
# 高价值寄件券面额阈值
HIGH_VALUE_COUPON_MIN = 12


# ==================== 日志缓冲 ====================
class LogBuffer:
    def __init__(self):
        self.lines: List[str] = []

    def log(self, msg: str):
        self.lines.append(msg)

    def flush(self):
        text = '\n'.join(self.lines)
        with output_lock:
            print(text)
        self.lines.clear()


# ==================== 代理管理器 ====================
class ProxyManager:
    def __init__(self, api_url: str):
        self.api_url = api_url

    def get_proxy(self) -> Optional[Dict[str, str]]:
        try:
            if not self.api_url:
                return None
            response = requests.get(self.api_url, timeout=10)
            if response.status_code == 200:
                proxy_text = response.text.strip()
                if ':' in proxy_text:
                    proxy = proxy_text if proxy_text.startswith('http') else f'http://{proxy_text}'
                    return {'http': proxy, 'https': proxy}
            return None
        except Exception:
            return None

    @staticmethod
    def display_proxy(proxy_dict: Optional[Dict[str, str]]) -> str:
        if not proxy_dict:
            return '无代理'
        proxy = proxy_dict.get('http', '')
        if '@' in proxy:
            parts = proxy.split('@')
            return f"http://***@{parts[-1]}"
        return proxy


# ==================== HTTP客户端 ====================
class SFHttpClient:
    def __init__(self, proxy_manager: ProxyManager):
        self.proxy_manager = proxy_manager
        self.session = requests.Session()
        self.session.verify = False
        self.current_proxy_display = '无代理'

        proxy = self.proxy_manager.get_proxy()
        if proxy:
            self.session.proxies = proxy
            self.current_proxy_display = ProxyManager.display_proxy(proxy)

        self.headers = {
            'Host': 'mcs-mimp-web.sf-express.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090a13) UnifiedPCWindowsWechat(0xf254173b) XWEB/19027',
            'Accept': 'application/json, text/plain, */*',
            'Content-Type': 'application/json',
            'channel': 'xcxpart',
            'platform': 'MINI_PROGRAM',
            'accept-language': 'zh-CN,zh;q=0.9',
        }

    def _generate_sign(self) -> Dict[str, str]:
        timestamp = str(int(round(time.time() * 1000)))
        data = f'token={TOKEN}&timestamp={timestamp}&sysCode={SYS_CODE}'
        signature = hashlib.md5(data.encode()).hexdigest()
        return {'syscode': SYS_CODE, 'timestamp': timestamp, 'signature': signature}

    def request(self, url: str, data: Optional[Dict] = None) -> Optional[Dict]:
        for attempt in range(MAX_PROXY_RETRIES + 1):
            sign_data = self._generate_sign()
            headers = {**self.headers, **sign_data}
            try:
                resp = self.session.post(url, headers=headers, json=data or {}, timeout=PROXY_TIMEOUT)
                resp.raise_for_status()
                result = resp.json()
                if result is not None:
                    return result
            except Exception:
                pass
            if attempt < MAX_PROXY_RETRIES:
                new_proxy = self.proxy_manager.get_proxy()
                if new_proxy:
                    self.session.proxies = new_proxy
                    self.current_proxy_display = ProxyManager.display_proxy(new_proxy)
                time.sleep(1)
        return None

    def login(self, url: str) -> tuple:
        try:
            decoded_input = unquote(url)
            if decoded_input.startswith('sessionId=') or '_login_mobile_=' in decoded_input:
                cookie_dict = {}
                for item in decoded_input.split(';'):
                    item = item.strip()
                    if '=' in item:
                        k, v = item.split('=', 1)
                        cookie_dict[k] = v
                for k, v in cookie_dict.items():
                    self.session.cookies.set(k, v, domain='mcs-mimp-web.sf-express.com')
                phone = cookie_dict.get('_login_mobile_', '')
                return (True, phone) if phone else (False, '')
            else:
                self.session.get(unquote(url), headers=self.headers, timeout=PROXY_TIMEOUT)
                cookies = self.session.cookies.get_dict()
                phone = cookies.get('_login_mobile_', '')
                return (True, phone) if phone else (False, '')
        except Exception:
            return False, ''


# ==================== 判断高价值奖品 ====================
def is_high_value(item: Dict) -> bool:
    """判断是否为高价值奖品"""
    product_type = item.get('productType', '')
    product_name = item.get('productName', '')

    # 实物奖品都算高价值
    if product_type in HIGH_VALUE_TYPES:
        return True

    # 名称包含关键词
    for kw in HIGH_VALUE_KEYWORDS:
        if kw in product_name:
            return True

    # 高面额寄件券
    if product_type in ('SFC', 'SFFC', 'SFTC'):
        try:
            denomination = float(item.get('denomination', '0'))
            if item.get('couponType') == 1 and denomination >= HIGH_VALUE_COUPON_MIN:
                return True
        except (ValueError, TypeError):
            pass

    return False


# ==================== 查询执行器 ====================
class AwardQueryExecutor:
    def __init__(self, http: SFHttpClient, phone: str, log: LogBuffer):
        self.http = http
        self.phone = phone
        self.masked_phone = phone[:3] + "****" + phone[7:] if len(phone) >= 7 else phone
        self.log = log

    def query_awards(self) -> Optional[List[Dict]]:
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~activityCore~userAwardService~queryUserAward'
        data = {
            "tag": "ANNIVERSARY_2026",
            "productType": "",
            "pageNo": 1,
            "pageSize": 200,
            "startTime": "2026-03-16 10:00:00"
        }
        resp = self.http.request(url, data=data)
        if resp and resp.get('success'):
            obj = resp.get('obj', {})
            return obj.get('list', [])
        return None

    def run(self) -> Dict[str, Any]:
        log = self.log

        awards = self.query_awards()
        if awards is None:
            log.log(f"❌ {self.masked_phone} | 查询失败")
            return {'success': False, 'phone': self.phone, 'masked_phone': self.masked_phone,
                    'total': 0, 'high_value': [], 'all_awards': []}

        # 分类统计
        high_value_items = []
        coupon_count = 0
        product_summary = {}

        for item in awards:
            name = item.get('productName', '未知')
            product_summary[name] = product_summary.get(name, 0) + 1

            if is_high_value(item):
                high_value_items.append({
                    'name': name,
                    'desc': item.get('productDesc', ''),
                    'type': item.get('productType', ''),
                    'get_time': item.get('getTime', ''),
                    'tag': item.get('tag', ''),
                })
            else:
                coupon_count += 1

        # 输出该账号信息
        if high_value_items:
            log.log(f"🎉 {self.masked_phone} | 奖品{len(awards)}个 | 高价值{len(high_value_items)}个:")
            for hv in high_value_items:
                log.log(f"   ⭐ {hv['name']} ({hv['get_time']})")
        else:
            log.log(f"📦 {self.masked_phone} | 奖品{len(awards)}个 | 均为普通券")

        return {
            'success': True,
            'phone': self.phone,
            'masked_phone': self.masked_phone,
            'total': len(awards),
            'high_value': high_value_items,
            'all_awards': awards,
            'product_summary': product_summary,
        }


# ==================== 账号执行 ====================
def run_account(account_url: str, index: int) -> Dict[str, Any]:
    log = LogBuffer()
    proxy_url = os.getenv('SF_PROXY_API_URL', '')
    proxy_manager = ProxyManager(proxy_url)

    http = SFHttpClient(proxy_manager)
    retry_count = 0
    login_success = False
    phone = ''

    while retry_count < MAX_PROXY_RETRIES and not login_success:
        try:
            if retry_count > 0:
                http = SFHttpClient(proxy_manager)
            success, phone = http.login(account_url)
            if success:
                login_success = True
                break
        except Exception:
            pass
        retry_count += 1
        if retry_count < MAX_PROXY_RETRIES:
            time.sleep(1)

    if not login_success:
        log.log(f"❌ 账号{index + 1} 登录失败")
        log.flush()
        return {'success': False, 'phone': '', 'masked_phone': '未登录', 'index': index,
                'total': 0, 'high_value': [], 'all_awards': []}

    executor = AwardQueryExecutor(http, phone, log)
    result = executor.run()
    result['index'] = index

    log.flush()
    return result


# ==================== 主程序 ====================
def main():
    env_name = 'sfsyUrl'
    env_value = os.getenv(env_name)
    if not env_value:
        print(f"❌ 未找到环境变量 {env_name}，请检查配置")
        return

    account_urls = [url.strip() for url in env_value.split('&') if url.strip()]
    if not account_urls:
        print(f"❌ 环境变量 {env_name} 为空或格式错误")
        return

    print("=" * 60)
    print(f"🔍 顺丰33周年 - 奖品查询")
    print(f"📱 共 {len(account_urls)} 个账号")
    print(f"⚙️ 并发数量: {CONCURRENT_NUM}")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    all_results = []

    if CONCURRENT_NUM <= 1:
        for idx, url in enumerate(account_urls):
            result = run_account(url, idx)
            all_results.append(result)
            if idx < len(account_urls) - 1:
                time.sleep(1)
    else:
        with ThreadPoolExecutor(max_workers=CONCURRENT_NUM) as pool:
            futures = {pool.submit(run_account, url, idx): idx for idx, url in enumerate(account_urls)}
            for future in as_completed(futures):
                all_results.append(future.result())

    all_results.sort(key=lambda x: x['index'])

    # ==================== 汇总报告 ====================
    print(f"\n{'='*60}")
    print(f"📊 奖品查询汇总")
    print(f"{'='*60}")

    total_awards = 0
    all_high_value = []

    for r in all_results:
        total_awards += r.get('total', 0)
        for hv in r.get('high_value', []):
            hv['masked_phone'] = r['masked_phone']
            all_high_value.append(hv)

    success_count = sum(1 for r in all_results if r['success'])
    fail_count = len(all_results) - success_count

    print(f"📱 查询账号: {len(all_results)} (成功{success_count} / 失败{fail_count})")
    print(f"🎁 总奖品数: {total_awards}")
    print(f"⭐ 高价值奖品: {len(all_high_value)} 个")

    # 高价值奖品分类：实物 vs 券
    if all_high_value:
        physical_items = [hv for hv in all_high_value if hv.get('type') in ('SFM',)]
        coupon_items = [hv for hv in all_high_value if hv.get('type') not in ('SFM',)]

        if physical_items:
            print(f"\n{'─'*60}")
            print(f"🏆 实物奖品 ({len(physical_items)}个):")
            print(f"{'─'*60}")
            for hv in physical_items:
                print(f"  📞 {hv['masked_phone']}: {hv['name']}")

        if coupon_items:
            print(f"\n{'─'*60}")
            print(f"🎫 高价值券 ({len(coupon_items)}个):")
            print(f"{'─'*60}")
            for hv in coupon_items:
                print(f"  📞 {hv['masked_phone']}: {hv['name']}")

        # 按名称统计数量
        print(f"\n{'─'*60}")
        print(f"📋 高价值奖品统计:")
        if physical_items:
            phy_count = {}
            for hv in physical_items:
                phy_count[hv['name']] = phy_count.get(hv['name'], 0) + 1
            print(f"  🏆 实物:")
            for name, count in sorted(phy_count.items(), key=lambda x: -x[1]):
                print(f"     {name} x{count}")
        if coupon_items:
            cou_count = {}
            for hv in coupon_items:
                cou_count[hv['name']] = cou_count.get(hv['name'], 0) + 1
            print(f"  🎫 券:")
            for name, count in sorted(cou_count.items(), key=lambda x: -x[1]):
                print(f"     {name} x{count}")

    print(f"\n{'='*60}")
    print("🎊 查询完成!")


if __name__ == '__main__':
    main()
