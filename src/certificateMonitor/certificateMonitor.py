#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
# *******************************************
# -*- CreateTime  :  2023/03/13 15:51:17
# -*- Author      :  ayunwSky
# -*- FileName    :  certificateMonitor.py
# *******************************************

import os
import sys
import ssl
import yaml
import socket
import datetime

# 把项目根目录加入到 sys.path 中
root_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
if root_path not in sys.path:
    sys.path.insert(0, root_path)

from utils import send_email, alert, settings
from utils.custom_logging import logger


def get_domain():
    with open('src/config/all.yaml', 'r', encoding='utf-8') as f:
        data = yaml.safe_load_all(f)
        for domain in data:
            return domain


# 获取每个域名的证书信息
def get_certificate_info(domain, port):
    context = ssl.create_default_context()
    context.set_ciphers('DEFAULT@SECLEVEL=1')
    with socket.create_connection((domain, port)) as sock:
        with context.wrap_socket(sock, server_hostname=domain) as sslsock:
            cert = sslsock.getpeercert()
            subject = dict(x[0] for x in cert['subject'])
            issued_to = subject.get('commonName')
            issuer = dict(x[0] for x in cert['issuer'])
            issued_by = issuer.get('organizationName')
            valid_from = datetime.datetime.strptime(cert['notBefore'], '%b %d %H:%M:%S %Y %Z')
            valid_to = datetime.datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
            expire_days = (valid_to - datetime.datetime.utcnow()).days
            return (issued_to, valid_from, valid_to, expire_days, issued_by)


def notify(ssl_expire_time, domain_name, email_content):
    # 发送告警到邮件
    if settings.env_settings["APP_OPEN_EMAIL"] == "1":
        sendEmail = send_email.sendEmail(email_content)
        if sendEmail == "200":
            logger.warning(f"域名: [{domain_name}] 的 SSL 证书还有 [{ssl_expire_time}] 天就要过期了,请及时更换证书.告警已经发送至指定邮箱!")

    # 发送告警到钉钉
    if settings.env_settings["APP_OPEN_DINGTALK"] == "1":
        dingtalk_phone_member_list = []
        dingtalk_token = settings.env_settings["APP_DINGTALK_TOKEN"]
        dingtalk_phone_member = settings.env_settings["APP_DINGTALK_PHONE_MEMBER"]
        if dingtalk_phone_member != "":
            phone_member_list = dingtalk_phone_member.split(",")
            for phone_member in phone_member_list:
                dingtalk_phone_member_list.append(phone_member)

        dtalk = alert.DinTalk(dingtalk_token)
        resp = dtalk.sendmessage(dingtalk_phone_member_list,
                                 f"域名 [{domain_name}] 的 SSL 证书还有 [{ssl_expire_time}] 天就要过期了,请注意及时更换证书!")
        if resp["errcode"] == 0:
            logger.info("Send alarm message to DingTalk successfully.")
        else:
            resp_code = resp["errcode"]
            resp_msg = resp["errmsg"]
            logger.error(f"Failed to send alarm message to DingTalk.Error code: {resp_code},error message: {resp_msg}.")


def check_send_alert():
    all_domains = get_domain()
    for domain in all_domains['domains']:
        domain_name = domain.split(':')[0]
        domain_port = domain.split(':')[1]
        if not domain_port.isnumeric():
            logger.warning(f"域名 {domain_name} 的端口填写成了 {domain_port}, 端口填写错误,请重新填写")
            sys.exit(1)
        info = get_certificate_info(domain=domain_name, port=domain_port)
        ssl_expire_time = info[3]
        email_content = f"告警消息:\n\n\t\t\t\t域名: {domain_name}\n\t\t\t\t生效日期: {info[1]}\n\t\t\t\t过期日期: {info[2]}\n\n\n\n距离SSL证书过期还有: {ssl_expire_time} 天,请注意更换证书!\n"
        try:
            if int(ssl_expire_time) <= int(settings.env_settings["SSL_EXPIRE_DAYS"]):
                notify(ssl_expire_time, domain_name, email_content)
        except Exception as e:
            logger.error(f"Error: {e}")


# 主体函数
def main():
    check_send_alert()
