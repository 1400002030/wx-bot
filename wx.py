import re
import sys
import threading
import time
from datetime import datetime

import requests


class WeiXin:

    def __init__(self):
        # 公众号登陆账号密码
        self.unm = "p1788831@163.com"
        self.pwd = "jiayou@123"
        self.token = ''
        self.fakeid = ''
        # 字典存储用户与fakeid的关系
        self.users = {}
        self.msg2user_capable = {}
        # session自动处理cookies
        self.session = requests.Session()
        self.session.headers.update({"Host": "mp.weixin.qq.com",
                                     "Referer": "https://mp.weixin.qq.com/",
                                     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36"})

    def get_login_qr(self):
        res = self.session.get("https://mp.weixin.qq.com/")
        self.session.get(
            "https://mp.weixin.qq.com/webpoc/cgi/chat/checkChatPermission?type=15&grayType=random&token=&lang=zh_CN&f=json&ajax=1")
        r = self.session.post("https://mp.weixin.qq.com/cgi-bin/bizlogin",
                              data={"action": "prelogin", "token": "", "lang": "zh_CN", "f": "json", "ajax": "1"})
        headers = {
            "Host": "mp.weixin.qq.com",
            "Referer": "https://mp.weixin.qq.com/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"}
        payload = 'userlang=zh_CN&redirect_url=&login_type=3&sessionid=168334465835796&token=&lang=zh_CN&f=json&ajax=1'
        res = self.session.post("https://mp.weixin.qq.com/cgi-bin/bizlogin?action=startlogin", data=payload,
                                headers=headers)
        # 获取验证码
        random_ = "https://mp.weixin.qq.com/cgi-bin/scanloginqrcode?action=getqrcode&random=" + \
                  str(datetime.now().timestamp()).split(".")[0]
        res = self.session.get(random_)
        return res.content

    def listen_task(self):
        for i in range(60):
            res = self.session.get(
                "https://mp.weixin.qq.com/cgi-bin/scanloginqrcode?action=ask&token=&lang=zh_CN&f=json&ajax=1/").json()
            print(res['status'],file=sys.stdout)
            if res['status'] == 1:
                print("扫码成功",file=sys.stdout)
                break
            time.sleep(1)

        headers = {
            "Host": "mp.weixin.qq.com",
            "Referer": "https://mp.weixin.qq.com/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"}
        payload = 'userlang=zh_CN&redirect_url=&cookie_forbidden=0&cookie_cleaned=0&plugin_used=0&login_type=3&token=&lang=zh_CN&f=json&ajax=1'
        res = self.session.post("https://mp.weixin.qq.com/cgi-bin/bizlogin?action=login", data=payload, headers=headers)
        self.token = re.findall("token=(\d*)", res.text)[0]
        print(self.token,file=sys.stdout)

        # 保持会话
        self.to_home()

    def to_home(self):
        while True:
            print('访问主页',file=sys.stdout)
            url = f"https://mp.weixin.qq.com/cgi-bin/home?action=get_finder_live_info&token={self.token}&lang=zh_CN&f=json&ajax=1"
            self.session.get(url=url)
            print(self.session.cookies,file=sys.stdout)
            time.sleep(60 * 60 * 6)

    def start_listen(self):
        t = threading.Thread(target=self.listen_task)
        t.start()

    def login(self):
        """登陆"""
        headers = {
            "Host": "mp.weixin.qq.com",
            "Referer": "https://mp.weixin.qq.com/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36"
        }
        url_login = "https://mp.weixin.qq.com/cgi-bin/login"
        r_login = self.session.post(url_login)
        print(r_login.text,file=sys.stdout)
        try:
            self.token = re.findall("token=(\d*)", r_login.content)[0]
            print("token ", self.token,file=sys.stdout)
            if self.token != '':
                print("login success and get token!",file=sys.stdout)
                # 登陆之后转入首页，可去掉
                url_index = "https://mp.weixin.qq.com/cgi-bin/home?t=home/index&lang=zh_CN&token=%s" % self.token
                r_index = self.session.get(url_index)
                if r_index.status_code == 200:
                    print("get the index",file=sys.stdout)
                else:
                    print("get index failed",file=sys.stdout)
            else:
                print("login failed",file=sys.stdout)
        except:
            print("get token error",file=sys.stdout)

    def get_fakeid(self):
        """得到自己的fakeid"""
        url_fakeid = "https://mp.weixin.qq.com/cgi-bin/settingpage?t=setting/index&action=index&token=%s&lang=zh_CN" % self.token
        r_fakeid = self.session.get(url_fakeid)
        try:
            self.fakeid = re.findall("fakeid=(\d{10})", r_fakeid.text)[0]
            print("get fakeid ", self.fakeid,file=sys.stdout)
        except:
            print("get fakeid error",file=sys.stdout)

    def get_users(self):
        """微信更改网址，推荐用users_capable
           得到用户昵称和对应fakeid，写入users字典"""
        url_user = "https://mp.weixin.qq.com/cgi-bin/contactmanage?t=user/index&pageidx=0&type=0&token=%s&lang=zh_CN" % self.token
        r_user = self.session.get(url_user)
        print(r_user.text,file=sys.stdout)
        total_users = int(re.findall("totalCount : '(\d*)'", r_user.text)[0])
        page_count = int(re.findall("pageCount : (\d*)", r_user.text)[0])
        page_size = int(re.findall("pageSize : (\d*),", r_user.text)[0])
        user_ids = []
        user_names = []
        for pageidx in xrange(page_count):
            url_userpage = "https://mp.weixin.qq.com/cgi-bin/contactmanage?t=user/index&pageidx=%s&type=0&token=%s&lang=zh_CN" % (
                str(pageidx), self.token)
            r_userid = self.session.get(url_userpage)
            thepage_user = re.findall("\"id\":\"(.*?){28}\"", r_userid.text)
            thepage_username = re.findall(
                "\"nick_name\":\"(.*?)\"", r_userid.text)
            user_ids += thepage_user
            user_names += thepage_username
        self.users = dict(zip(user_names, user_ids))
        print("get users done",file=sys.stdout)

    def get_users_capable(self):
        url_msgusers = "https://mp.weixin.qq.com/cgi-bin/message?t=message/list&action=&keyword=&offset=0&count=%d&day=7&filterivrmsg=&token=%s&lang=zh_CN"
        r_msgusers = self.session.get(url_msgusers % (20, self.token))
        print(r_msgusers.text,file=sys.stdout)
        total_msg = int(re.findall(r'total_count : (\d*)', r_msgusers.text)[0])
        r_allmsgusers = self.session.get(url_msgusers % (total_msg, self.token))
        fakeid = re.findall(r"\"fakeid\":\"(.*?){28}\"", r_allmsgusers.text)
        nick_name = re.findall(r"\"nick_name\":\"(.*?)\"", r_allmsgusers.text)
        date_time = map(int, re.findall(r"\"date_time\":(\d*)", r_allmsgusers.text))
        now = time.time()
        less_than_48h = [i for i in date_time if now - i < 172800]
        msg_capable = len(less_than_48h)
        fakeid_capable = list(set(fakeid[:msg_capable]))
        nick_name_capable = list(set(nick_name[:msg_capable]))
        self.msg2user_capable = dict(zip(nick_name_capable, fakeid_capable))
        print("get users_capable done",file=sys.stdout)

    def get_user_info_by_open_id(self, openId):
        url = "https://mp.weixin.qq.com/cgi-bin/user_tag?action=get_fans_info"
        payload = f'token={self.token}&lang=zh_CN&f=json&ajax=1&random=0.8208940766104249&user_openid={openId}'

        headers = {
            "Host": "mp.weixin.qq.com",
            "Referer": "https://mp.weixin.qq.com/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
        }
        print(self.session.cookies,file=sys.stdout)
        res = self.session.post(url, data=payload, headers=headers)
        print(res.text,file=sys.stdout)
        return res.json()

    def msg2user(self, msg, touserid):
        """发送消息给单个指定用户"""
        url_msg = "https://mp.weixin.qq.com/cgi-bin/singlesend?t=ajax-response&f=json&token=%s&lang=zh_CN" % self.token
        msg_headers = {
            "Host": "mp.weixin.qq.com",
            "Origin": "https://mp.weixin.qq.com",
            "Referer": "https://mp.weixin.qq.com/cgi-bin/singlesendpage?t=message/send&action=index&tofakeid=%s&token=%s&lang=zh_CN" % (
                touserid, self.token),
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36"
        }
        msg_data = {
            "token": self.token,
            "lang": "zh_CN",
            "f": "json",
            "ajax": "1",
            "random": "0.4469808244612068",
            "type": "1",
            "content": msg,
            "tofakeid": touserid,
            "imgcode": ''
        }
        r_msg = self.session.post(url_msg, data=msg_data, headers=msg_headers)
        if r_msg.status_code == 200:
            err_msg = re.findall("\"err_msg\":\"(.*?)\"", r_msg.content)[0]
            # 发送成功
            if err_msg == 'ok':
                print("send msg %s to %s done" % (msg, touserid),file=sys.stdout)
            # 微信限制，用户48小时内没有主动发送消息，则公众号无法发送消息给该用户
            elif err_msg == 'customer block':
                print("denied because the user hasn't send msg to you in the past 48 hours",file=sys.stdout)
            else:
                print("failed,", err_msg,file=sys.stdout)
        else:
            print("send msg to %s failed,and the err_msg %s" % (touserid, r_msg.status_code),file=sys.stdout)

    def msg2users(self, msg):
        for user in self.msg2user_capable:
            self.msg2user(msg, self.msg2user_capable[user])

    def send2user(self, msg, touser):
        """msg : str
           touser : 用户的昵称"""
        self.login()
        self.get_fakeid()
        self.get_users_capable()
        if touser in self.msg2user_capable:
            print("user %s exists" % touser,file=sys.stdout)
            self.msg2user(msg, self.msg2user_capable[touser])
        else:
            print("user %s not exists" % touser,file=sys.stdout)

    def send2users(self, msg):
        self.login()
        self.get_fakeid()
        self.get_users_capable()
        self.msg2users(msg)

# https://mp.weixin.qq.com/misc/getheadimg?fakeid=oTIo_5gj0dOfVbKIMkBvlaOdxdWk&token=1648872805&lang=zh_CN
