#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import json
import urllib3
import smtplib
import datetime
import requests
from requests.adapters import HTTPAdapter
from email.utils import formataddr
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from utils import genSign, settings
from utils.customLogging import customLogger

urllib3.disable_warnings()


class WeiXin(object):
    """
      微信消息发送
    """
    headers = {"Content-Type": "application/json"}
    req_message = {"errcode": 1, "errmsg": ""}

    def __init__(self, corpid, corpsecret, agentid):
        """
        :param corpid:  企业id
        :param corpsecret:  自定义应用secret
        :param agentid: 自定义应用ID
        """
        self.corpid = corpid
        self.corpsecret = corpsecret
        self.agentid = agentid

    def __access_token(self):
        """
        :return: access_token
        """
        try:
            req = requests.get("https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={0}&corpsecret={1}".format(
                self.corpid, self.corpsecret))
            if req.json()["errcode"] != 0:
                self.req_message["errcode"] = 0
                self.req_message["errmsg"] = "获取access_token失败:" + str(req.json())
            else:
                self.req_message["errmsg"] = req.json()["access_token"]
            return self.req_message
        except Exception as e:
            self.req_message["errcode"] = 0
            self.req_message["errmsg"] = "获取access_token失败,监测你的网络是否正常"
            return self.req_message

    def sendmessage(self, touser, message):
        """
        :param touser: 发送给的用户,会@对应的人 支持多用户UserID1|UserID2|UserID3
        :param message:  发送的消息
        :return:  json
        """
        data = {
            "touser": touser,
            "msgtype": "text",
            "agentid": self.agentid,
            "text": {
                "content": message
            },
            "safe": 0
        }
        access_token = self.__access_token()
        if access_token["errcode"]:
            try:
                req = requests.post("https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={}".format(
                    access_token["errmsg"]),
                                    data=json.dumps(data),
                                    headers=self.headers,
                                    timeout=10)

                if req.json()["errcode"] == 0:
                    self.req_message["errmsg"] = "发送成功"
                else:
                    self.req_message["errcode"] = 0
                    self.req_message["errmsg"] = str(req.json())
            except:
                self.req_message["errcode"] = 0
                self.req_message["errmsg"] = "发送失败,请求接口错误"
        else:
            return access_token
        return self.req_message


class Email(object):
    """
    邮件消息,默认QQ邮箱不用传递smtp参数
    """
    req_message = {"errcode": 1, "errmsg": ""}

    def __init__(self, from_sender, from_pass, smtp="smtp.qq.com", smtp_port=465, smtp_ssl=True):
        """
        :param from_sender: 发件人
        :param from_pass: 发件人密码
        :param smtp: smtp地址,默认QQ邮箱
        :param smtp_port: smtp端口
        :param smtp_ssl: 是否启用ssl
        """
        self.from_sender = from_sender
        self.from_pass = from_pass
        self.smtp = smtp
        self.smtp_port = smtp_port
        self.smtp_ssl = smtp_ssl

    def sendmessage(self, to_mail, title, message):
        """
        :param to_mail: 收件人
        :param message: 消息类容
        :return:
        """
        ret = True
        try:
            message = MIMEMultipart()
            msg = MIMEText(message, 'plain', 'utf-8')
            msg['From'] = formataddr([str(self.from_sender), self.from_sender])
            msg['To'] = formataddr([str(to_mail), to_mail])
            msg['Subject'] = title

            if not self.smtp_ssl:
                server = smtplib.SMTP(self.smtp, self.smtp_port)
            else:
                server = smtplib.SMTP_SSL(self.smtp, self.smtp_port)
            server.login(self.from_sender, self.from_pass)
            server.sendmail(self.from_sender, [
                to_mail,
            ], msg.as_string())
            server.quit()
        except Exception as e:
            self.req_message["errcode"] = 0
            self.req_message["errmsg"] = f"发送失败{e}"
        return self.req_message


class DinTalk(object):
    """
     钉钉webhook消息发送
    """
    headers = {"Content-Type": "application/json"}
    req_message = {"errcode": 1, "errmsg": ""}

    def __init__(self, access_token):
        """
        :param access_token: access_token,只需要URL后面 access_token= 后面的值
        """
        self.access_token = access_token

    def sendmessage(self, phone_numbers, message):
        """
        :param phone_numbers: 钉钉群组中的成员手机号
        :param message: 发送的消息
        :return: errcode  1 发送失败, 0 发送成功
        """
        timestamp, sign = genSign.gen_sign()
        webhook_url = f"https://oapi.dingtalk.com/robot/send?access_token={self.access_token}&timestamp={timestamp}&sign={sign}"
        data = {"msgtype": "text", "text": {"content": str(message)}, "at": {"atMobiles": phone_numbers, "isAtAll": False}}
        try:
            resp = requests.post(webhook_url, data=json.dumps(data), headers=self.headers, timeout=5)
            if resp.status_code == 200 and resp.json()["errcode"] == 0:
                return resp.json()
            else:
                self.req_message["errcode"] = 1
                self.req_message["errmsg"] = str(resp.json())
                return self.req_message
        except Exception as e:
            self.req_message["errcode"] = 1
            self.req_message["errmsg"] = f"请求钉钉失败,请检查你的网络是否正常.错误信息: {e}"
            return self.req_message


class FeiShu(object):
    """
    飞书 webhook 告警通道
    """
    headers = {'Content-Type': 'application/json; charset=utf-8'}
    req_message = {'StatusCode': 0, 'StatusMessage': 'success', 'code': 0, 'data': {}, 'msg': 'success'}

    def __init__(self, access_token, secret):
        """
        :param access_token: 飞书的机器人v2版本接口的 hook/ 后面的 token 信息
        :param secret: 飞书安全设置中的加签秘钥
        """
        self.access_token = access_token
        self.secret = secret

    def sendmessage(self, name, active_time, expire_time, ssl_remaining_days):
        """
        :param name: 域名
        :param active_time: 域名证书生效时间
        :param expire_time: 域名证书失效时间
        :param ssl_remaining_days: 证书剩余几天到期
        :return: errcode  1 发送失败, 0 发送成功
        """
        timestamp = int(datetime.datetime.now().timestamp())
        sign = genSign.feishu_gen_sign(timestamp)
        webhook_url = f"https://open.feishu.cn/open-apis/bot/v2/hook/{self.access_token}"
        fs_alert_type = settings.feishu_settings["APP_FS_ALERT_TYPE"]
        isCritical = "Critical" if ssl_remaining_days <= 30 else "firing"

        alert_title = "平台告警通知"
        alert_name = "证书到期告警"
        alert_instance = f"\n告警实例: {name}\n"
        alert_ssl_active_time = f"生效时间: {active_time}\n"
        alert_ssl_expire_time = f"到期时间: {expire_time}\n"
        alert_ssl_remaining_days = f"可用天数: {ssl_remaining_days}\n"
        alert_level = f"告警等级: {isCritical}\n"
        alert_message = f"告警信息: 域名 {name} 的 SSL 证书将在 {ssl_remaining_days} 天后过期, 请及时更换证书!\n"

        if fs_alert_type == "post":
            send_data = {
                "timestamp": timestamp,
                "sign": sign,
                "msg_type": "post",
                "content": {
                    "post": {
                        "zh_cn": {
                            "title":
                            alert_title,
                            "content": [[
                                {
                                    "tag": "text",
                                    "text": alert_instance
                                },
                                {
                                    "tag": "text",
                                    "text": alert_ssl_active_time
                                },
                                {
                                    "tag": "text",
                                    "text": alert_ssl_expire_time
                                },
                                {
                                    "tag": "text",
                                    "text": alert_ssl_remaining_days
                                },
                                {
                                    "tag": "text",
                                    "text": alert_level
                                },
                                {
                                    "tag": "text",
                                    "text": alert_message
                                },
                            ]],
                        }
                    }
                },
            }
        elif fs_alert_type == "interactive":
            send_data = {
                "msg_type": "interactive",
                "timestamp": timestamp,
                "sign": sign,
                "card": {
                    "config": {
                        "wide_screen_mode": True
                    },
                    "header": {
                        "template": 'red' if isCritical == 'Critical' or isCritical == 'firing' else 'green',
                        "title": {
                            "content": alert_title if isCritical == 'Critical' or isCritical == 'firing' else '平台告警恢复',
                            "tag": "plain_text"
                        }
                    },
                    "elements": [{
                        "tag": "div",
                        "text": {
                            "tag": "plain_text",
                            "content": alert_name,
                            "lines": 1
                        },
                        "fields": [{
                            "text": {
                                "tag": "lark_md",
                                "content": alert_instance,
                            }
                        }, {
                            "text": {
                                "tag": "lark_md",
                                "content": alert_ssl_active_time,
                            }
                        }, {
                            "text": {
                                "tag": "lark_md",
                                "content": alert_ssl_expire_time,
                            }
                        }, {
                            "text": {
                                "tag": "lark_md",
                                "content": alert_ssl_remaining_days,
                            }
                        }, {
                            "text": {
                                "tag": "lark_md",
                                "content": alert_level,
                            }
                        }, {
                            "text": {
                                "tag": "lark_md",
                                "content": alert_message,
                            }
                        }, {
                            "text": {
                                "tag": "lark_md",
                                "content": "<at id=all></at>" if isCritical == 'Critical' else ""
                            },
                        }]
                    }],
                }
            }

        try:
            session = requests.Session()
            session.mount('http://', HTTPAdapter(max_retries=3))
            session.mount('https://', HTTPAdapter(max_retries=3))
            alertMsg = json.dumps(send_data)

            resp = session.post(webhook_url, data=alertMsg, headers=self.headers, timeout=5, verify=False)
            if resp.status_code == 200 and resp.json()["StatusCode"] == 0:
                return resp.json()
            else:
                self.req_message["StatusCode"] = 1
                self.req_message["StatusMessage"] = "failure"
                self.req_message["code"] = 1
                self.req_message["msg"] = "failure"
                self.req_message["data"] = resp.json()
                customLogger.error(f"请求飞书接口失败后返回的错误信息: {resp.json()}")
                return self.req_message
        except requests.exceptions.RequestException as e:
            self.req_message["StatusCode"] = 1
            self.req_message["StatusMessage"] = "failure"
            self.req_message["code"] = 1
            self.req_message["msg"] = f"请求飞书接口失败,请检查你的网络是否正常.错误信息: {e}"
            self.req_message["data"] = resp.json()
            return self.req_message
