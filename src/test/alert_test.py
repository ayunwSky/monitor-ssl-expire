#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
# *******************************************
# -*- CreateTime  :  2023/05/18 11:12:09
# -*- Author      :  Allen_Jol
# -*- FileName    :  alert_test.py
# *******************************************

import os
import sys

# 把项目根目录加入到 sys.path 中
root_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
if root_path not in sys.path:
    sys.path.insert(0, root_path)

from src.utils import alert
from src.utils.custom_logging import logger


class AlertTest():

    def __init__(self) -> None:
        pass

    def test_dingtalk():
        # webhook地址，只需要 access_token= 后面的值
        dtalk = alert.DinTalk("e3xxx691d")
        # phone_numbers 表示要艾特钉钉群里的用户的手机号,支持以列表的形式填写
        # phone_numbers = ["177xxxxxxxx", "153xxxx1993"]
        phone_numbers = ["177xxxxxxxx"]
        # 发送的用户，以及发送的消息，多用户使用"user1|user2|user3"
        resp = dtalk.sendmessage(phone_numbers, "自定义告警模块实现钉钉告警通知测试")
        if resp["errcode"] == 0:
            logger.info("发送告警成功")
        else:
            resp_code = resp["errcode"]
            resp_msg = resp["errmsg"]
            logger.error(f"Error code: {resp_code}.Error message: {resp_msg}")

    def test_sendemail():
        # 默认ssl是True
        smtp = alert.Email("发件人账号", "发件人密码", smtp="smtp地址", smtp_port="smtp端口 int", smtp_ssl=False)
        resp = smtp.sendmessage("收件人账号", '标题', '内容')
        if resp["errcode"]:
            logger.info("发送成功")
        else:
            logger.error(resp["errmsg"])

    def test_wechat():
        corpid = "企业的ID"
        secret = "自定义应用secret"
        agentid = "自定义应用agentid"
        wechat = alert.WeiXin(corpid, secret, agentid)
        resp = wechat.sendmessage("消息接受者（在企业微信后台查看的账号）", "发送内容")
        if resp["errcode"]:
            logger.info("发送成功")
        else:
            logger.error(resp["errmsg"])


if __name__ == '__main__':
    alertTest = AlertTest()

    alertTest.test_dingtalk()
    # alertTest.test_sendemail()
    # alertTest.test_wechat()
