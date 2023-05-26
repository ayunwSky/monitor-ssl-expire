#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import os

# 项目相关的全局配置
global_settings = {
    'APP_ENV': os.getenv("APP_ENV", "prod"),
    'APP_PORT': os.getenv("APP_PORT", "8080"),
    'APP_HOST': os.getenv("APP_HOST", "0.0.0.0"),
    'APP_LOG_LEVEL': os.getenv("APP_LOG_LEVEL", "INFO"),
    'SSL_EXPIRE_DAYS': os.getenv("SSL_EXPIRE_DAYS", "90")
}

# 邮箱的配置
email_settings = {
    'APP_MAIL_OPEN': os.getenv("APP_MAIL_OPEN", "1"),
    'APP_MAIL_PORT': os.getenv("APP_MAIL_PORT", "邮件服务器端口"),
    'APP_MAIL_USER': os.getenv("APP_MAIL_USER", "发件人邮箱的用户名"),
    'APP_MAIL_PASS': os.getenv("APP_MAIL_PASS", "发件人邮箱的密码"),
    'APP_MAIL_HOST': os.getenv("APP_MAIL_HOST", "SMTP邮件服务器"),
    'APP_MAIL_SENDER': os.getenv("APP_MAIL_SENDER", "发件人邮箱"),
    'APP_MAIL_RECEIVERS': os.getenv("APP_MAIL_RECEIVERS", "收件人的邮箱,可以写多个,以逗号分隔")
}

# 钉钉的配置
dingtalk_settings = {
    'APP_DINGTALK_OPEN': os.getenv("APP_DINGTALK_OPEN", "0"),
    'APP_DINGTALK_TOKEN': os.getenv("APP_DINGTALK_TOKEN", "钉钉机器人的 webhook 地址中,access_token= 后面的这部分信息"),
    'APP_DINGTALK_SECRET': os.getenv("APP_DINGTALK_SECRET", "钉钉机器人的安全设置中的加签秘钥"),
    'APP_DINGTALK_PHONE_MEMBER': os.getenv("APP_DINGTALK_PHONE_MEMBER", "钉钉群组接受被艾特的成员手机号")
}

# 飞书的配置
feishu_settings = {
    'APP_FS_OPEN': os.getenv("APP_FS_OPEN", "0"),
    'APP_FS_TOKEN': os.getenv("APP_FS_TOKEN", ""),
    'APP_FS_SECRET': os.getenv("APP_FS_SECRET", ""),
    'APP_FS_ALERT_TYPE': os.getenv("APP_FS_ALERT_TYPE", "interactive")
}
