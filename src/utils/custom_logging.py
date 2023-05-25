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

# 以下表示当前目录的上上级目录
BASE_DIR = Path(__file__).resolve().parent.parent.parent
LOG_PATH = BASE_DIR / 'logs'
ACCESS_LOGFILE = LOG_PATH / 'access.log'
DEFAULT_LOGFILE = LOG_PATH / 'default.log'

if not os.path.exists(LOG_PATH):
    os.mkdir(LOG_PATH)

test_format = '[%(asctime)s] - [%(levelname)s]: %(message)s'
simple_format = '[%(asctime)s] - [%(levelname)s] - [%(filename)s:%(lineno)d]: %(message)s'
standard_format = '[%(asctime)s] - [%(levelname)s] - [%(threadName)s:%(thread)d] - [task_id:%(name)s] ' \
                  '- [%(filename)s:%(lineno)d]: %(message)s'

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
    'handlers': {
        'default': {
            'level': os.getenv('APP_LOG_LEVEL', 'DEBUG'),
            'class': 'logging.FileHandler',
            'formatter': 'standard',
            'filename': DEFAULT_LOGFILE,
            'encoding': 'utf-8',
        },
        'console': {
            'level': os.getenv('APP_LOG_LEVEL', 'DEBUG'),
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'access': {
            'level': os.getenv('APP_LOG_LEVEL', 'INFO'),
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'standard',
            'filename': ACCESS_LOGFILE,
            'maxBytes': 1024 * 1024 * 200,
            'backupCount': 10,
            'encoding': 'utf-8',
        },
    },
    'loggers': {
        '': {
            'handlers': ['default', 'console'],
            'level': os.getenv('APP_LOG_LEVEL', 'DEBUG'),
            'propagate': False,
        },
        'access_log': {
            'handlers': [
                'access',
            ],
            'level': os.getenv('APP_LOG_LEVEL', 'INFO'),
            'propagate': False,
        },
        'console_log': {
            'handlers': [
                'console',
            ],
            'level': os.getenv('APP_LOG_LEVEL', 'DEBUG'),
            'propagate': False,
        },
        'access_console_log': {
            'handlers': ['access', 'console'],
            'level': os.getenv('APP_LOG_LEVEL', 'INFO'),
            'propagate': False,
        },
    },
}

config.dictConfig(LOGGING_DIC)
customLogger = getLogger("console_log")

if __name__ == '__main__':
    customLogger.info("I am test log...")
