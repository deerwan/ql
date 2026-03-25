'''
美添赚
活动入口,微信打开：http://tg.1693182678.api.mengmorwpt2.cn/h5_share/ads/tg?user_id=115772
活动入口,微信打开：http://tg.1693182678.api.mengmorwpt2.cn/h5_share/ads/tg?user_id=115772
打开活动入口，抓包的任意接口cookies中的Authorization参数,

填到脚本最下方的,脚本最下方的,脚本最下方的 CKList配置中,把xxxx替换成你的Authorization参数
填到脚本最最下方的,脚本最最下方的,脚本最最下方的 CKList配置中,把xxxx替换成你的Authorization参数
填到脚本最最最下方的,脚本最最最下方的,脚本最最下方的 CKList配置中,把xxxx替换成你的Authorization参数

单账户 CKList=[{'Authorization': 'xxxx'}]
多账户CKList=[{'Authorization': 'xxxx'},{'Authorization': 'xxxx'},{'Authorization': 'xxxx'},]

其他参数说明（脚本最下方填写参数）

const $ = new Env("美添赚")
内置推送第三方 wxpusher（脚本最下方填写参数）
appToken = 'xxx'  # 这个是填wxpusher的appToken
topicIds = 0  # 这个是wxpusher的topicIds改成你自己的,在主题管理里能看到应用的topicIds
具体使用方法请看文档地址：https://wxpusher.zjiecode.com/docs/#/

回调服务器（脚本最下方填写参数）
key=''这个是回调服务器的key
key访问http://175.24.153.42:8882/getkey获取

定时运行每小时一次
达到标准自动提现
'''
import time
import requests
import random
import re
checkDict={
'MzkzNjI3NDAwOA==':['木新领袋管家','gh_04e096463e91'],
}
def getmsg():
    lvsion = 'v1.5'
    r=''
    try:
        u='http://175.24.153.42:8881/getmsg'
        p={'type':'mtzyd'}
        r=requests.get(u,params=p)
        rj=r.json()
        version=rj.get('version')
        gdict = rj.get('gdict')
        gmmsg = rj.get('gmmsg')
        print('系统公告:',gmmsg)
        print(f'最新版本{version},当前版本{lvsion}')
        print(f'系统的公众号字典{len(gdict)}个:{gdict}')
        print(f'本脚本公众号字典{len(checkDict.values())}个:{list(checkDict.keys())}')
        print('='*50)
    except Exception as e:
        print(r.text)
        print(e)
        print('公告服务器异常')
def printjson(text):
    if printf==0:
        return
    print(text)
def push(title,link,text,type):
    str1='''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>TITLE</title>
<style type=text/css>
   body {
   	background-image: linear-gradient(120deg, #fdfbfb 0%, #a5d0e5 100%);
    background-size: 300%;
    animation: bgAnimation 6s linear infinite;
}
@keyframes bgAnimation {
    0% {background-position: 0% 50%;}
    50% {background-position: 100% 50%;}
    100% {background-position: 0% 50%;}
}
</style>
</head>
<body>
<p>TEXT</p><br>
<p><a href="http://175.24.153.42:8882/lookstatus?key=KEY&type=TYPE">查看状态</a></p><br>
<p><a href="http://175.24.153.42:8882/lookwxarticle?key=KEY&type=TYPE&wxurl=LINK">点击阅读检测文章</a></p><br>
</body>
</html>
    '''
    content=str1.replace('TITTLE',title).replace('LINK',link).replace('TEXT',text).replace('TYPE',type).replace('KEY',key)
    datapust = {
      "appToken":appToken,
      "content":content,
      "summary":title,
      "contentType":2,
      "topicIds":[topicIds],
    }
    urlpust = 'http://wxpusher.zjiecode.com/api/send/message'
    try:
        p = requests.post(url=urlpust, json=datapust).text
        printjson(p)
        print('推送成功')
        return True
    except:
        print('推送失败！')
        return False

def getinfo(link):
    try:
        r=requests.get(link)
        #print(r.text)
        html = re.sub('\s', '', r.text)
        biz=re.findall('varbiz="(.*?)"\|\|', html)
        if biz!=[]:
            biz=biz[0]
        if biz=='' or biz==[]:
            if '__biz' in link:
                biz = re.findall('__biz=(.*?)&', link)
                if biz != []:
                    biz = biz[0]
        nickname = re.findall('varnickname=htmlDecode\("(.*?)"\);', html)
        if nickname!=[]:
            nickname=nickname[0]
        user_name = re.findall('varuser_name="(.*?)";', html)
        if user_name!=[]:
            user_name=user_name[0]
        msg_title = re.findall("varmsg_title='(.*?)'\.html\(", html)
        if msg_title!=[]:
            msg_title=msg_title[0]
        text=f'公众号唯一标识：{biz}|文章:{msg_title}|作者:{nickname}|账号:{user_name}'
        print(text)
        return nickname,user_name,msg_title,text,biz
    except Exception as e:
        print(e)
        print('异常')
        return False
def setstatus():
    u='http://175.24.153.42:8882/setstatus'
    p={'key':key,'type':'mtzyd','val':'1'}
    r=requests.get(u,params=p)
    printjson(r.text)
    print('设置阅读状态为待阅读')
def getstatus():
    u = 'http://175.24.153.42:8882/getstatus'
    p = {'key':key,'type': 'mtzyd'}
    r = requests.get(u, params=p)
    return r.text
class MTZYD():
    def __init__(self,cg):
        self.headers={
            'Authorization': cg['Authorization'],
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 NetType/WIFI MicroMessenger/7.0.20.1781(0x6700143B) WindowsWechat(0x63090621) XWEB/8351 Flue',
            'content-type': 'application/json',
            'Accept': '*/*',
            'Origin': 'http://71692693186.tt.bendishenghuochwl1.cn',
            'Referer': 'http://71692693186.tt.bendishenghuochwl1.cn/',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh',
        }
    def user_info(self):
        u='http://api.mengmorwpt1.cn/h5_share/user/info'
        r=requests.post(u,headers=self.headers,json={"openid":0})
        printjson(r.text)
        rj=r.json()
        if rj.get('code')==200:
            nickname=rj.get('data').get('nickname')
            points=rj.get('data').get('points')
            used_points = rj.get('data').get('used_points')
            self.sy=points-used_points
            print(f'当前账号：{nickname},总积分积分：{points}，已经提现：{used_points},剩余：{self.sy}')
        else:
            print('获取账号信息异常,ck可能失效请重新获取')
            return False
    def sign(self):
        u='http://api.mengmorwpt1.cn/h5_share/user/sign'
        r = requests.post(u, headers=self.headers, json={"openid": 0})
        printjson(r.text)
        print('签到成功')
    def getMissions(self):
        ''
        u='http://api.mengmorwpt1.cn/h5_share/daily/getMissions'
        r = requests.post(u, headers=self.headers, json={"openid": 0})
        rj = r.json()
        if rj.get('code')!=200:
            printjson(r.text)
            return False
        info=''
        for i in rj.get('data'):
            if i.get('title')=='文章阅读推荐':
                info=i
                break
        if info=='':
            printjson(r.text)
            print('没有找到任务')
            return False
        printjson(info)
        if info.get('left_time')=='开始活动':
            return True
        else:
            print('下次阅读,',end='')
            print(info.get('left_time'))
            return False
    def read_info(self):
        u=f'http://api.mengmorwpt1.cn/h5_share/daily/get_read'
        r = requests.post(u, headers=self.headers, json={"openid": 0})
        printjson(r.text)
        rj = r.json()
        if rj.get('code')==200:
            self.link=rj.get('data').get('link')
        else:
            print('获取阅读链接异常异常')
            return False
    def gettaskinfo(self,infolist):
        for i in infolist:
            if i.get('url'):
                return i
    def read(self):
        print('阅读开始')
        h={
            'Host': 'api.wanjd.cn',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 NetType/WIFI MicroMessenger/7.0.20.1781(0x6700143B) WindowsWechat(0x63090621) XWEB/8351 Flue',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': '*/*',
            'Origin': 'http://uha294070.294070nwq.com.294070u.meitianzhuan2.cn',
            'Referer': 'http://uha294070.294070nwq.com.294070u.meitianzhuan2.cn/',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh',
        }
        self.num=1000
        pt=0
        while True:
            if self.num<=0:
                break
            print('-'*50)
            u1='https://api.wanjd.cn/wxread/articles/tasks'
            p={'href':self.link}
            r=requests.post(u1,headers=h,data=p)
            printjson(r.text)
            rj = r.json()
            code=rj.get('code')
            if code==500:
                print('阅读异常')
                break
            if code==200:
                if pt==0:
                    self.num= len(rj.get('data'))
                    pt=1
                taskinfo=self.gettaskinfo(rj.get('data'))
                url=taskinfo.get('url')
                id=taskinfo.get('id')
                a = getinfo(url)
                if a == False:
                    push('美添赚过检测', url, '文章获取失败', 'mtzyd')
                    return False
                if self.testCheck(a, url) == False:
                    return False
                tsm = random.randint(7, 10)
                print(f'本次模拟读{tsm}秒')
                time.sleep(tsm)
                u1 = 'https://api.wanjd.cn/wxread/articles/three_read'
                p1 = {'id': id, 'href': self.link}
                r = requests.post(u1, headers=h, data=p1)
                printjson(r.text)
                self.num-=1
        curl = 'https://api.wanjd.cn/wxread/articles/check_success'
        cp = {'type': 1, 'href': self.link}
        cr = requests.post(curl, headers=h, data=cp)
        printjson(cr.text)
        print('本次阅读已完成')
    def testCheck(self, a, link):
        if checkDict.get(a[4]) != None:
            setstatus()
            for i in range(60):
                if i % 30 == 0:
                    push('美添赚过检测', link, a[3], 'mtzyd')
                getstatusinfo = getstatus()
                if getstatusinfo == '0':
                    print('过检测文章已经阅读')
                    return True
                elif getstatusinfo == '1':
                    print(f'正在等待过检测文章阅读结果{i}秒。。。')
                    time.sleep(1)
                else:
                    print(getstatusinfo)
                    print('服务器异常')
                    return False
            print('过检测超时中止脚本防止黑号')
            return False
        else:
            return True
    def withdraw(self):
        if self.sy<1000:
            print('没有达到提现标准')
            return False
        u='http://api.mengmorwpt1.cn/h5_share/user/withdraw'
        r=requests.post(u,headers=self.headers)
        print('提现结果',r.text)
    def run(self):
        if self.user_info()==False:
            return False
        self.sign()
        if self.getMissions():
            self.read_info()
            self.read()
            self.user_info()
        self.withdraw()
if __name__ == '__main__':
    printf = 0  # 打印调试日志0不打印，1打印，若运行异常请打开调试
    appToken = 'xxxx'  # 这个是填wxpusher的appToken
    topicIds = 0  # 这个是wxpusher的topicIds改成你自己的
    key = 'xxxx'  # key从这里获取http://175.24.153.42:8882/getkey
    CKList=[
        {'name':'备注','Authorization':'share:login:xxxx'}
    ]
    getmsg()
    for i in CKList:
        api=MTZYD(i)
        api.run()
