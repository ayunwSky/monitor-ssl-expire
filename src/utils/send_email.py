#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
# *******************************************
# -*- CreateTime  :  2023/03/10 16:01:18
# -*- Author      :  ayunwSky
# -*- FileName    :  send_email.py
# *******************************************

import os
import sys
import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header

# 把项目根目录加入到 sys.path 中
root_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
if root_path not in sys.path:
    sys.path.insert(0, root_path)

from utils.custom_logging import customLogger


def sendEmail(email_content, subject):
    # 设置SMTP邮件服务器
    mail_host = os.getenv("APP_MAIL_HOST", "")
    # 邮件服务器端口
    mail_port = os.getenv("APP_MAIL_PORT", "")
    # 发件人邮箱的用户名
    # mail_user = os.getenv("APP_MAIL_USER", "")
    # 发件人邮箱的密码
    mail_pass = os.getenv("APP_MAIL_PASS", "")
    # 发件人邮箱
    sender = os.getenv("APP_MAIL_SENDER", "")
    # 收件人是谁，可以是多个，在列表中用逗号隔开
    # to_receivers = ["receivers1@gmail.com", "receivers2@gmail.com"]
    to_receivers = ["receivers1@gmail.com"]
    # 抄送给谁
    cc_receivers = [""]
    # 整合收件人
    receivers = to_receivers + cc_receivers
    # 主题
    # subject = "SSL证书到期提醒 " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    message = MIMEMultipart()
    # 邮件内容，格式，编码
    message = MIMEText(email_content, 'plain', 'utf-8')
    # 发邮件的人
    message['From'] = Header(sender)
    # 如果是单个接收邮件的收件箱，则to_receivers可以直接用字符串的形式
    # message['To'] = to_receivers
    # 收件人邮箱放在一个列表里，则需要join一下 to_receivers
    message['To'] = Header(';'.join(to_receivers))
    # 抄送人
    message['Cc'] = Header(';'.join(cc_receivers))
    # 邮件主题
    message['Subject'] = Header(subject, 'utf-8')

    try:
        smtpObj = smtplib.SMTP(mail_host, mail_port)
        smtpObj.starttls()
        smtpObj.login(sender, mail_pass)
        # 发送邮件
        smtpObj.sendmail(sender, receivers, message.as_string())
        # 关闭连接
        smtpObj.quit()
        customLogger.info("Send email successfully!")
        return "200"
    except smtplib.SMTPException as e:
        customLogger.error(f"Unable to send email, {e}")
        return "500"


if __name__ == '__main__':
    sendEmail('邮件内容: 发送域名的 SSL 证书即将过期的邮件测试', '邮件主题: 测试域名的 SSL 证书是否即将过期')
