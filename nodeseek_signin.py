#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NodeSeek 签到脚本 - 适配青龙面板

【首次使用参数说明】

1. 获取 Cookie：
   - 浏览器访问 https://www.nodeseek.com 并登录
   - 按 F12 打开开发者工具 → Application → Cookies → https://www.nodeseek.com
   - 复制列表中所有 Name 和对应的 Value，按以下格式拼接：
     name1=value1; name2=value2; name3=value3
   - 示例：cf_clearance=xxx; colorscheme=light; fog=xxx; hmti_=xxx; pjwt=xxx; session=xxx; session_id=xxx; smac=xxx

2. 青龙面板环境变量设置：
   - 名称: NS_COOKIE
   - 值: 上一步拼接好的完整 Cookie 字符串（所有字段用 "; " 连接）
   - 类型: 普通变量

3. 可选参数：
   - NS_RANDOM: 签到随机参数，默认 true，一般无需修改

4. 多账号支持：
   - 多个账号的 Cookie 用 "&" 分隔
   - 格式: cookie1; cookie2; ...&cookie1; cookie2; ...

5. 定时任务：
   - 在青龙面板"定时任务"中添加，建议每天固定时间执行一次
   - 命令: python3 /ql/data/scripts/nodeseek_signin.py

6. 通知功能：
   - 脚本会自动尝试加载青龙面板自带的 sendNotify 模块发送通知
   - 无需额外配置
"""
import os
import sys
import time
import json
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

try:
    import requests
except ImportError:
    os.system("pip3 install requests -q")
    import requests

# ==================== 通知模块 ====================
# 尝试加载青龙面板通知模块
QL_NOTIFY_PATH = "/ql/scripts/send/sendNotify.py"
ql_send = None

# 检查是否在青龙面板环境中
if os.path.exists(QL_NOTIFY_PATH):
    try:
        sys.path.insert(0, "/ql/scripts/send")
        from sendNotify import send
        ql_send = send
    except ImportError:
        pass

# 也检查其他可能的通知路径
notify_paths = [
    "/ql/data/scripts/send/sendNotify.py",
    "/ql/data/send/sendNotify.py",
]
for notify_path in notify_paths:
    if os.path.exists(notify_path):
        try:
            sys.path.insert(0, os.path.dirname(notify_path))
            from sendNotify import send
            ql_send = send
            break
        except ImportError:
            pass


def notify(title, content):
    """发送通知"""
    if ql_send:
        ql_send(title, content)
    else:
        print(f"[通知] {title}\n{content}")


# ==================== 签到逻辑 ====================
def sign_in(cookie, ns_random="true"):
    """执行签到"""
    if not cookie:
        return "invalid", "无有效Cookie"

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "Origin": "https://www.nodeseek.com",
        "Referer": "https://www.nodeseek.com/board",
        "Content-Type": "application/json",
        "Cookie": cookie,
    }

    try:
        url = f"https://www.nodeseek.com/api/attendance?random={ns_random}"
        response = requests.post(url, headers=headers, timeout=15)
        data = response.json()
        msg = data.get("message", "")

        if data.get("success") or "鸡腿" in msg:
            return "success", msg
        elif "已完成签到" in msg:
            return "already", msg
        elif data.get("status") == 404:
            return "invalid", "Cookie已失效"
        else:
            return "fail", msg
    except Exception as e:
        return "error", str(e)


# ==================== 查询签到统计 ====================
def get_signin_stats(cookie, days=30):
    """查询最近N天的签到收益统计"""
    if not cookie:
        return None, "无有效Cookie"

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "Origin": "https://www.nodeseek.com",
        "Referer": "https://www.nodeseek.com/board",
        "Cookie": cookie,
    }

    try:
        shanghai_tz = ZoneInfo("Asia/Shanghai")
        now = datetime.now(shanghai_tz)
        query_start = now - timedelta(days=days)

        all_records = []
        page = 1
        while page <= 20:
            url = f"https://www.nodeseek.com/api/account/credit/page-{page}"
            response = requests.get(url, headers=headers, timeout=15)
            data = response.json()

            if not data.get("success") or not data.get("data"):
                break

            records = data.get("data", [])
            if not records:
                break

            # 检查最后一条记录时间
            last_time = datetime.fromisoformat(
                records[-1][3].replace("Z", "+00:00")
            ).astimezone(shanghai_tz)
            if last_time < query_start:
                for record in records:
                    record_time = datetime.fromisoformat(
                        record[3].replace("Z", "+00:00")
                    ).astimezone(shanghai_tz)
                    if record_time >= query_start:
                        all_records.append(record)
                break
            else:
                all_records.extend(records)

            page += 1
            time.sleep(0.3)

        # 筛选签到收益记录
        signin_records = []
        for record in all_records:
            amount, balance, description, timestamp = record
            record_time = datetime.fromisoformat(
                timestamp.replace("Z", "+00:00")
            ).astimezone(shanghai_tz)

            if (record_time >= query_start and
                    "签到收益" in description and "鸡腿" in description):
                signin_records.append({
                    "amount": amount,
                    "date": record_time.strftime("%Y-%m-%d"),
                })

        if not signin_records:
            return {
                "total_amount": 0,
                "average": 0,
                "days_count": 0,
                "records": [],
                "period": f"近{days}天" if days > 1 else "今天",
            }, "没有找到签到记录"

        total_amount = sum(r["amount"] for r in signin_records)
        days_count = len(signin_records)
        average = round(total_amount / days_count, 2) if days_count > 0 else 0

        stats = {
            "total_amount": total_amount,
            "average": average,
            "days_count": days_count,
            "records": signin_records,
            "period": f"近{days}天" if days > 1 else "今天",
        }
        return stats, "查询成功"

    except Exception as e:
        return None, f"查询异常: {str(e)}"


# ==================== 主流程 ====================
def main():
    # 读取环境变量
    ns_cookie_raw = os.getenv("NS_COOKIE", "")
    ns_random = os.getenv("NS_RANDOM", "true")

    if not ns_cookie_raw:
        print("错误: 未设置 NS_COOKIE 环境变量")
        sys.exit(1)

    # 分割多个 Cookie
    cookie_list = [c.strip() for c in ns_cookie_raw.split("&") if c.strip()]
    if not cookie_list:
        print("错误: NS_COOKIE 为空")
        sys.exit(1)

    print(f"=== NodeSeek 签到脚本 ===")
    print(f"共 {len(cookie_list)} 个账号")
    print(f"随机参数: {ns_random}")
    print(f"运行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    results = []
    total_success = 0
    total_already = 0

    for i, cookie in enumerate(cookie_list, 1):
        print(f"--- 账号 {i}/{len(cookie_list)} ---")
        status, msg = sign_in(cookie, ns_random)
        print(f"签到结果: {msg}")

        # 查询统计
        stats, stats_msg = get_signin_stats(cookie, 30)
        if stats:
            period = stats["period"]
            d_count = stats["days_count"]
            t_legs = stats["total_amount"]
            avg_legs = stats["average"]
            print(f"统计({period}): 已签{d_count}天，共{t_legs}个鸡腿，平均{avg_legs}个/天")

        results.append(f"账号{i}: {msg}")
        if status == "success":
            total_success += 1
        elif status == "already":
            total_already += 1

        time.sleep(1)  # 避免请求过快

    # 汇总
    print(f"\n=== 签到汇总 ===")
    print(f"成功: {total_success} | 已签: {total_already} | 总计: {len(cookie_list)}")

    # 发送通知
    if ql_send:
        title = "NodeSeek 签到"
        content_lines = "\n".join(results)
        summary = f"汇总: 成功{total_success} | 已签{total_already}"
        content = content_lines + "\n\n" + summary
        notify(title, content)


if __name__ == "__main__":
    main()
