#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
# *******************************************
# -*- Author      :  ayunwSky
# -*- FileName    :  send_email.py
# *******************************************

import sys
import smtplib
import datetime
from jinja2 import Template
from email.header import Header
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from utils import settings
from utils.customLogging import customLogger


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
    mail_port = settings.email_settings["APP_MAIL_PORT"]
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
    message = MIMEText(email_content, 'html', 'utf-8')
    message['From'] = Header(sender)
    message['To'] = Header(';'.join(to_receivers))
    message['Cc'] = Header(';'.join(cc_receivers))
    message['Subject'] = Header(email_subject, 'utf-8')

    try:
        smtpObj = smtplib.SMTP(mail_host, int(mail_port))
        smtpObj.starttls()
        smtpObj.login(sender, mail_pass)
        smtpObj.sendmail(sender, receivers, message.as_string())
        smtpObj.quit()
        return "200", "success"
    except smtplib.SMTPException as e:
        return "500", e
