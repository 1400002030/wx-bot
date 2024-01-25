# -*- coding:utf-8 -*-
"""
2015-01-16 by Camel
https://github.com/daoluan/WXSender-Python/ is acknowledged

"""
import io
import mimetypes
import sys

import flask
from flask import Flask, request, send_file

from wx import WeiXin
print('This is error output', file=sys.stderr)
print('This is standard output', file=sys.stdout)
app = Flask(__name__)

wx_mp = {}


@app.route('/getLoginQr')
def get_login_qr():
    appId = request.args.get("appId")
    print(appId,file=sys.stdout)
    wx = None
    if appId in wx_mp:
        wx = wx_mp[appId]
    else:
        wx = WeiXin()
        wx_mp[appId] = wx
    img = wx.get_login_qr()
    wx.start_listen()
    ioS = io.BytesIO(img)
    return send_file(ioS, mimetype="image/png")


@app.route('/userInfo')
def get_user_info_by_open_id():
    appId = request.args.get("appId")
    openId = request.args.get("openId")
    print(appId,file=sys.stdout)
    wx = None
    if appId in wx_mp:
        print('获取',file=sys.stdout)
        wx = wx_mp[appId]
    return wx.get_user_info_by_open_id(openId)


def init_wx(appId):
    # 从数据库读取公众号配置和token
    wx_mp[appId] = WeiXin()


if __name__ == '__main__':
    app.run("localhost", "28083")
# wx.send2user('test测试', 'Leuan')  # 'Camel'是我的昵称，请替换成自己的

# session = requests.session()
# session.headers.update({
#     "Host": "mp.weixin.qq.com",
#     "Referer": "https://mp.weixin.qq.com/",
#     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36"
# })
#
# # 获取ua_id
# res = session.get("https://mp.weixin.qq.com/")
#
# # 获取wxuin
# session.get(
#     "https://mp.weixin.qq.com/webpoc/cgi/chat/checkChatPermission?type=15&grayType=random&token=&lang=zh_CN&f=json&ajax=1")
#
# r = session.post("https://mp.weixin.qq.com/cgi-bin/bizlogin",
#                  data={"action": "prelogin", "token": "", "lang": "zh_CN", "f": "json", "ajax": "1"})
# session.headers.setdefault("Content-Type", "application/x-www-form-urlencoded; charset=UTF-8")
# payload = 'userlang=zh_CN&redirect_url=&login_type=3&sessionid=168334465835796&token=&lang=zh_CN&f=json&ajax=1'
# res = session.post("https://mp.weixin.qq.com/cgi-bin/bizlogin?action=startlogin", data=payload)
# # 获取验证码
# random_ = "https://mp.weixin.qq.com/cgi-bin/scanloginqrcode?action=getqrcode&random=" + \
#           str(datetime.now().timestamp()).split(".")[0]
# res = session.get(random_)
# print(res.content,file=sys.stdout)
# with open("./qr.png", "wb") as qr:
#     qr.write(res.content)
# while True:
#     res = session.get(
#         "https://mp.weixin.qq.com/cgi-bin/scanloginqrcode?action=ask&token=&lang=zh_CN&f=json&ajax=1/").json()
#     if res['status'] == 1:
#         print("扫码成功")
#         break
#     time.sleep(1)
#
# payload = 'userlang=zh_CN&redirect_url=&cookie_forbidden=0&cookie_cleaned=0&plugin_used=0&login_type=3&token=&lang=zh_CN&f=json&ajax=1'
# res = session.post("https://mp.weixin.qq.com/cgi-bin/bizlogin?action=login", data=payload)
# print(res.text)
