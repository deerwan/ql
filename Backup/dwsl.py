# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2023/7/6 12:24
# @Author  : ziyou
# -------------------------------
# cron "1 8,10,12,15,18,22 * * *" script-path=xxx.py,tag=匹配cron用
# const $ = new Env('得物森林')
# 抓包获取 x_auth_token
# 得物森林
# export dewu_x_auth_token='Bearer ey**&Bearer ey**',多账号使用换行或&
# 青龙拉取命令 ql raw https://raw.githubusercontent.com/q7q7q7q7q7q7q7/ziyou/main/%E5%BE%97%E7%89%A9%E6%A3%AE%E6%9E%97.py
# 第一个账号助力作者，其余账号依ck顺序助力
# https://t.me/q7q7q7q7q7q7q7_ziyou


import os
import random
import re
import sys
import time
import requests
from urllib.parse import urlparse, parse_qs

X_AUTH_TOKEN = []
SHARE_CODE_LIST = []
AUTHOR_SHARE_CODE_LIST = []

# X_AUTH_TOKEN = ['Bearer eyJhbGciOi*******',
#                 'Bearer eyJhbGciOi*******', ]

dewu_x_auth_token = os.getenv("dewu_x_auth_token")
if dewu_x_auth_token:
    X_AUTH_TOKEN += dewu_x_auth_token.replace("&", "\n").split("\n")


# 下载作者的助力码
def download_author_share_code():
    global AUTHOR_SHARE_CODE_LIST
    response = requests.get('https://netcut.cn/p/d3436822ba03c0c3')
    _list = re.findall(r'"note_content":"(.*?)"', response.text)
    if _list:
        share_code_list = _list[0].split(r'\n')
        AUTHOR_SHARE_CODE_LIST += share_code_list


# 获得url params 中键为key的值
def get_url_key_value(url, key):
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    _dict = {k: v[0] if len(v) == 1 else v for k, v in query_params.items()}
    key_value = _dict.get(key)
    return key_value


class DeWu:
    WATERTING_G: int = 40  # 每次浇水克数
    REMAINING_G: int = 1800  # 最后浇水剩余不超过的克数
    User_Agent = "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3"

    def __init__(self, x_auth_token, index, waterting_g=WATERTING_G, remaining_g=REMAINING_G, user_agent=User_Agent):
        self.index = index
        self.waterting_g = waterting_g  # 每次浇水克数
        self.remaining_g = remaining_g  # 最后浇水剩余不超过的克数
        self.session = requests.Session()
        self.headers = {'appVersion': '5.24.5', 'SK': '', 'User-Agent': user_agent, 'x-auth-token': x_auth_token}
        self.tree_id = 0  # 树的id
        self.tasks_completed_number = 0  # 任务完成数
        self.cumulative_tasks_list = []  # 累计计任务列表
        self.tasks_dict_list = []  # 任务字典列表
        self.is_team_tree = False  # 是否是团队树

    # 种树奖品
    def tree_info(self):
        url = 'https://app.dewu.com/hacking-tree/v1/user/target/info'
        response = self.session.get(url, headers=self.headers)
        response_dict = response.json()
        # print(response_dict)
        if response_dict.get('code') == 200:
            name = response_dict.get('data').get('name')
            level = response_dict.get('data').get('level')
            return name, level
        print(response_dict.get('msg'))
        return '', ''

    # 判断是否是团队树
    def determine_whether_is_team_tree(self):
        url = 'https://app.dewu.com/hacking-tree/v1/team/info'
        response = self.session.get(url, headers=self.headers)
        response_dict = response.json()
        # print(response_dict)
        if response_dict.get('data').get('show') is True and response_dict.get('data').get('teamTreeId'):
            self.is_team_tree = True

    # 领潮金币签到
    def check_in(self):
        url = 'https://app.dewu.com/hacking-game-center/v1/sign/sign'
        response = self.session.post(url, headers=self.headers)
        response_dict = response.json()
        # print(response_dict)
        if response_dict.get('code') == 200:
            print(f"签到成功！")
            return
        print(f"签到失败！ {response_dict.get('msg')}")

    # 水滴7天签到
    def droplet_check_in(self):
        url = 'https://app.dewu.com/hacking-tree/v1/sign/sign_in'
        response = self.session.post(url, headers=self.headers)
        response_dict = response.json()
        # print(response_dict)
        if response_dict.get('code') == 200:
            # 暂时设置，看看礼盒是什么先
            print(f"签到成功,获得{response_dict.get('data').get('Num')}g水滴")
            return
        print(f"签到失败！ {response_dict.get('msg')}")

    # 领取气泡水滴
    def receive_droplet_extra(self):
        temporary_number = 0
        countdown_time = 0
        while True:
            url = 'https://app.dewu.com/hacking-tree/v1/droplet-extra/info'
            response = self.session.get(url, headers=self.headers)
            response_dict = response.json()
            # print(response_dict)
            if response_dict.get('code') != 200:
                print(f"获取气泡水滴信息失败! {response_dict}")
                return
            if response_dict.get('data').get('receivable') is True:  # 判断是否能领取
                if response_dict.get('data').get('dailyExtra'):  # 第一次领取时
                    water_droplet_number = response_dict.get('data').get('dailyExtra').get('totalDroplet')
                else:  # 第二次领取时
                    water_droplet_number = response_dict.get('data').get('onlineExtra').get('totalDroplet')
                # 如果二者不相等，说明浇水成功 但奖励有变化 继续浇水
                if temporary_number != water_droplet_number:  # 如果二者相等，说明浇水成功 但奖励没变化 不再浇水 直接领取
                    temporary_number = water_droplet_number
                    if water_droplet_number < 60:
                        print(f'当前气泡水滴{water_droplet_number}g，未满，开始浇水')
                        if self.waterting():  # 成功浇水 继续 否则 直接领取
                            time.sleep(0.5)
                            continue  # 浇水成功后查询信息
                print(f"当前可领取气泡水滴{water_droplet_number}g")
                url = 'https://app.dewu.com/hacking-tree/v1/droplet-extra/receive'
                response = self.session.post(url, headers=self.headers)
                response_dict = response.json()
                # print(response_dict)
                if response_dict.get('code') != 200:
                    countdown_time += 60
                    if countdown_time > 60:  # 已经等待过60s，任为领取成功，退出
                        print(f"领取气泡水滴失败! {response_dict}")
                        return
                    print(f'等待{countdown_time}秒后领取')
                    time.sleep(countdown_time)
                    continue
                print(f"领取气泡水滴成功! 获得{response_dict.get('data').get('totalDroplet')}g水滴")
                countdown_time = 0  # 领取成功，重置等待时间
            else:  # 今天不可领取了，退出
                water_droplet_number = response_dict.get('data').get('dailyExtra').get('totalDroplet')
                print(f"{response_dict.get('data').get('dailyExtra').get('popTitle')},"
                      f"已经积攒{water_droplet_number}g水滴!")
                return

    # 浇水充满气泡水滴
    def waterting_droplet_extra(self):
        while True:
            url = 'https://app.dewu.com/hacking-tree/v1/droplet-extra/info'
            response = self.session.get(url, headers=self.headers)
            response_dict = response.json()
            # print(response_dict)
            count = response_dict.get('data').get('dailyExtra').get('times')
            if not count:
                print(f"气泡水滴已充满，明日可领取{response_dict.get('data').get('dailyExtra').get('totalDroplet')}g")
                return
            for _ in range(count):
                if not self.waterting():  # 无法浇水时退出
                    return
                time.sleep(0.5)

    # 领取木桶水滴,200秒满一次,每天领取3次
    def receive_bucket_droplet(self):
        url = 'https://app.dewu.com/hacking-tree/v1/droplet/get_generate_droplet'
        response = self.session.post(url, headers=self.headers)
        response_dict = response.json()
        # print(response_dict)
        if response_dict.get('code') != 200:
            print(f"领取木桶水滴失败! {response_dict}")
            return
        print(f"领取木桶水滴成功! 获得{response_dict.get('data').get('droplet')}g水滴")

    # 判断木桶水滴是否可以领取
    def judging_bucket_droplet(self):
        url = 'https://app.dewu.com/hacking-tree/v1/droplet/generate_info'
        response = self.session.get(url, headers=self.headers)
        response_dict = response.json()
        # print(response_dict)
        if response_dict.get('data').get('currentDroplet') == 100:
            print(f"今天已领取木桶水滴{response_dict.get('data').get('getTimes')}次")
            self.receive_bucket_droplet()
            return True
        return False

    # 获取助力码
    def get_shared_code(self):
        url = 'https://app.dewu.com/hacking-tree/v1/keyword/gen'
        response = self.session.post(url, headers=self.headers)
        response_dict = response.json()
        # print(response_dict)
        if response_dict.get('code') != 200:
            print(f"获取助力码失败! {response_dict}")
            return
        keyword_desc = response_dict.get('data').get('keywordDesc').replace('\n', '')
        print(f"获取助力码成功! {keyword_desc}")

    # 获得当前水滴数
    def get_droplet_number(self):
        url = 'https://app.dewu.com/hacking-tree/v1/user/init'
        _json = {"keyword": ""}
        response = self.session.post(url, headers=self.headers, json=_json)
        response_dict = response.json()
        # print(response_dict)
        droplet_number = response_dict.get('data').get('droplet')
        return droplet_number

    # 领取累计任务奖励
    def receive_cumulative_tasks_reward(self, condition):
        url = 'https://app.dewu.com/hacking-tree/v1/task/extra'
        _json = {'condition': condition}
        response = self.session.post(url, headers=self.headers, json=_json)
        response_dict = response.json()
        # print(response_dict)
        if response_dict.get('code') != 200:
            print(f"领取累计任务奖励失败! {response_dict}")
            return
        print(f"领取累计任务奖励成功! 获得{response_dict.get('data').get('num')}g水滴")

    # 领取任务奖励
    def receive_task_reward(self, classify, task_id, task_type):
        time.sleep(0.2)
        url = 'https://app.dewu.com/hacking-tree/v1/task/receive'
        if task_type in [251, ]:
            _json = {'classify': classify, 'taskId': task_id, 'completeFlag': 1}
        else:
            _json = {'classify': classify, 'taskId': task_id}
        response = self.session.post(url, headers=self.headers, json=_json)
        response_dict = response.json()
        # print(response_dict)
        if response_dict.get('code') != 200:
            print(f"领取任务奖励失败! {response_dict}")
            return
        print(f"领取任务奖励成功! 获得{response_dict.get('data').get('num')}g水滴")

    # 领取浇水奖励
    def receive_watering_reward(self):
        url = 'https://app.dewu.com/hacking-tree/v1/tree/get_watering_reward'
        _json = {'promote': ''}
        response = self.session.post(url, headers=self.headers, json=_json)
        response_dict = response.json()
        # print(response_dict)
        if response_dict.get('code') != 200:
            print(f"领取浇水奖励失败! {response_dict}")
            return
        print(f"领取浇水奖励成功! 获得{response_dict.get('data').get('currentWateringReward').get('rewardNum')}g水滴")

    # 领取等级奖励
    def receive_level_reward(self):
        while True:
            url = 'https://app.dewu.com/hacking-tree/v1/tree/get_level_reward'
            _json = {'promote': ''}
            response = self.session.post(url, headers=self.headers, json=_json)
            response_dict = response.json()
            # print(response_dict)
            if response_dict.get('code') != 200 or response_dict.get('data') is None:
                print(f"领取等级奖励失败! {response_dict.get('msg')}")
                return
            level = response_dict.get('data').get('levelReward').get('showLevel') - 1
            reward_num = response_dict.get('data').get('currentLevelReward').get('rewardNum')
            print(f"领取{level}级奖励成功! 获得{reward_num}g水滴")
            if response_dict.get('data').get('levelReward').get('isComplete') is False:
                return
            time.sleep(1)

    # 浇水
    def waterting(self):
        if self.is_team_tree is True:  # 如果是团队树，使用团队浇水
            return self.team_waterting()
        url = 'https://app.dewu.com/hacking-tree/v1/tree/watering'
        response = self.session.post(url, headers=self.headers)
        response_dict = response.json()
        # print(response_dict)
        if response_dict.get('code') != 200:
            print(f"浇水失败! {response_dict}")
            return False
        print(f"成功浇水{self.waterting_g}g")
        if response_dict.get('data').get('nextWateringTimes') == 0:
            print('开始领取浇水奖励')
            time.sleep(1)
            self.receive_watering_reward()
        return True

    # 团队浇水
    def team_waterting(self):
        url = 'https://app.dewu.com/hacking-tree/v1/team/tree/watering'
        _json = {"teamTreeId": self.tree_id}
        response = self.session.post(url, headers=self.headers, json=_json)
        response_dict = response.json()
        # print(response_dict)
        if response_dict.get('code') != 200:
            print(f"浇水失败! {response_dict}")
            return False
        print(f"成功浇水{self.waterting_g}g")
        if response_dict.get('data').get('nextWateringTimes') == 0:
            print('开始领取浇水奖励')
            time.sleep(1)
            self.receive_watering_reward()
        return True

    # 多次执行浇水，领取浇水奖励
    def execute_receive_watering_reward(self):
        while True:
            url = 'https://app.dewu.com/hacking-tree/v1/tree/get_tree_info'
            response = self.session.get(url, headers=self.headers)
            response_dict = response.json()
            # print(response_dict)
            if response_dict.get('code') != 200:
                print(f"获取种树进度失败! {response_dict}")
                return
            count = response_dict.get('data').get('nextWateringTimes')  # 获取浇水奖励还需要的浇水次数
            if response_dict.get('data').get('wateringReward') is None or count <= 0:  # 没有奖励时退出
                return
            for _ in range(count):
                if not self.waterting():  # 无法浇水时退出
                    return
                time.sleep(0.5)

    # 浇水直到少于 指定克数
    def waterting_until_less_than(self):
        droplet_number = self.get_droplet_number()
        if droplet_number > self.remaining_g:
            count = int((droplet_number - self.remaining_g) / self.waterting_g)
            for _ in range(count + 1):
                if not self.waterting():  # 无法浇水时退出
                    return
                time.sleep(0.5)

    # 提交任务完成状态
    def submit_task_completion_status(self, _json):
        url = 'https://app.dewu.com/hacking-task/v1/task/commit'
        response = self.session.post(url, headers=self.headers, json=_json)
        response_dict = response.json()
        # print(response_dict)
        if response_dict.get('code') == 200:
            return True
        return False

    # 获取任务列表
    def get_task_list(self):
        url = 'https://app.dewu.com/hacking-tree/v1/task/list'
        response = self.session.get(url, headers=self.headers)
        response_dict = response.json()
        # print(response_dict)
        if response_dict.get('code') == 200:
            self.tasks_completed_number = response_dict.get('data').get('userStep')  # 任务完成数量
            self.cumulative_tasks_list = response_dict.get('data').get('extraAwardList')  # 累计任务列表
            self.tasks_dict_list = response_dict.get('data').get('taskList')  # 任务列表
            return True

    # 水滴大放送任务步骤1
    def task_obtain(self, task_id, task_type):
        url = 'https://app.dewu.com/hacking-task/v1/task/obtain'
        _json = {'taskId': task_id, 'taskType': task_type}
        response = self.session.post(url, headers=self.headers, json=_json)
        response_dict = response.json()
        # print(response_dict)
        if response_dict.get('code') == 200 and response_dict.get('status') == 200:
            return True
        return False

    # 浏览任务开始  且等待16s TaskType有变化  浏览15s会场会变成16
    def task_commit_pre(self, _json):
        url = 'https://app.dewu.com/hacking-task/v1/task/pre_commit'
        response = self.session.post(url, headers=self.headers, json=_json)
        response_dict = response.json()
        # print(response_dict)
        if response_dict.get('code') == 200 and response_dict.get('status') == 200:
            return True
        return False

    # 执行任务
    def execute_task(self):
        self.get_task_list()  # 刷新任务列表
        for tasks_dict in self.tasks_dict_list:
            if tasks_dict.get('isReceiveReward') is True:  # 今天不能进行操作了，跳过
                continue
            if tasks_dict.get('rewardCount') >= 3000:  # 获取水滴超过3000的，需要下单，跳过
                continue
            # 'taskId' 任务ID
            # 'taskName' 任务名字
            # 'isComplete' 是否未完成
            # 'isReceiveReward' 完成后是否领取奖励
            # 'taskType'任务类型
            # 'rewardCount' 完成任务所获得的奖励水滴
            # 'isObtain' 是否完成任务前置要求
            # 'jumpUrl' 是否完成任务前置要求
            classify = tasks_dict.get('classify')
            task_id = tasks_dict.get('taskId')
            task_
