import asyncio
import json
import os
import threading
import time
import requests

import uiautomator2 as u2

from logger import get_logger


# python -m weditor
# 群聊搜索页面左上角放大镜按钮
BTN_1 = "com.tencent.wework:id/lvo"
# 群聊搜索页面搜索完成后第一个项目
BTN_2 = '//*[@resource-id="com.tencent.wework:id/gvh"]/android.widget.TextView[1]'
# 输入框按钮, 需要找到EditText
INPUT_BTN = "com.tencent.wework:id/h_8"
# 校验标题
VALID_TITLE = "com.tencent.wework:id/luj"
# 发送按钮
SEND_BTN = "com.tencent.wework:id/h9x"

COM_TENCENT_WEWORK = 'com.tencent.wework'
logger = get_logger()

# 通知群机器人地址
GROUP_BOT_WEBHOOK = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=89e6b4a1-d751-4e5e-a4b7-95620638149b"


def send_error(message: str):
    """发送异常信息"""
    data = {
        "msgtype": "markdown",
        "markdown": {
            "content": f"""<font color=\"warning\">‼️服务告警</font>
> <font color=\"comment\">微信机器人运行异常</font>  
> 

{message}"""
        }
    }
    print(data)
    res = requests.post(GROUP_BOT_WEBHOOK, json=data)
    logger.info(f"发送异常消息 {res.text}")


class Phone:
    def __init__(self, addr):
        self.d: u2.Device = None
        self.last = None
        self.id = None
        self.addr = addr
        self.device_info = None
        logger.info(f"[{self.id}] 初始化")
        self.connect_device()
        self.to_home()
        threading.Thread(target=self.check_loop).start()
        logger.info("启动")

    def connect_device(self):
        os.system(f"adb connect {self.addr}")
        self.d: u2.Device = u2.connect(self.addr)
        self.id = self.d.device_info['udid']
        logger.info(f"连接设备[{self.id}]")

    def check_loop(self):
        while True:
            self.heart_check()
            time.sleep(60)

    def send_message(self, user: str, message: str):
        logger.info(f'''================================================
[{self.id}] 发送消息 ---> {user} ||=> SENDING''')
        # 如果不再聊天页面则回到首页重新进入
        # if not self.d(resourceId="com.tencent.wework:id/gdx").exists or self.last != user:
        self.to_home()
        self.d(text="通讯录").click()
        self.d(text="群聊").click()
        self.d(resourceId=BTN_1).click()
        self.d.send_keys(user)
        self.d.xpath(BTN_2).click()
        self.last = user
        self.d(resourceId=INPUT_BTN).click()

        # 校验
        if not self.d(resourceId=VALID_TITLE, textContains=user).exists:
            logger.info("校验失败 ||=> FAIL")
            return
        self.d.send_keys(message)
        self.d(resourceId=SEND_BTN).click()
        logger.info(f'[{self.id}] 发送消息 ---> {user} ||=> SUCCESS')

    def to_home(self):
        # self.d.app_start(COM_TENCENT_WEWORK)
        logger.info(f'[{self.id}] 前往首页')
        if self.d.current_app()['package'] != COM_TENCENT_WEWORK:
            self.d.app_start(COM_TENCENT_WEWORK)
        for i in range(5):
            if self.d(text='消息').exists:
                return
            self.d.press("back")
        self.d.app_stop(COM_TENCENT_WEWORK)
        self.d.app_start(COM_TENCENT_WEWORK)

    def heart_check(self):
        try:
            logger.info(f'[{self.id}] 健康检查 --> {self.d.healthcheck()}')
            self.d.screen_on()
        except:
            send_error("设备连接异常")
            self.connect_device()

    def test(self):
        logger.info(self.d.app_list())
        logger.info(self.d.app_info(COM_TENCENT_WEWORK))
        self.send_message("通知测试群", "测试消息")
        self.d.app_start(COM_TENCENT_WEWORK)


if __name__ == '__main__':
    phone = Phone("192.168.1.30")
    phone.test()
    # send_error("kk")
