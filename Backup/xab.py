# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2023/8/27 8:59
# @Author  : ziyou
# -------------------------------
# 喜爱帮注册地址 https://m.xiaicn.cn/invite/588570
# 每月至少3块钱
# cron "27 7,12,23 * * *" script-path=xxx.py,tag=匹配cron用
# const $ = new Env('喜爱帮')
# 喜爱帮
# export xiaibang_ck='手机号#密码&手机号#密码'
# 注意：密码中不能包含 & # \n
# export xiaibang_ck='18*********#16947027******',多账号使用换行或&



import os
import re
import sys
import time

import requests

ck_list = []

ck_list_str = os.getenv("xiaibang_ck")
if ck_list_str:
    ck_list += ck_list_str.replace("&", "\n").split("\n")


class XiAiBang:
    def __init__(self, ck, index):
        self.phone_number, self.password = ck.split('#')
        self.cookies = {}
        self.headers = {'Host': 'm.xiaicn.com',
                        'Connection': 'keep-alive',
                        'Accept': 'application/json, image/webp',
                        'X-Requested-With': 'XMLHttpRequest',
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'Origin': 'https://m.xiaicn.com',
                        'Sec-Fetch-Site': 'same-origin',
                        'Sec-Fetch-Mode': 'cors',
                        'Sec-Fetch-Dest': 'empty',
                        'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
                        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1 Edg/115.0.0.0',
                        }
        self._csrf_token = ''

    # 登录
    def login(self):
        headers = self.headers
        login_headers = {
            'authority': 'm.xiaicn.com',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cache-control': 'no-cache',
            'pragma': 'no-cache',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'none',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1 Edg/115.0.0.0',
        }
        url = 'https://m.xiaicn.com/cas/login'
        response = requests.get(url, headers=login_headers)
        set_cookie_header = response.headers.get('Set-Cookie')
        # 使用正则表达式提取 USER_REMEMBER_ME 值
        _match = re.search(r"NiuToken=([^;]+)", set_cookie_header)
        if not _match:
            print('未获取到 NiuToken')
            return False
        _value = _match.group(1)
        # print(_value)
        self.cookies.update({'NiuToken': _value})
        response_text = response.text
        # print(response_text)
        _csrf_token_list = re.findall(r'<input type="hidden" name="_csrf_token" value="(.*?)"/>', response_text)
        if not _csrf_token_list:
            print('未获取到 _csrf_token')
            return False
        _csrf_token = _csrf_token_list[0]
        self._csrf_token = _csrf_token
        params = {'_random': str(time.time() * 1000), }
        data = {'_csrf_token': _csrf_token,
                '_target_path': '',
                '_username': self.phone_number,
                '_password': self.password, }
        response = requests.post('https://m.xiaicn.com/cas/login', params=params, cookies=self.cookies, headers=headers,
                                 data=data)
        response_dict = response.json()
        # print(response_dict)
        if response_dict.get('code') == 0:
            print('登录成功')
            # print(response.headers.get('Set-Cookie'))
            set_cookie_header = response.headers.get('Set-Cookie')
            # 使用正则表达式提取 USER_REMEMBER_ME 值
            _match = re.search(r"USER_REMEMBER_ME=([^;]+)", set_cookie_header)
            if _match:
                _value = _match.group(1)
                # print(_value)
                self.cookies.update({'USER_REMEMBER_ME': _value})
                return True
        print(f'签到失败 {response_dict.get("msg")}')
        return False

    # 获取用户信息
    def get_infomation(self):
        headers = self.headers
        response = requests.get('https://m.xiaicn.com/user/capital',
                                cookies=self.cookies, headers=headers)  # 领取前请求分红界面
        response_text = response.text
        # print(response_text)
        balance = re.findall(r'<span class="num">(.*?)</span>', response_text)[0]
        print(f'{self.phone_number} 当前余额：{balance}')

    # 签到
    def check_in(self):
        url = 'https://m.xiaicn.com/user/active/daily_sign'
        response = requests.get(url, cookies=self.cookies)
        response_text = response.text
        # print(response_text)
        request_id_list = re.findall(r'"requestId":"(.*?)"', response_text)
        if not request_id_list:
            print('签到失败，未获取到 requestId')
            return False
        request_id = request_id_list[0]

        csrf_token_list = re.findall(r'csrfToken ="(.*?)"', response_text)
        if not csrf_token_list:
            print('签到失败，未获取到 csrfToken，可能是今日已签到')
            return False
        csrf_token = csrf_token_list[0]

        headers = self.headers
        _csrf_token = self._csrf_token
        params = {'_random': str(time.time() * 1000), }
        data = {'csrfToken': csrf_token,
                'requestId': request_id, }
        response = requests.post('https://m.xiaicn.com/user/active/daily_sign/sign', params=params,
                                 cookies=self.cookies, headers=headers, data=data)
        response_dict = response.json()
        # print(response_dict)
        if response_dict.get('code') == 0:
            grant_money = response_dict.get("data").get("grantMoney")
            sign_count = response_dict.get("data").get("signCount")
            print(f'签到成功，今日签到获得{int(grant_money) / 10000}元，连续签到天数：{sign_count}')
            return
        print(f'签到失败 {response_dict.get("msg")}')

    # 领取签到任务奖励
    def receive_check_in_task_rewards(self):
        for task_id in ['152', '133']:
            headers = self.headers
            params = {'_random': str(time.time() * 1000), }
            data = f'taskId={task_id}&isCurrent=1'
            response = requests.post('https://m.xiaicn.com/user/active/period_task/reward', params=params,
                                     cookies=self.cookies, headers=headers, data=data)
            response_dict = response.json()
            # print(response_dict)
            if response_dict.get('code') == 0:
                reward_money = response_dict.get("data").get("rewardMoney")
                if task_id == '152':
                    print(f'领取每日签到任务奖励成功，今日签到获得{int(reward_money) / 10000}元')
                    continue
                if task_id == '133':
                    print(f'领取每月签到任务奖励成功，今日签到获得{int(reward_money) / 10000}元')
                    continue
            if task_id == '152':
                print(f'每日签到任务 {response_dict.get("msg")}')
                continue
            if task_id == '133':
                print(f'每月签到任务 {response_dict.get("msg")}')
                continue

    # 领取分红金
    def receive_bonus(self):
        headers = self.headers
        requests.get('https://m.xiaicn.com/user/daily_dividend?_nav=0lkd55uo',
                     cookies=self.cookies, headers=headers)  # 领取前请求分红界面
        time.sleep(0.5)
        params = {'_random': str(time.time() * 1000), }
        data = f'_empty_post={time.time() * 1000}'
        response = requests.post('https://m.xiaicn.com/user/daily_dividend/award', params=params,
                                 cookies=self.cookies, headers=headers, data=data)
        response_dict = response.json()
        # print(response_dict)
        if response_dict.get('code') == 0:
            print(f'领取成功')
            return
        print(f'{response_dict.get("msg")}')

    def main(self):
        character = '★★'
        print(f'{character}开始登录')
        if not self.login():  # 登录
            return
        self.get_infomation()  # 获取用户信息
        print(f'{character}开始签到')
        self.check_in()
        print(f'{character}开始领取签到任务奖励')
        self.receive_check_in_task_rewards()
        print(f'{character}开始领取分红金')
        self.receive_bonus()
        self.get_infomation()  # 获取用户信息


def main():
    if not ck_list:
        print('没有获取到账号！')
        return
    print(f'获取到{len(ck_list)}个账号！')
    for index, ck in enumerate(ck_list):
        print(f'*****第{index + 1}个账号*****')
        XiAiBang(ck, index).main()
        print('')


if __name__ == '__main__':
    main()
    sys.exit()
