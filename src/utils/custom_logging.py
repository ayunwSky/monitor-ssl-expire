#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
# *******************************************
# -*- CreateTime  :  2023/03/13 12:44:01
# -*- Author      :  ayunwSky
# -*- FileName    :  custom_logging.py
# *******************************************

import os
from pathlib import Path
from logging import config, getLogger

# 以下表示当前目录的上一级目录
BASE_DIR = Path(__file__).resolve().parent.parent
LOG_PATH = BASE_DIR / 'logs'
if not os.path.exists(LOG_PATH):
    os.mkdir(LOG_PATH)

# log文件的绝对路径
ACCESS_LOGFILE = LOG_PATH / 'access.log'
DEFAULT_LOGFILE = LOG_PATH / 'default.log'

# 定义日志格式
standard_format = '[%(asctime)s] - [%(levelname)s] - [%(threadName)s:%(thread)d] - [task_id:%(name)s] ' \
                  '- [%(filename)s:%(lineno)d]: %(message)s'

simple_format = '[%(asctime)s] - [%(levelname)s] - [%(filename)s:%(lineno)d]: %(message)s'

test_format = '[%(asctime)s] - [%(levelname)s]: %(message)s'

# 日志配置字典
LOGGING_DIC = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': standard_format
        },
        'simple': {
            'format': simple_format
        },
        'test': {
            'format': test_format
        },
    },
    'filters': {},
    # handlers: 日志接收者,不同的handlers会将日志输出到不同的位置
    'handlers': {
        # 默认输出到文件
        'default': {
            'level': os.getenv('APP_LOG_LEVEL', 'DEBUG'),
            'class': 'logging.FileHandler',  # 输出到文件
            'formatter': 'standard',
            'filename': DEFAULT_LOGFILE,
            'encoding': 'utf-8',
        },
        # 输出到终端(标准输出)
        'console': {
            'level': os.getenv('APP_LOG_LEVEL', 'DEBUG'),
            'class': 'logging.StreamHandler',  # 输出到屏幕，即终端
            'formatter': 'simple'
        },
        # 根据日志文件大小来自动切割日志
        'access': {
            'level': os.getenv('APP_LOG_LEVEL', 'INFO'),
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'standard',
            'filename': ACCESS_LOGFILE,
            'maxBytes': 1024 * 1024 * 200,  # 200MB
            'backupCount': 10,
            'encoding': 'utf-8',
        },
    },
    # loggers: 日志的生产者,负责产生不同级别的日志。产生的日志会传递给handlers,然后控制输出日志的位置
    'loggers': {
        # 默认的 loggers
        '': {
            'handlers': ['default', 'console'],  # 这个 logger 产生的日志会丢给 default 和 console 这两个接收者
            'level': os.getenv('APP_LOG_LEVEL', 'DEBUG'),
            'propagate': False,  # 和日志继承相关，一般改成 False 即可。
        },
        'console_log': {
            'handlers': ['console'],  # 这个 logger 产生的日志会丢给 console 这个接收者
            'level': os.getenv('APP_LOG_LEVEL', 'DEBUG'),
            'propagate': False,
        },
        'access_log': {
            'handlers': ['access'],  # 这个 logger 产生的日志会丢给 access 这个接收者
            'level': os.getenv('APP_LOG_LEVEL', 'INFO'),
            'propagate': False,
        },
        'access_console_log': {
            'handlers': ['access', 'console'],  # 这个 logger 产生的日志会丢给 access 和 console 这两个接收者
            'level': os.getenv('APP_LOG_LEVEL', 'INFO'),
            'propagate': False,
        },
    },
}

config.dictConfig(LOGGING_DIC)
logger = getLogger("access_console_log")

if __name__ == '__main__':
    logger.info("I am test log...")
