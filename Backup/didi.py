# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2023/7/10 17:54
# @Author  : ziyou
# -------------------------------
# 参考了 一风一燕 的原脚本进行修改
# cron "0 8,10,13,14,15,17 * * *" script-path=xxx.py,tag=匹配cron用
# const $ = new Env('滴滴')
# 抓包获取 didi_jifen_token
# 手机开启抓包后，点击福利金 查看福利金的明细后
# 寻找 https://rewards.xiaojukeji.com/loyalty_credit/bonus/getWelfareUsage4Wallet
# 链接里的token=xxxx&city，xxx便是 didi_jifen_token
# 主要功能：自动领取我的权益、福利金签到、瓜分福利金、领取完单返福利金、领取每日优惠券...
# 滴滴
# export didi_jifen_token='9Op**__w==&9Op**__w==',多账号使用换行或&


import datetime
import os
import re
import sys
import time
import requests

ck_list = []

MONTH_SIGNAL = False  # 默认关闭月月领券

__version__ = '1.0.0'


# 加载环境变量
def get_env():
    global ck_list
    env_str = os.getenv("didi_jifen_token")
    if env_str:
        ck_list += env_str.replace("&", "\n").split("\n")


def get_version_from_github():
    latest_version = '获取失败'
    username = "q7q7q7q7q7q7q7"
    repo = "ziyou"
    filepath = "滴滴.py"
    url_list = [
        f'https://raw.fgit.cf/{username}/{repo}/main/{filepath}',
        f"https://ghproxy.com/https://raw.githubusercontent.com/{username}/{repo}/main/{filepath}",
    ]
    for url in url_list:
        try:
            response = requests.get(url, timeout=(3, 3))
            if response.status_code == 200:
                response_text = response.text
                version_regex = r"^__version__\s*=\s*[\'\"]([^\'\"]*)[\'\"]"
                version_match = re.search(version_regex, response_text,
                                          re.MULTILINE)
                if version_match is not None and __version__:
                    latest_version = version_match.group(1)
                    break
        except Exception as e:
            if e:
                pass
    print(f'现在运行的版本是：{__version__}，最新版本：{latest_version}')


class DiDi:
    LAT = '28.20055'  # 纬度
    LNG = '113.01907'  # 经度
    CITY_ID = 24  # 城市id

    def __init__(self, token, city_id=CITY_ID, lat=LAT, lng=LNG):
        self.token = token
        self.city_id = city_id
        self.lat = lat
        self.lng = lng
        self.today = datetime.datetime.now().strftime(
            '%Y-%m-%d')  # 今天时间 例如：'2023-07-12'
        # 明天时间 例如：'2023-07-13'
        self.tomorrow = (datetime.datetime.now() + datetime.timedelta(
            days=1)).strftime('%Y-%m-%d')
        self.activity_id_today = 0  # 今天的瓜分福利金的活动id 用于完成今天的瓜分福利金 需在14点之前
        self.task_id_today = 0  # 完成今天的瓜分福利金的任务id 用于完成今天的瓜分福利金 需在14点之前
        self.status_today = 0  # 显示今天的瓜分活动状态 1为待报名 2为已参加 3为已完成待发奖 4为已发奖 5为未参加
        self.activity_id_tomorrow = 0  # 明天瓜分福利金的活动id 用于报名明天的瓜分福利金
        self.status_tomorrow = 0  # 显示今天的瓜分活动状态 1为待报名 2为已参加 3为已完成待发奖 4为已发奖 5为未参加
        self.count_tomorrow = 0

    # 签到
    def check_in(self):
        url = f'https://ut.xiaojukeji.com/ut/welfare/api/action/dailySign'
        _json = {"token": self.token,
                 "lat": self.lat,
                 "lng": self.lng,
                 "platform": "na",
                 "env": '{}'}
        response = requests.post(url=url, json=_json)
        response_dict = response.json()
        # print(response_dict)
        if response_dict.get('errno') == 0:
            subsidy_amount = response_dict['data']['subsidy_state'][
                'subsidy_amount']
            print(f"今日签到成功，获得{subsidy_amount}福利金")
            return
        if response_dict.get('errno') == 40009:
            print("今日福利金已签到，无需重复签到!")
            return
        print(f'福利金签到出错！ {response_dict}')

    # 获取瓜分活动ID
    def get_carve_up_action_id(self):
        url = f'https://ut.xiaojukeji.com/ut/welfare/api/home/init/v2'
        _json = {"token": self.token,
                 "lat": self.lat,
                 "lng": self.lng,
                 "platform": "na",
                 "env": '{}'}
        response = requests.post(url=url, json=_json)
        response_dict = response.json()
        # print(response_dict)
        divide_data = response_dict['data']['divide_data']['divide']

        today_data = divide_data[self.today]
        # print(today_data)
        self.activity_id_today, self.task_id_today, self.status_today = \
            today_data['activity_id'], today_data[
                'task_id'], today_data['status']

        tomorrow_data = divide_data[self.tomorrow]
        # print(tomorrow_data)
        self.activity_id_tomorrow, self.status_tomorrow, self.count_tomorrow = \
            tomorrow_data['activity_id'], \
                tomorrow_data['status'], tomorrow_data['button']['count']
        return True

    # 报名明天的瓜分福利金
    def apply_carve_up_action(self):
        url = f'https://ut.xiaojukeji.com/ut/welfare/api/action/joinDivide'
        _json = {"token": self.token,
                 "lat": self.lat,
                 "lng": self.lng,
                 "platform": "na",
                 "env": '{}',
                 "activity_id": self.activity_id_tomorrow,
                 "count": self.count_tomorrow,
                 "type": "ut_bonus"}
        response = requests.post(url=url, json=_json)
        response_dict = response.json()
        # print(response_dict)
        if response_dict.get("errno") == 0:
            if response_dict.get("data", {}).get("result") is True:
                print("报名今日打卡瓜分活动成功！")
                return
        print(f'报名今日打卡瓜分活动失败！ {response_dict}')

    # 完成今天的瓜分福利金 需在14点之前
    def complete_carve_up_action(self):
        url = f'https://ut.xiaojukeji.com/ut/welfare/api/action/divideReward'
        _json = {"token": self.token,
                 "lat": self.lat,
                 "lng": self.lng,
                 "platform": "na",
                 "env": '{}',
                 "activity_id": self.activity_id_today,
                 "task_id": self.task_id_today}
        response = requests.post(url=url, json=_json)
        response_dict = response.json()
        # print(response_dict)
        if response_dict.get("errno") == 0:
            if response_dict.get("data", {}).get("result") is True:
                print("完成今日打卡瓜分活动成功！")
                return
        print(f'完成今日打卡瓜分活动失败！ {response_dict}')

    # 查询当前福利金数量
    def get_info(self):
        url = "https://rewards.xiaojukeji.com/loyalty_credit/bonus/getWelfareUsage4Wallet"
        params = {"token": self.token, "city_id": self.city_id}
        response = requests.get(url=url, params=params)
        response_dict = response.json()
        # print(response_dict)
        balance = response_dict['data']['balance']
        return balance

    # 查询权益详情
    def inquire_benefits_details(self):
        url = "https://member.xiaojukeji.com/dmember/h5/privilegeLists"
        params = {"token": self.token, "city_id": self.city_id}
        time.sleep(0.5)
        response = requests.get(url=url, params=params)
        response_dict = response.json()
        # print(response_dict)
        privileges_list = response_dict.get('data', {}).get('privileges',
                                                            [])  # 我的权益列表
        return privileges_list

    # 领取 周周领券 活动的优惠券
    def receive_level_gift_week(self):
        privileges_list = self.inquire_benefits_details()
        for privileges in privileges_list:
            if privileges.get('name') not in ['周周领券'] or privileges.get(
                    'level_gift') is None:
                continue
            coupons_list = privileges.get('level_gift', {}).get('coupons', [])
            for coupons in coupons_list:
                status = coupons.get('status')  # 0为未领取，1为已使用，2为未使用
                if status != 0:
                    continue
                batch_id = coupons.get('batch_id')
                # print(batch_id)
                print(
                    f"开始领取 {coupons.get('remark')}{coupons.get('coupon_title')}")
                url = f"https://member.xiaojukeji.com/dmember/h5/receiveLevelGift?xbiz=&prod_key=wyc-vip-level&xpsid=&dchn=&xoid=&xenv=passenger&xspm_from=&xpsid_root=&xpsid_from=&xpsid_share=&token={self.token}&batch_id={batch_id}&env={{}}&gift_type=1&city_id={self.city_id}"
                time.sleep(0.5)
                response = requests.get(url=url)
                response_dict = response.json()
                # print(f'{response_dict}')
                if response_dict.get('errno') == 0:
                    print('领取成功！')
                    continue
                print(f'领取出错！ {response_dict}')

    # 领取 月月领券 活动的优惠券
    def receive_level_gift_month(self):
        if not MONTH_SIGNAL:
            print('月月领券已设置关闭')
            return
        privileges_list = self.inquire_benefits_details()
        for privileges in privileges_list:
            if privileges.get('name') not in ['月月领券'] or privileges.get(
                    'level_gift') is None:
                continue
            coupons_list = privileges.get('level_gift', {}).get('coupons', [])
            for coupons in coupons_list:
                status = coupons.get('status')  # 0为未领取，1为已使用，2为未使用
                if status != 0:
                    continue
                batch_id = coupons.get('batch_id')
                # print(batch_id)
                print(
                    f"开始领取 {coupons.get('remark')}{coupons.get('coupon_title')}")
                url = f"https://member.xiaojukeji.com/dmember/h5/receiveLevelGift?xbiz=&prod_key=wyc-vip-level&xpsid=&dchn=&xoid=&xenv=passenger&xspm_from=&xpsid_root=&xpsid_from=&xpsid_share=&token={self.token}&batch_id={batch_id}&env={{}}&gift_type=1&city_id={self.city_id}"
                time.sleep(0.5)
                response = requests.get(url=url)
                response_dict = response.json()
                # print(f'{response_dict}')
                if response_dict.get('errno') == 0:
                    print('领取成功！')
                    continue
                print(f'领取出错！ {response_dict}')

    # 膨胀 周周领券 活动的优惠券
    def swell_coupon(self):
        privileges_list = self.inquire_benefits_details()  # 我的权益列表
        for privileges in privileges_list:
            if privileges.get('name') in ['周周领券', '月月领券']:
                if privileges.get('level_gift') is None:
                    continue
                coupons_list = privileges.get('level_gift', {}).get('coupons',
                                                                    [])
                for coupons in coupons_list:  # 膨胀
                    swell_status = coupons.get(
                        'swell_status')  # 0代表不能膨胀，1代表能膨胀,2代表已膨胀
                    # print(swell_status)
                    if swell_status == 1:
                        print(
                            f"开始膨胀 {coupons.get('remark')}{coupons.get('coupon_title')}")
                        batch_id = coupons.get('batch_id')
                        coupon_id = coupons.get('coupon_id')
                        url = f'https://member.xiaojukeji.com/dmember/h5/swell_coupon?city_id={self.city_id}'
                        _json = {"token": self.token,
                                 "batch_id": batch_id,
                                 "coupon_id": coupon_id,
                                 "city_id": self.city_id}
                        time.sleep(0.5)
                        response = requests.post(url=url, json=_json)
                        response_dict = response.json()
                        # print(response_dict)
                        if response_dict.get('error') == 0:
                            if response_dict.get('data', {}).get(
                                    'is_swell') is True:
                                print('膨胀成功！')
                                continue
                            print('膨胀失败！')
                            continue
                        print(f'膨胀出错！ {response_dict}')
                return

    # 领取行程意外险
    def receive_travel_insurance(self):
        privileges_list = self.inquire_benefits_details()  # 我的权益列表
        for privileges in privileges_list:
            if privileges.get('name') == '行程意外险':
                # print(privileges)
                need_received = privileges.get('need_received')
                if need_received == 1:  # 0为未领取，1为已领取
                    print('已领取了！')
                    return
                if need_received == 0:  # 0为未领取，1为已领取
                    url = 'https://member.xiaojukeji.com/dmember/h5/bindPrivilege'
                    _json = {"token": self.token, "type": 3}
                    time.sleep(0.5)
                    response = requests.post(url=url, json=_json)
                    response_dict = response.json()
                    # print(response_dict)
                    if response_dict.get('errno') == 0:
                        print('领取成功！')
                        return
                    print(f'领取出错！ {response_dict}')
                    return
                print(f'出现未知情况！ {need_received =} {privileges}')
                return

    # 领取周三折上折权益
    def receive_memberday_discount_multi(self):
        privileges_list = self.inquire_benefits_details()  # 我的权益列表
        for privileges in privileges_list:
            if privileges.get('name') == '周三折上折':
                # print(privileges)
                need_received = privileges.get('need_received')
                if need_received == 1:  # 0为未领取，1为已领取
                    print('已领取了！')
                    return
                if need_received == 0:  # 0为未领取，1为已领取
                    url = 'https://member.xiaojukeji.com/dmember/h5/receiveMemberDayDiscount'
                    _json = {"token": self.token, "privilege_type": 1}
                    time.sleep(0.5)
                    response = requests.post(url=url, json=_json)
                    response_dict = response.json()
                    # print(response_dict)
                    if response_dict.get('errno') == 0:
                        print('领取成功！')
                        return
                    print(f'领取出错！ {response_dict}')
                    return
                print(f'出现未知情况！ {need_received =} {privileges}')
                return

    # 领取 气泡奖励 完单返福利金
    def receive_wyc_order_finish(self):
        url = 'https://ut.xiaojukeji.com/ut/welfare/api/home/getBubble'
        _json = {"token": self.token,
                 "lat": self.lat,
                 "lng": self.lng,
                 "platform": "na",
                 "env": "{}"}
        # time.sleep(0.5)
        response = requests.post(url=url, json=_json)
        response_dict = response.json()
        # print(response_dict)
        bubble_list = response_dict.get('data', {}).get('bubble_list', [])
        # print(bubble_list)
        for bubble in bubble_list:
            if bubble.get('pre_content') == '完单返':
                # print(bubble)
                cycle_id = bubble.get('cycle_id')
                reward_count = bubble.get('reward_count')
                url = 'https://ut.xiaojukeji.com/ut/welfare/api/action/clickBubble'
                _json = {"token": self.token,
                         "lat": self.lat,
                         "lng": self.lng,
                         "platform": "na",
                         "env": "{}",
                         "cycle_id": cycle_id,
                         "bubble_type": "wyc_order_finish"}
                time.sleep(0.5)
                response = requests.post(url=url, json=_json)
                response_dict = response.json()
                # print(response_dict)
                if response_dict.get('errno') == 0:
                    print(f'领取成功，获得{reward_count}福利金！')
                    return
                print(f'领取出错！ {response_dict}')
                return

    # 天天领神券签到
    def claim_coupon_check_in(self):
        url = 'https://ut.xiaojukeji.com/ut/janitor/api/action/sign/do'
        headers = {'Didi-Ticket': self.token}
        response = requests.post(url=url, headers=headers)
        response_dict = response.json()
        # print(response_dict)
        if response_dict.get('errno') == 0:
            current_progress = response_dict.get("data").get("current_progress")
            total_progress = response_dict.get("data").get("total_progress")
            print(f'签到成功！签到进度：{current_progress}/{total_progress}')
            return
        print(f'签到失败！{response_dict.get("errmsg")}')

    # 天天领神券抽奖
    def claim_coupon_lottery(self):
        url = 'https://api.didi.cn/webx/chapter/product/init'
        headers = {'Didi-Ticket': self.token}
        _json = {"dchn": "dKlklLa",
                 "args": {"runtime_args": {"token": self.token,
                                           "lat": self.lat, "lng": self.lng,
                                           "env": {},
                                           "platform": "na",
                                           "Didi-Ticket": self.token, }}, }
        response = requests.post(url=url, headers=headers, json=_json)
        response_dict = response.json()
        # print(response_dict)
        lottery_chance = response_dict.get('data').get('conf').get(
            'strategy_data').get('data').get('lottery_chance')
        act_id = response_dict.get('data').get('conf').get('ext').get(
            'act_conf').get('act_id')
        # print(lottery_chance, act_id)
        # print(f'当前抽奖次数为：{lottery_chance}')
        for _ in range(lottery_chance):
            url = 'https://ut.xiaojukeji.com/ut/janitor/api/action/lottery/doLottery'
            headers = {'Didi-Ticket': self.token}
            _json = {"act_id": act_id}
            response = requests.post(url=url, headers=headers, json=_json)
            response_dict = response.json()
            # print(response_dict)
            if response_dict.get('errno') == 0:
                print(
                    f'抽奖成功！获得{response_dict.get("data").get("prize_data")[0].get("name")}')
                time.sleep(5)
                continue
            print(f'抽奖失败！{response_dict.get("errmsg")}')
            return

    # 瓜瓜乐
    def guaguale(self):
        if self.get_carve_up_action_id():
            print(f'开始完成今日瓜分活动！')
            if self.status_today == 2:  # 1为待报名，2为待完成，3为已完成，4为已领取
                self.complete_carve_up_action()  # 完成瓜分福利金 需在14点之前
            elif self.status_today == 3:
                print('今天已完成瓜分活动！')
            elif self.status_today == 4:
                print('今天已领取瓜分活动奖励！')
            else:
                print('完成失败，可能昨日未报名！')
            print(f'开始报名明日瓜分活动！')
            if self.status_tomorrow == 1:  # 1为待报名，2为待完成，3为已完成，4为已领取
                self.apply_carve_up_action()  # 报名瓜分福利金
            elif self.status_tomorrow == 2:
                print('今天已经报名参加瓜分明天的福利金了！')
            else:
                print('报名参加瓜分明天的福利金出现未知错误！')

    def today_pick(self):
        url = 'https://api.didi.cn/webx/chapter/page/batch/config'
        headers = {'Didi-Ticket': self.token}
        _json = {"dchn": "PxJanq9",
                 "args": [
                     {"dchn": "kkXgpzO", "prod_key": "ut-limited-seckill",
                      "runtime_args": {"token": self.token,
                                       "lat": self.lat, "lng": self.lng,
                                       "env": {},
                                       "Didi-Ticket": self.token, }
                      },
                     {"dchn": "gL3E8qZ", "prod_key": "ut-support-coupon",
                      "runtime_args": {"token": self.token,
                                       "lat": self.lat,
                                       "lng": self.lng, "env": {},
                                       "Didi-Ticket": self.token, }
                      }
                 ]}
        response = requests.post(url=url, headers=headers, json=_json)
        response_dict = response.json()
        # print(response_dict)
        activity_list = response_dict.get('data').get('conf')
        # print(activity_list)
        for activity in activity_list:
            if activity.get('dchn') == 'gL3E8qZ':
                print('★开始领取每日精选')
                coupons_list = activity.get('strategy_data').get('data').get(
                    'daily_coupon').get('coupons')
                coupons_status_name_dict = {'1': '可领取', '2': '已经领取',
                                            '4': '已抢光',
                                            '6': '待前置条件完成'}
                for coupon_index, coupon in enumerate(coupons_list):
                    coupons_name = coupon.get('name')
                    coupons_status = coupon.get('status')  # 1为可领取 2为已经领取 4为抽奖抢券
                    print(f'{coupon_index + 1}.券名：{coupons_name} '
                          f'状态：{coupons_status_name_dict[str(coupons_status)]}')
                    if coupons_status == 1:
                        print('开始领取')
                        activity_id = coupon.get('activity_id')

                        if coupons_name == '打车5元券':
                            print('该券为分享助力才能领券，不支持自动领取')
                            continue
                        if activity_id == '10010':
                            print(
                                '该券为明天在目的地栏搜“领券”必得1张快车优惠券，不支持自动领取')
                            continue

                        group_id = coupon.get('group_id')
                        coupon_conf_id = coupon.get('coupon_conf_id')
                        group_date = coupon.get('group_date')
                        url = 'https://ut.xiaojukeji.com/ut/janitor/api/action/coupon/bind'
                        headers = {'Didi-Ticket': self.token}
                        _json = {
                            'group_date': group_date,
                            "activity_id": activity_id,
                            "group_id": group_id,
                            "coupon_conf_id": coupon_conf_id,
                        }
                        response = requests.post(
                            url=url, headers=headers, json=_json)
                        response_dict = response.json()
                        # print(response_dict)
                        if response_dict.get('errno') == 0:
                            # name = response_dict.get('data').get('name')
                            print(f'领取成功')
                            time.sleep(0.5)
                            continue
                        print(f'领取失败 {response_dict}')
                        return

            if activity.get('dchn') == 'kkXgpzO':
                print('★开始领取限时抢')
                seckill_list = activity.get('strategy_data').get('data').get(
                    'seckill')  # 秒杀列表
                seckill_status_name_dict = {'1': '正在热抢', '2': '即将开始',
                                            '3': '已经开抢'}
                coupons_status_name_dict = {'1': '可领取', '2': '已经领取',
                                            '4': '抽奖抢券', '5': '未到时间'}

                for seckill in seckill_list:
                    seckill_name = seckill.get('start_at')
                    seckill_status = int(
                        seckill.get('status'))  # 1为正在热抢 2为即将开始 3为已经开抢
                    print(
                        f'☆☆场次：{seckill_name} 状态：{seckill_status_name_dict[str(seckill_status)]}')
                    if seckill_status in [1, 3]:
                        coupons_list = seckill.get('coupons')
                        for coupon_index, coupon in enumerate(coupons_list):
                            coupons_name = coupon.get('name')
                            coupons_status = coupon.get(
                                'status')  # 1为可领取 2为已经领取 4为抽奖抢券
                            print(f'{coupon_index + 1}.券名：{coupons_name} '
                                  f'状态：{coupons_status_name_dict[str(coupons_status)]}')
                            if coupons_status == 1:
                                print('开始领取')
                                activity_id = coupon.get('activity_id')
                                group_id = coupon.get('group_id')
                                coupon_conf_id = coupon.get('coupon_conf_id')
                                group_date = coupon.get('group_date')
                                url = 'https://ut.xiaojukeji.com/ut/janitor/api/action/coupon/bind'
                                headers = {'Didi-Ticket': self.token}
                                _json = {"activity_id": activity_id,
                                         "group_id": group_id,
                                         'group_date': group_date,
                                         "coupon_conf_id": coupon_conf_id, }
                                response = requests.post(url=url,
                                                         headers=headers,
                                                         json=_json)
                                response_dict = response.json()
                                # print(response_dict)
                                if response_dict.get('errno') == 0:
                                    # name = response_dict.get('data').get('name')
                                    print(f'领取成功')
                                    time.sleep(0.5)
                                    continue
                                print(f'领取失败 {response_dict}')

    def main(self):
        character = '★★'
        print(f'{character}当前福利金数量为：{self.get_info()}')
        print(f'{character}开始领取每日精选活动券')
        self.today_pick()
        print(f'{character}开始进行福利金签到')
        self.check_in()
        print(f'{character}开始进行瓜瓜乐瓜分福利金')
        self.guaguale()
        print(f'{character}开始领取 周周领券 活动的优惠券')
        self.receive_level_gift_week()
        print(f'{character}开始领取 月月领券 活动的优惠券')
        self.receive_level_gift_month()
        print(f'{character}开始膨胀 周周或月月领券 活动的优惠券')
        self.swell_coupon()
        print(f'{character}开始领取行程意外险')
        self.receive_travel_insurance()
        print(f'{character}开始领取周三折上折权益')
        self.receive_memberday_discount_multi()
        print(f'{character}开始领取气泡奖励')
        self.receive_wyc_order_finish()
        print(f'{character}开始天天领神券签到')
        self.claim_coupon_check_in()
        print(f'{character}开始天天领神券抽奖')
        self.claim_coupon_lottery()
        print(f'{character}当前福利金数量为：{self.get_info()}')


# 主程序
def main(ck_list):
    get_version_from_github()
    get_env()
    if not ck_list:
        print('没有获取到账号！')
        return
    print(f'获取到{len(ck_list)}个账号！')
    for index, ck in enumerate(ck_list):
        print(f'*****第{index + 1}个账号*****')
        DiDi(ck).main()
        print('')


if __name__ == '__main__':
    main(ck_list)
    sys.exit()
