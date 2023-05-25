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

from utils import send_email, alert, settings
from utils.custom_logging import customLogger


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
    if settings.email_settings["APP_OPEN_EMAIL"] != "1" and \
        settings.dingtalk_settings["APP_OPEN_DINGTALK"] != "1" and \
        settings.feishu_settings["APP_OPEN_FS"] != "1":
        customLogger.warning(
            f"Not open any alert channel, need to set at least one of environment variable: (APP_OPEN_EMAIL、APP_OPEN_DINGTALK、APP_OPEN_FS)!")

    if settings.email_settings["APP_OPEN_EMAIL"] == "1":
        receiver_email = settings.email_settings['APP_MAIL_RECEIVERS']
        if receiver_email != "" and "," in receiver_email:
            receivers_list = receiver_email.split(",")
            all_receiver_email_list = [receivers for receivers in receivers_list]
            customLogger.info(f"all_receiver_email_list: {all_receiver_email_list}")
        else:
            all_receiver_email_list = [receiver_email]

        sendEmail = send_email.sendEmail(email_subject, domains_info_list, email_format='html')
        if sendEmail[0] == "200":
            customLogger.info(f"Send alert message of domain SSL expire info to Email successfully, email list: {all_receiver_email_list},please check!")
        elif sendEmail[0] == "500":
            errMsg = sendEmail[1]
            customLogger.error(f"Failed to send email, error message: {errMsg}")

    if settings.dingtalk_settings["APP_OPEN_DINGTALK"] == "1":
        dingtalk_token = settings.dingtalk_settings["APP_DINGTALK_TOKEN"]
        dingtalk_phone_member = settings.dingtalk_settings["APP_DINGTALK_PHONE_MEMBER"]
        if dingtalk_phone_member != "" and "," in dingtalk_phone_member:
            phone_member_list = dingtalk_phone_member.split(",")
            all_dingtalk_phone_member_list = [phone_member for phone_member in phone_member_list]
        else:
            all_dingtalk_phone_member_list = [dingtalk_phone_member]

        dtalk = alert.DinTalk(dingtalk_token)
        for domain in domains_info_list:
            domain_name = domain["name"]
            domain_ssl_remaining_days = domain["ssl_remaining_days"]
            resp = dtalk.sendmessage(all_dingtalk_phone_member_list,
                                     f"Domain [{domain_name}] SSL cert will expire in [{domain_ssl_remaining_days}] days, check and replace the certificate in time!")
            if resp["errcode"] == 0:
                customLogger.info(
                    f"Send alert message of domain [{domain_name}] SSL expire info to DingTalk successfully! At user: {all_dingtalk_phone_member_list}!"
                )
            else:
                resp_code = resp["errcode"]
                resp_msg = resp["errmsg"]
                customLogger.error(
                    f"Failed to send alert message of domain [{domain_name}] SSL expire info to DingTalk. Error code: {resp_code}. Error message: {resp_msg}"
                )

    if settings.feishu_settings["APP_OPEN_FS"] == "1":
        fs_token = settings.feishu_settings["APP_FS_TOKEN"]
        fs_secret = settings.feishu_settings["APP_FS_SECRET"]
        fs_alert_type = settings.feishu_settings["APP_FS_ALERT_TYPE"]

        if fs_token is None or fs_secret is None or fs_alert_type is None:
            customLogger.error(
                f"Please set system environment variable and try again, Require: (APP_FS_TOKEN、APP_FS_SECRET、APP_FS_ALERT_TYPE)"
            )
            sys.exit(1)

        feishu = alert.FeiShu(access_token=fs_token, secret=fs_secret)
        for domain in domains_info_list:
            name = domain['name']
            active_time = domain['active_time']
            expire_time = domain['expire_time']
            ssl_remaining_days = domain['ssl_remaining_days']
            resp = feishu.sendmessage(name, active_time, expire_time, ssl_remaining_days)
            if resp["StatusCode"] == 0 and resp["StatusMessage"] == "success":
                customLogger.info(f"Send alert message of domain [{name}] ssl expire to feishu successfully! Msg: {resp}")
            else:
                resp_code = resp["StatusCode"]
                resp_msg = resp["StatusMessage"]
                customLogger.error(
                    f"Failed to send alert message of domain [{name}] ssl expire to feishu. Error code: {resp_code}. Error message: {resp_msg}"
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
        customLogger.error(f"Error: {e}")


def main():
    """ 主体函数 """
    email_subject = "SSL证书到期提醒 " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    check_send_alert(email_subject, email_format="html")
