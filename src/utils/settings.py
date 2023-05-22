#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
# *******************************************
# -*- CreateTime  :  2023/03/14 09:06:21
# -*- Author      :  ayunwSky
# -*- FileName    :  settings.py
# *******************************************

import os

# 所有的环境变量配置
env_settings = {
    'APP_PORT': os.getenv("APP_PORT", "8080"),
    'APP_HOST': os.getenv("APP_HOST", "0.0.0.0"),
    'APP_ENV': 'dev' if not os.getenv("APP_ENV") else os.getenv("APP_ENV"),
    'APP_MAIL_PORT': os.getenv("APP_MAIL_PORT", "邮件服务器端口"),
    'APP_MAIL_USER': os.getenv("APP_MAIL_USER", "发件人邮箱的用户名"),
    'APP_MAIL_PASS': os.getenv("APP_MAIL_PASS", "发件人邮箱的密码"),
    'APP_MAIL_HOST': os.getenv("APP_MAIL_HOST", "SMTP邮件服务器"),
    'APP_MAIL_SENDER': os.getenv("APP_MAIL_SENDER", "发件人邮箱"),
    'APP_OPEN_EMAIL': os.getenv("APP_OPEN_EMAIL", "0"),
    'APP_OPEN_DINGTALK': os.getenv("APP_OPEN_DINGTALK", "0"),
    'APP_DINGTALK_TOKEN': os.getenv("APP_DINGTALK_TOKEN", "your-dingtalk-access-token"),
    'APP_DINGTALK_SECRET': os.getenv("APP_DINGTALK_SECRET", "your-dingtalk-secret"),
    'APP_DINGTALK_PHONE_MEMBER': os.getenv("APP_DINGTALK_PHONE_MEMBER", "135xxxxxxxx"),
    'APP_LOG_LEVEL': os.getenv("APP_LOG_LEVEL", "INFO"),
    'SSL_EXPIRE_DAYS': os.getenv("SSL_EXPIRE_DAYS", "30")
}

# 项目相关的全局配置
global_settings = {
    'APP_PORT': os.getenv("APP_PORT", "8080"),
    'APP_HOST': os.getenv("APP_HOST", "0.0.0.0"),
    'APP_ENV': 'dev' if not os.getenv("APP_ENV") else os.getenv("APP_ENV"),
    'APP_LOG_LEVEL': os.getenv("APP_LOG_LEVEL", "INFO"),
    'SSL_EXPIRE_DAYS': os.getenv("SSL_EXPIRE_DAYS", "30")
}

# 邮箱的配置
email_settings = {
    'APP_OPEN_EMAIL': os.getenv("APP_OPEN_EMAIL", "0"),
    'APP_MAIL_PORT': os.getenv("APP_MAIL_PORT", "邮件服务器端口"),
    'APP_MAIL_USER': os.getenv("APP_MAIL_USER", "发件人邮箱的用户名"),
    'APP_MAIL_PASS': os.getenv("APP_MAIL_PASS", "发件人邮箱的密码"),
    'APP_MAIL_HOST': os.getenv("APP_MAIL_HOST", "SMTP邮件服务器"),
    'APP_MAIL_SENDER': os.getenv("APP_MAIL_SENDER", "发件人邮箱")
}

# 钉钉的配置
dingtalk_settings = {
    'APP_OPEN_DINGTALK': os.getenv("APP_OPEN_DINGTALK", "0"),
    'APP_DINGTALK_TOKEN': os.getenv("APP_DINGTALK_TOKEN", "your-dingtalk-access-token"),
    'APP_DINGTALK_SECRET': os.getenv("APP_DINGTALK_SECRET", "your-dingtalk-secret"),
    'APP_DINGTALK_PHONE_MEMBER': os.getenv("APP_DINGTALK_PHONE_MEMBER", "135xxxxxxxx")
}
