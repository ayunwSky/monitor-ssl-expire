#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
# *******************************************
# -*- CreateTime  :  2023/05/18 17:04:27
# -*- Author      :  Allen_Jol
# -*- FileName    :  genSign.py
# -*- Desc        :  钉钉机器人加签
# *******************************************

import os
import sys
import time
import hmac
import base64
import hashlib
import datetime
import urllib.parse

#root_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
#if root_path not in sys.path:
#    sys.path.insert(0, root_path)

from utils import settings


def gen_sign():
    timestamp = str(round(time.time() * 1000))
    secret = settings.dingtalk_settings["APP_DINGTALK_SECRET"]
    secret_enc = secret.encode('utf-8')
    string_to_sign = '{}\n{}'.format(timestamp, secret)
    string_to_sign_enc = string_to_sign.encode('utf-8')
    hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
    sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
    return timestamp, sign


def feishu_gen_sign(timestamp):
    secret = settings.feishu_settings["APP_FS_SECRET"]
    string_to_sign = '{}\n{}'.format(timestamp, secret)
    hmac_code = hmac.new(string_to_sign.encode("utf-8"), digestmod=hashlib.sha256).digest()
    sign = base64.b64encode(hmac_code).decode('utf-8')
    return sign
