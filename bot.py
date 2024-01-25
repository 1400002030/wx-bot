import json
import time
import pika
import requests

from logger import logger
from phone_bot import Phone, send_error

# hostname = 'leuan.top'
hostname = '95online.cn'
port = 5672

queue = 'py.wx.bot'  # 队列名
routing_key = 'py.wx.bot'
exchange = 'topic.system'
credentials = pika.PlainCredentials(username='yy', password='yy')
parameters = pika.ConnectionParameters(
    host=hostname, port=port, credentials=credentials, connection_attempts=10, retry_delay=10)
connection = pika.BlockingConnection(parameters=parameters)
# 创建通道
channel = connection.channel()
declear_queue_result = channel.queue_declare(queue=queue, durable=True)

we_com = Phone("192.168.1.30")
# we_com = Phone("192.168.1.116")

group_name_map = {
    # 1646774108723200002: "文件传输助手-通知群",
    1646774108723200002: "通知测试群",
    1647080335398707201: "安庆浪漫月-通知群",
    1647109922761510914: "文件传输助手-通知群",
    1650745766919585794: "铜陵格林童趣-通知群",
    1653291277451051009: "西安星豆豆-通知群",
    1653298778720485378: "房山快乐童年-通知群",
    1655813575500414978: "衡水童颜无际-通知群",
    1662857606592028674: "南京妈咪来了-通知群",
    1667076614568583169: "济南安可拾月-通知群",
    1675805322984865793: "常州金色童年-通知群",
	1740639877914980352: "石家庄-通知群"
}

# 堆积数量
wait_count = 0


def callback(ch, method, properties, body):
    global wait_count
    logger.info(" [x] Received %r" % (body.decode(),))

    # 忽略客资通知
    if (wait_count > 0 and '订单' not in body.decode()):
        ch.basic_ack(delivery_tag=method.delivery_tag)  # 发送ack消息
        wait_count -= 1
        logger.info(f"忽略堆积的客资消息 --> {wait_count}")
        return
    elif (wait_count > 0):
        logger.info(f"重发堆积的订单消息 --> {wait_count}")

    data = json.loads(body)
    tenant_id = data['tenantId']
    if tenant_id not in group_name_map:
        ch.basic_ack(delivery_tag=method.delivery_tag)  # 发送ack消息
        wait_count -= 1
        return

    name = group_name_map[tenant_id]
    # 通知内容解析
    content = data['message']
    # 发送消息
    try:
        we_com.send_message(name, content)
    except Exception as e:
        logger.warn('发送失败')
        send_error(f"发送失败 ---> {e}")
        we_com.connect_device()
        we_com.send_message(name, content)
    ch.basic_ack(delivery_tag=method.delivery_tag)  # 发送ack消息


# 添加不按顺序分配消息的参数,可有可无
# channel.basic_qos(prefetch_count=1)
# 告诉rabbitmq使用callback来接收信息


if __name__ == '__main__':
    # no_ack来标记是否需要发送ack，默认是False，开启状态
    channel.basic_consume(queue, callback, False)
    wait_count = declear_queue_result.method.message_count
    logger.info(f"当前积压{wait_count}条数据")
    chose = input("是否忽略客资消息: Y/n\n")
    if chose != 'Y':
        wait_count = 0
        logger.info("不忽略客资消息")
    else:
        logger.info("忽略客资消息")

    while True:
        try:
            channel.start_consuming()
        except Exception as e:
            send_error(f"消息队列断开连接 ---> {e}")
            time.sleep(10)
