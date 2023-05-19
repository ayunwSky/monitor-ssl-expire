#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
# *******************************************
# -*- CreateTime  :  2023/05/18 10:49:43
# -*- Author      :  Allen_Jol
# -*- FileName    :  alert.py
# *******************************************

import os
import sys
import json
import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr

# 把项目根目录加入到 sys.path 中
root_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
if root_path not in sys.path:
    sys.path.insert(0, root_path)

from src.utils import genSign


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
        timestamp = genSign.gen_sign()[0]
        sign = genSign.gen_sign()[1]
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
            self.req_message["errmsg"] = f"请求钉钉失败,请检查你的网络是否正常,错误信息: {e}"
            return self.req_message


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
            # 请求失败
            return self.req_message

    def sendmessage(self, touser, message):
        """
        :param touser: 发送给的用户,会@对应的人 支持多用户UserID1|UserID2|UserID3
        :param message:  发送的消息
        :return:  json
        """
        data = {"touser": touser, "msgtype": "text", "agentid": self.agentid, "text": {"content": message}, "safe": 0}
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
            # 括号里的对应发件人邮箱昵称、发件人邮箱账号
            msg['From'] = formataddr([str(self.from_sender), self.from_sender])
            # 括号里的对应收件人邮箱昵称、收件人邮箱账号
            msg['To'] = formataddr([str(to_mail), to_mail])
            # 邮件的主题,也可以说是标题
            msg['Subject'] = title

            if not self.smtp_ssl:
                server = smtplib.SMTP(self.smtp, self.smtp_port)
            else:
                # 发件人邮箱中的SMTP服务器
                server = smtplib.SMTP_SSL(self.smtp, self.smtp_port)
            # 括号中对应的是发件人邮箱账号、邮箱密码
            server.login(self.from_sender, self.from_pass)
            # 括号中对应的是发件人邮箱账号、收件人邮箱账号、发送邮件
            server.sendmail(self.from_sender, [
                to_mail,
            ], msg.as_string())
            server.quit()
        except Exception as e:
            self.req_message["errcode"] = 0
            self.req_message["errmsg"] = f"发送失败{e}"
        return self.req_message
