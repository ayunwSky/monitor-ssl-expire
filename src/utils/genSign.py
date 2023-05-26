#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
# *******************************************
# -*- Author      :  ayunwSky
# -*- FileName    :  genSign.py
# *******************************************

import time
import hmac
import base64
import hashlib
import urllib.parse

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
