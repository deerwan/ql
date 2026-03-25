"""
项目名: 熊猫代理
版本号：V1.00
作者: 幻生
注册地址: http://www.xiongmaodaili.com
脚本功能:
    自动签到获取积分

配置参数:
    - `xmdl` 格式: 手机号#密码#昵称，以`&`或换行符分隔或者多个同名环境变量。


==================================================


仅用于测试和学习研究，禁止用于商业用途，不能保证其合法性，准确性，完整性和有效性，请根据情况自行判断；您必须在下载后的24小时内从计算机或手机中完全删除以上内容。

如果任何单位或个人认为该项目的脚本可能涉嫌侵犯其权利，则应及时通知并提供身份证明，所有权证明，我们将在收到认证文件后删除相关脚本。

==================================================

脚本依赖：
    - Python依赖如下：
        - requests
        - requests_toolbelt

---------------------------------------------------
"""
import os
import re
import requests
import urllib3
from requests_toolbelt.multipart.encoder import MultipartEncoder

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def login(account, password):
    url = "http://www.xiongmaodaili.com/xiongmao-web/user/login"
    headers = {
        "Host": "www.xiongmaodaili.com",
        "Proxy-Connection": "keep-alive",
        "Accept": "application/json, text/plain, */*",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.6261.95 Safari/537.36",
        "Origin": "http://www.xiongmaodaili.com",
        "Referer": "http://www.xiongmaodaili.com/",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9",
    }
    data = MultipartEncoder(
        fields={"account": account, "password": password, "originType": "1"}
    )
    headers["Content-Type"] = data.content_type
    response = requests.post(
        url,
        headers=headers,
        data=data,
        cookies={"invitationCode": "2A609042-FAC9-4943-BBF7-04A4D9F471A3"},
        verify=False,
    )
    if response.json()["code"] == "0":
        return response.cookies
    else:
        print("登录失败", response.json()["msg"])
        return None


def sign_in(cookies):
    url = "http://www.xiongmaodaili.com/xiongmao-web/points/receivePoints?signInDay=1"
    headers = {
        "Host": "www.xiongmaodaili.com",
        "Proxy-Connection": "keep-alive",
        "Accept": "*/*",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.6261.95 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": "http://www.xiongmaodaili.com/IntegralMall",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9",
    }
    response = requests.get(url, headers=headers, cookies=cookies, verify=False)
    print(response.json()["msg"])


def get_user_points(cookies):
    url = "http://www.xiongmaodaili.com/xiongmao-web/points/getUserPoints"
    headers = {
        "Host": "www.xiongmaodaili.com",
        "Proxy-Connection": "keep-alive",
        "Accept": "*/*",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.6261.95 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": "http://www.xiongmaodaili.com/IntegralMall",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9",
    }
    response = requests.get(url, headers=headers, cookies=cookies, verify=False)
    print("当前账号积分：", response.json()["obj"])


if __name__ == "__main__":
    tokens = []
    if os.getenv("xmdl"):
        tokens = re.split(r"&|\n", os.getenv("xmdl"))
    if len(tokens) == 0:
        print(f"当前无账号，请先配置下 账号！")
    else:
        index_counter = 0
        for token in tokens:
            if len(token.split("#")) > 1:
                account = token.split("#")[0]
                password = token.split("#")[1]
                # 在提交任务前递增计数器并分配给任务
                index_counter += 1
                cookies = login(account, password)
                if cookies:
                    sign_in(cookies)
                    get_user_points(cookies)
            else:
                print(f"账号[{index_counter}] 格式不正确，无法正常执行任务！")
