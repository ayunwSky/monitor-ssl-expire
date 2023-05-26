#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
# *******************************************
# -*- Author      :  ayunwSky
# -*- FileName    :  sendAlertChannel.py
# *******************************************

import sys
from utils import alertChannelType, send_email, settings
from utils.customLogging import customLogger


class SendAlertMsgChannel(object):
    """ 用于发送告警的通道 """
    alert_channel_type = "(email、dingtalk、feishu)"

    def __init__(self, email_subject, domains_info_list=""):
        self.email_subject = email_subject
        self.domains_info_list = domains_info_list

    def alert_send_to_email(self):
        """ 发送告警到email通道 """
        receiver_email = settings.email_settings['APP_MAIL_RECEIVERS']
        if receiver_email != "" and "," in receiver_email:
            receivers_list = receiver_email.split(",")
            all_receiver_email_list = [receivers for receivers in receivers_list]
            customLogger.info(f"all_receiver_email_list: {all_receiver_email_list}")
        else:
            all_receiver_email_list = [receiver_email]

        sendEmail = send_email.sendEmail(self.email_subject, self.domains_info_list, email_format='html')
        if sendEmail[0] == "200":
            return "200", "success"
        elif sendEmail[0] == "500":
            resp_msg = sendEmail[1]
        return "500", resp_msg

    def alert_send_to_dingtalk(self, domain_name, ssl_remaining_days):
        """ 发送告警到钉钉通道 """
        dingtalk_token = settings.dingtalk_settings["APP_DINGTALK_TOKEN"]
        dingtalk_phone_member = settings.dingtalk_settings["APP_DINGTALK_PHONE_MEMBER"]
        if dingtalk_phone_member != "" and "," in dingtalk_phone_member:
            phone_member_list = dingtalk_phone_member.split(",")
            all_dingtalk_phone_member_list = [phone_member for phone_member in phone_member_list]
        else:
            all_dingtalk_phone_member_list = [dingtalk_phone_member]

        dtalk = alertChannelType.DinTalk(dingtalk_token)
        resp = dtalk.sendmessage(
            all_dingtalk_phone_member_list,
            f"Domain [{domain_name}] SSL cert will expire in [{ssl_remaining_days}] days, check and replace the certificate in time!"
        )

        if resp["errcode"] == 0:
            return "200", "success"
        else:
            resp_errcode = resp["errcode"]
            resp_errmsg = resp["errmsg"]
            resp_msg = {"resp_errcode": resp_errcode, "resp_errmsg": resp_errmsg}
            return "500", resp_msg

    def alert_send_to_feishu(self, domain_name, active_time, expire_time, ssl_remaining_days):
        """ 发送告警到飞书通道 """
        fs_token = settings.feishu_settings["APP_FS_TOKEN"]
        fs_secret = settings.feishu_settings["APP_FS_SECRET"]
        fs_alert_type = settings.feishu_settings["APP_FS_ALERT_TYPE"]
        if fs_token is None or fs_secret is None or fs_alert_type is None:
            customLogger.error(
                f"Please set APP environment variable and try again, Require: (APP_FS_TOKEN、APP_FS_SECRET、APP_FS_ALERT_TYPE)")
            sys.exit(1)

        feishu = alertChannelType.FeiShu(access_token=fs_token, secret=fs_secret)
        resp = feishu.sendmessage(domain_name, active_time, expire_time, ssl_remaining_days)
        if resp["StatusCode"] == 0 and resp["StatusMessage"] == "success":
            return "200", "success"
        else:
            resp_status_code = resp["StatusCode"]
            resp_status_message = resp["StatusMessage"]
            resp_msg = {"resp_status_code": resp_status_code, "resp_status_message": resp_status_message}
            return "500", resp_msg
