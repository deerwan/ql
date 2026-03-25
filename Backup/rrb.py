# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2023/8/24 21:34
# @Author  : ziyou
# -------------------------------
# 微信打开 阅读地址 http://ebb1696246394221.sunsunblue.cloud/user/index.html?mid=1708804592407543808
# cron "15 10-12 * * *" script-path=xxx.py,tag=匹配cron用
# const $ = new Env('微信阅读_人人帮')
# 抓包 http://ebb.vinse.cn/api 类似网址下的  un#uid#token
# 微信阅读_人人帮
# export renrenbang_ck='un#uid#token&un#uid#token'
# export renrenbang_ck='18*********#16947027******#3a6256e1ea9********',多账号使用换行或&
# 运行前看几篇过检测，后面基本不会再出检测了
# 也可以使用 pushplus http://www.pushplus.plus/ 发送过检测通知 填写pushplus的token
# 选填 export push_token='****'
# 一天运行一两次


import sys
import time
import random
import requests
import re

import os
from retrying import retry

ck_list = []
PUSH_TOKEN = ''

ck_list_str = os.getenv("renrenbang_ck")
if ck_list_str:
    ck_list += ck_list_str.replace("&", "\n").split("\n")

push_token_list_str = os.getenv("push_token")
if push_token_list_str:
    PUSH_TOKEN = push_token_list_str.replace("&", "\n").split("\n")[0]


# 请求文章地址
@retry(stop_max_attempt_number=3, wait_random_min=3000,
       wait_random_max=5000)  # 重试3次，重试等待时间3s到5s随机
def parsing_web_pages(url):
    # print('开始解析网页')
    try:
        response = requests.get(url, timeout=(10, 10))
        # print(response.text)
        return response.text
    except Exception as e:
        if e:
            pass


# 获得文章的相关信息
def get_name(url):
    name_1_list = []
    for _ in range(3):
        response_text = parsing_web_pages(url)
        pattern = r'nickname.*?>([^<>]+?)</strong>'
        name_1_list = re.findall(pattern, response_text)
        name_2_list = re.findall('name = "(.*?)"', response_text)
        wechat_name_list = re.findall(
            '<span class="profile_meta_value">(.*?)</span>', response_text)
        if not wechat_name_list:
            wechat_name_list = ['未获取到']
        if name_1_list:
            # print(re_list)
            return name_1_list[0], wechat_name_list[0]
        if name_2_list:
            # print(re_list)
            return name_2_list[0], wechat_name_list[0]
        time.sleep(3)
    print(f'寻找公众号名称失败 {name_1_list}')
    return '', ''


# 获取 worktile_id
def generate_worktile_id():
    response = requests.get('https://request.worktile.com/')
    set_cookie_header = response.headers.get('Set-Cookie')
    # 使用正则表达式提取 SID 值
    sid_match = re.search(r"sid=([^;]+)", set_cookie_header)
    if sid_match:
        sid_value = sid_match.group(1)
        cookies = {'sid': sid_value}
        requests.get('https://request.worktile.com/create', cookies=cookies)

        response = requests.get('https://request.worktile.com/api/requests/',
                                cookies=cookies)
        # print(response.json())
        response_dict = response.json()
        if data := response_dict.get('data')[0]:
            return data.get('id')


# 发送pushplus通知
def send_pushplus(push_token, article_url, worktile_id):
    headers = {"Content-Type": "application/json"}
    _json = {"token": push_token,
             "title": "微信文章检测",
             "content": f'<a href="{article_url}">点击验证跳转</a>\n\n'
                        f'<a href="https://request.worktile.com/{worktile_id}">点击完成验证跳转</a>',
             "template": "html"}
    response = requests.post("http://www.pushplus.plus/send", headers=headers,
                             json=_json)
    response_dict = response.json()
    # print(response_dict)
    if response_dict.get('code') == 200:
        print("pushplus通知发送成功")
        return True
    print(f"pushplus通知发送失败 {response_dict.get('msg')}")
    return False


# 等待验证
def waiting_verification(push_token, article_url):
    _id = generate_worktile_id()
    if not send_pushplus(push_token, article_url, _id):
        return False
    _time = 60
    print(f'请在{_time}秒内微信打开文章链接过验证')
    print(f'等待{_time}秒')
    for i in range(_time):
        response = requests.get(
            f"https://request.worktile.com/api/requests/{_id}/inspects")
        response_dict = response.json()
        if response_dict.get('data').get('inspects'):
            return True
        time.sleep(1)
    return False


class YueDu6:
    def __init__(self, ck, index):
        self.un, self.uid, self.token = ck.split('#')
        self.headers = {'un': self.un,
                        'uid': self.uid,
                        'platform': '0',
                        'token': self.token, }
        self.detection_list = [
            ['欢乐的小鱼儿', 'gh_cf733a65ca3d', 'Mzg2Mzk3Mjk5NQ=='],
        ]  # 订阅号名称，微信id，biz

    # 请求个人信息
    def requests_infomation(self):
        url = f"http://ebb.vinse.cn/api/user/info"
        headers = self.headers
        _json = {"pageSize": 10}
        response = requests.post(url, headers=headers, json=_json)
        response_dict = response.json()
        return response_dict

    # 获取个人信息
    def get_infomation(self):
        response_dict = self.requests_infomation()
        # print(response_dict)
        if response_dict.get('code') == 0:
            nick_name = response_dict.get('result').get('nickName')
            integral_current = response_dict.get('result').get(
                'integralCurrent')
            print(f'{nick_name} 帮豆：{integral_current}')
            return True
        return False

    # 签到
    def check_in(self):
        url = f"http://ebb.vinse.cn/api/user/getUserSignDays"
        headers = self.headers
        _json = {"pageSize": 10}
        response = requests.post(url, headers=headers, json=_json)
        response_dict = response.json()
        # print(response_dict)
        if int(response_dict.get('result').get('signStatus')) == 1:
            print("今天已经签到过了")
            return
        url = f"http://ebb.vinse.cn/api/user/sign"
        _json = {"pageSize": 10}
        response = requests.post(url, headers=headers, json=_json)
        response_dict = response.json()
        # print(response_dict)
        if response_dict.get('code') == 0:
            print(
                f'签到成功，获得{response_dict.get("result").get("point")}帮豆')
            return
        print(f'签到失败 {response_dict}')

    # 获取阅读地址
    def get_read_url(self):
        url = f'https://u.cocozx.cn/ipa/read/getEntryUrl?fr=ebb0726&uid={self.uid}'
        response = requests.get(url)
        response_dict = response.json()
        # print(response_dict)
        if int(response_dict.get('result').get('status')) == 2:
            print(f'你的账号被拉黑了，明天再来看看吧')
            return
        return response_dict.get('result').get('url')

    # 阅读文章
    def read_article(self):
        task_url = self.get_read_url()
        if not task_url:
            return
        nested_list = self.detection_list
        detection_list = [item for sublist in nested_list for item in
                          sublist]  # 解包检测文章的 订阅号名称，微信id，biz
        t = re.findall(r'mr(.*?)\.', task_url)[0]
        host = re.findall(r'//(.*/?)/', task_url)[0]
        headers = {'Host': 'u.cocozx.cn', 'Connection': 'keep-alive',
                   'Content-Length': '93',
                   'Accept': 'application/json, text/javascript, */*; q=0.01',
                   'User-Agent': 'Mozilla/5.0 (Linux; Android 13; 22041211AC Build/TP1A.220624.014; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/111.0.5563.116 Mobile Safari/537.36 XWEB/5235 MMWEBSDK/20230701 MMWEBID/544 MicroMessenger/8.0.40.2420(0x28002851) WeChat/arm64 Weixin NetType/WIFI Language/zh_CN ABI/arm64',
                   'Content-Type': 'application/json; charset=UTF-8',
                   'Origin': f'http://{host}',
                   'X-Requested-With': 'com.tencent.mm',
                   # 'Accept-Encoding': 'gzip, deflate',
                   'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7'}
        _json = {"un": None, "token": None, "pageSize": 20}
        url = f'http://u.cocozx.cn/api/common/ustr?t={t}'
        response = requests.post(url, headers=headers, json=_json)
        response_dict = response.json()
        _str = response_dict.get('result', {}).get('str')
        group_list = re.findall(r'group=(.*?)$', _str)
        group = ''
        if group_list:
            group = group_list[0]
        repeat_request_signal = 0  # 用来标记 连续两次 请求失败，说明可能黑号了
        for i in range(60):
            url = 'http://u.cocozx.cn/ipa/read/read'
            _json = {"fr": "ebb0726", "uid": self.uid, "group": str(group),
                     "un": None, "token": None, "pageSize": 20}
            response = requests.post(url, headers=headers, json=_json)
            response_dict = response.json()
            if response_dict.get('code') != 0 or response_dict.get(
                    'result') is None:
                print(f"{i + 1}：获取文章失败 {response_dict}")
                return
            # print(response_dict)
            status = response_dict.get('result', {}).get('status')
            if status == 10:
                # print(f'继续未完成的阅读任务')
                pass
            elif status == 30:
                repeat_request_signal += 1
                if repeat_request_signal >= 2:
                    print('连续两次获取文章报30状态，可能是黑号了，手动去看看')
                    break
                print(f"{i + 1}：即将重新请求获取文章")
                _time = 10
                print(f'等待{_time}秒')
                time.sleep(_time)
                continue
            elif status == 40:
                print("本次推荐文章已全部读完")
                return
            elif status == 50:
                print(f'你的账号被拉黑了，明天再来看看吧')
                return
            elif status == 60:
                print("已经全部阅读完了")
                return
            elif status == 70:
                print("下一轮还未开启")
                return
            else:
                print(f"未知状态 {response_dict}")
                return
            # print(response_dict)
            article_url = response_dict.get('result').get('url')
            if not article_url:
                return
            print(f"{i + 1}：获取文章成功 {article_url}")
            __biz_list = re.findall('__biz=(.+?)&', article_url)
            __biz = __biz_list[0] if __biz_list else None
            mid_list = re.findall('mid=(.+?)&', article_url)
            mid = mid_list[0] if mid_list else None
            name, wechat_name = get_name(article_url)
            print(
                f'订阅号名称：{name} 微信号：{wechat_name} mid：{mid} biz：{__biz}')
            if __biz in detection_list or name in detection_list or wechat_name in detection_list:
                print('该文章为检测文章')

                if PUSH_TOKEN:
                    print('即将通过pushplus发送给你')
                    if not waiting_verification(PUSH_TOKEN, article_url):
                        print('检测文章微信点击未验证，任务结束')
                        break
                    print('微信点击验证成功')
                else:
                    _time = 60
                    print(
                        f'请在{_time}秒内微信打开文章链接过验证 {article_url}')
                    print(f'等待{_time}秒')
                    time.sleep(_time)

            _time = random.randint(7, 9)
            print(f'等待{_time}秒')
            time.sleep(_time)
            url = f"http://u.cocozx.cn/ipa/read/submit"
            _json = {"fr": "ebb0726", "uid": self.uid, "group": str(group),
                     "un": None, "token": None, "pageSize": 20}
            response = requests.post(url, headers=headers, json=_json)
            response_dict = response.json()
            # print(response_dict)
            if response_dict.get('code') != 0:
                print(f'完成阅读失败 {response_dict}')
                return
            day_count = response_dict.get('result').get('dayCount')
            print(f"完成阅读成功，今日已阅读{day_count}篇")
            # time.sleep(3)

    # 搜狐助力
    def sohu_helps(self):
        headers = self.headers
        url = 'http://ebb.vinse.cn/api/task/getTaskType'
        _json = {"pageSize": 10}
        response = requests.post(url, headers=headers, json=_json)
        response_dict = response.json()
        task_list = response_dict.get('result').get('taskTypes')
        task_type_list = []
        for task in task_list:
            if task.get('businessType') == 5:
                task_type_list.append(task.get('taskType'))
        for task_type in task_type_list:
            for i in range(20):
                url = 'http://ebb.vinse.cn/api/task/v2/getTask'
                _json = {
                    "imgUrl": "http://juyouimg.oss-cn-zhangjiakou.aliyuncs.com/15/task/QoExACdjJc.png",
                    "businessType": 5, "taskType": f"{task_type}",
                    "pageSize": 10}
                response = requests.post(url, headers=headers, json=_json)
                response_dict = response.json()
                if response_dict.get('code') != 0:
                    print(response_dict.get("msg"))
                    break
                commit_num = response_dict.get('result').get('commitNum')
                print(f"{i + 1}：获取视频成功 已完成{commit_num}次")
                _time = random.randint(90, 100)
                print(f'等待{_time}秒')
                time.sleep(_time)
                url = 'http://ebb.vinse.cn/api/task/v2/commitTask'
                _json = {
                    "imgUrl": "http://juyouimg.oss-cn-zhangjiakou.aliyuncs.com/15/task/QoExACdjJc.png",
                    "businessType": 5, "taskType": f"{task_type}",
                    "pageSize": 10}
                response = requests.post(url, headers=headers, json=_json)
                response_dict = response.json()
                if response_dict.get('code') != 0:
                    print(f'观看失败 {response_dict.get("msg")}')
                    break
                print('观看成功')
                time.sleep(0.5)

    # 提现
    def withdraw(self):
        response_dict = self.requests_infomation()
        integral_current = response_dict.get('result', {}).get(
            'integralCurrent')
        print(f'当前金币：{integral_current}')
        if integral_current < 5000:
            print(f'金币少于5000不可提现')
            return
        withdraw_dict = {100000: "100000", 50000: "50000", 10000: "10000",
                         5000: "5000"}
        money = 0
        for key, value in withdraw_dict.items():
            if integral_current >= key:
                money = int(value)
                break
        print(f'选择提现金币：{money}')
        url = f"http://ebb.vinse.cn/apiuser/aliWd"
        headers = self.headers
        _json = {"val": money, "pageSize": 10}
        response = requests.post(url, headers=headers, json=_json)
        response_dict = response.json()
        print(response_dict)

    def main(self):
        character = '★★'
        if not self.get_infomation():
            return
        print(f'{character}开始签到')
        self.check_in()  # 签到
        print(f'{character}开始执行阅读文章')
        for _ in range(2):
            self.read_article()  # 阅读文章
            time.sleep(5)
        # print(f'{character}开始执行搜狐助力（收益次日结算）')
        # self.sohu_helps()
        print(f'{character}开始提现')
        self.withdraw()  # 提现


def main():
    if not ck_list:
        print('没有获取到账号！')
        return
    print(f'获取到{len(ck_list)}个账号！')
    for index, ck in enumerate(ck_list):
        print(f'*****第{index + 1}个账号*****')
        YueDu6(ck, index).main()
        print('')


if __name__ == '__main__':
    main()
    sys.exit()
