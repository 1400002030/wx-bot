import logging

# 创建Logger对象
logger = logging.getLogger()

# 配置Logger对象的输出格式和级别
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger.setLevel(logging.DEBUG)

# 创建一个输出到控制台的Handler对象
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)

# 创建一个输出到文件的Handler对象
file_handler = logging.FileHandler('bot-debug.log')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

info_handler = logging.FileHandler('bot-info.log')
info_handler.setLevel(logging.INFO)
info_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(info_handler)
logger.addHandler(console_handler)


def get_logger():
    return logger
