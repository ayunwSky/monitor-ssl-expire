#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
# *******************************************
# -*- Author      :  ayunwSky
# -*- FileName    :  certificateMonitor.py
# *******************************************

import sys
import ssl
import yaml
import socket
import datetime

from utils import settings
from utils.customLogging import customLogger
from certificateMonitor.sendAlertChannel import SendAlertMsgChannel


def get_domain():
    """ 解析配置文件 """
    with open('src/config/all.yaml', 'r', encoding='utf-8') as f:
        data = yaml.safe_load_all(f)
        for domain in data:
            return domain


def get_certificate_info(domain, port):
    """
    获取每个域名的证书信息
    :param domain: 域名
    :param port: 域名证书所使用的端口号
    """
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


def sendAlertMsg(email_subject, domains_info_list=""):
    """
    发送告警信息的通道.可以任选一个告警方式接收告警,也支持同时开启发送告警到多个告警通道

    :param email_subject: 邮件主题
    :param domains_info_list: 是一个列表类型,里面嵌套了多个域名的SSL证书到期时间小于指定时间的字典信息。
    :return
    """
    isEmailChannel = settings.email_settings["APP_MAIL_OPEN"]
    isFeishuChannel = settings.feishu_settings["APP_FS_OPEN"]
    isDingtalkChannel = settings.dingtalk_settings["APP_DINGTALK_OPEN"]

    customLogger.info(
        f"告警通道开启情况如下(1为开启,0为关闭): isEmailChannel: {isEmailChannel}, isDingtalkChannel: {isDingtalkChannel}, isFeishuChannel: {isFeishuChannel}"
    )

    if isEmailChannel != "1" and \
        isDingtalkChannel != "1" and \
        isFeishuChannel != "1":
        customLogger.warning(
            f"Not open any alert channel, need to set at least one of APP environment variable: (APP_MAIL_OPEN、APP_DINGTALK_OPEN、APP_FS_OPEN)!"
        )
        sys.exit(1)

    sendAlert = SendAlertMsgChannel(email_subject, domains_info_list)

    if isEmailChannel == "1":
        sendEmailResp = sendAlert.alert_send_to_email()
        if sendEmailResp[0] == "200":
            customLogger.info(f"Send alert message of domain ssl expire to email success, status code: {sendEmailResp[0]}!")
        elif sendEmailResp[0] == "500":
            customLogger.info(
                f"Send alert message of domain ssl expire to email failed, status code: {sendEmailResp[0]}, error message: {sendEmailResp[1]}!"
            )

    for domain in domains_info_list:
        domain_name = domain['name']
        active_time = domain['active_time']
        expire_time = domain['expire_time']
        ssl_remaining_days = domain['ssl_remaining_days']

        if isFeishuChannel == "1":
            sendFeishuResp = sendAlert.alert_send_to_feishu(domain_name, active_time, expire_time, ssl_remaining_days)
            if sendFeishuResp[0] == "200":
                customLogger.info(
                    f"Send alert message of domain [{domain_name}] ssl expire to feishu success, status code: {sendFeishuResp[0]}!"
                )
            elif sendFeishuResp[0] == "500":
                customLogger.info(
                    f"Send alert message of domain [{domain_name}] ssl expire to feishu failed, status code: {sendFeishuResp[0]}, error message: {sendFeishuResp[1]}!"
                )

        if isDingtalkChannel == "1":
            sendDingtalkResp = sendAlert.alert_send_to_dingtalk(domain_name, active_time, expire_time, ssl_remaining_days)
            if sendDingtalkResp[0] == "200":
                customLogger.info(
                    f"Send alert message of domain [{domain_name}] ssl expire to dingtalk success, status code: {sendDingtalkResp[0]}!"
                )
            elif sendDingtalkResp[0] == "500":
                customLogger.info(
                    f"Send alert message of domain [{domain_name}] ssl expire to dingtalk failed, status code: {sendDingtalkResp[0]}, error message: {sendDingtalkResp[1]}!"
                )


def check_send_alert(email_subject, email_format='html'):
    """
    判断域名的 SSL 证书小于指定时间(ssl_expire_time)则发送告警通知
    :param email_subject: 邮件主题
    """
    all_domains = get_domain()
    domains_info_list = []
    for domain in all_domains['domainsInfo']:
        if ":" in domain:
            domain_name = domain.split(':')[0]
            domain_port = domain.split(':')[1]
        else:
            domain_name = domain
            domain_port = "443"

        if not domain_port.isnumeric():
            customLogger.warning(f"域名 {domain_name} 的端口填写成了 {domain_port}, 端口填写错误,请重新填写")
            sys.exit(1)

        info = get_certificate_info(domain=domain_name, port=domain_port)
        ssl_expire_time = info[3]

        if int(ssl_expire_time) <= int(settings.global_settings["SSL_EXPIRE_DAYS"]):
            domains_info_dict = {
                "name": domain_name,
                "active_time": info[1],
                "expire_time": info[2],
                "ssl_remaining_days": ssl_expire_time
            }
            domains_info_list.append(domains_info_dict)

    try:
        if email_format == "html":
            sendAlertMsg(email_subject, domains_info_list)
        else:
            customLogger.error(
                f"Set email_format failed, you set email_format is: {email_format}, only support: 'html'. Please rreset it and restart APP..."
            )
            sys.exit(1)
    except Exception as e:
        customLogger.error(f"Error message: {e}")


def main():
    """ 主体函数 """
    email_subject = "SSL证书到期提醒 " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    check_send_alert(email_subject, email_format="html")
