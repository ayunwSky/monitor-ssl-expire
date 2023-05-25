#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
# *******************************************
# -*- CreateTime  :  2023/03/10 16:01:18
# -*- Author      :  ayunwSky
# -*- FileName    :  send_email.py
# *******************************************

import os
import sys
import smtplib
import datetime
from jinja2 import Template
from email.header import Header
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from utils import settings
from utils.custom_logging import customLogger


def sendEmail(email_subject, email_domains_info, email_format='html'):
    set_ssl_expire_days = settings.global_settings['SSL_EXPIRE_DAYS']
    current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if email_format == 'html':
        with open('src/email_template/email_template.html', 'r', encoding='utf-8') as f:
            template_content = f.read()
            template = Template(template_content)
            rendered_content = template.render(ssl_expire_days=set_ssl_expire_days, current_time=current_time, domains=email_domains_info)
            email_content = rendered_content
    else:
        customLogger.error(f"Set email_format failed, you set email_format is: {email_format}, only support: 'html'. Please rreset it and restart APP...")
        sys.exit(1)

    mail_host = settings.email_settings["APP_MAIL_HOST"]
    mail_pass = settings.email_settings["APP_MAIL_PASS"]
    sender = settings.email_settings["APP_MAIL_SENDER"]
    receiver_email = settings.email_settings['APP_MAIL_RECEIVERS']
    if receiver_email != "" and "," in receiver_email:
        receivers_list = receiver_email.split(",")
        to_receivers = [receivers for receivers in receivers_list]
    else:
        to_receivers = [receiver_email]

    cc_receivers = [""]
    receivers = to_receivers + cc_receivers

    message = MIMEMultipart()
    if email_format == 'plain':
        message = MIMEText(email_content, 'plain', 'utf-8')
    elif email_format == 'html':
        message = MIMEText(email_content, 'html', 'utf-8')
    message['From'] = Header(sender)
    message['To'] = Header(';'.join(to_receivers))
    message['Cc'] = Header(';'.join(cc_receivers))
    message['Subject'] = Header(email_subject, 'utf-8')

    try:
        smtpObj = smtplib.SMTP(mail_host, 587)
        smtpObj.starttls()
        smtpObj.login(sender, mail_pass)
        smtpObj.sendmail(sender, receivers, message.as_string())
        smtpObj.quit()
        return "200", "OK"
    except smtplib.SMTPException as e:
        return "500", e


def sendEmailTest():
    """ 测试发送邮件 """
    test_domains_data = [
    {
        'name': 'www.example1.cn',
        'active_time': '2022-07-25',
        'expire_time': '2023-07-24'
    },
    {
        'name': 'www.example2.cn',
        'active_time': '2022-06-23',
        'expire_time': '2024-06-22'
    },
    {
        'name': 'www.example3.cn',
        'active_time': '2022-08-02',
        'expire_time': '2023-08-04'
    },
    # Add more domain data as needed
    ]

    email_subject = "邮件主题是: 测试域名 SSL 证书到期时间 " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sendEmail(email_subject=email_subject, email_domains_info=test_domains_data, email_format='html')


if __name__ == '__main__':
    sendEmailTest()
