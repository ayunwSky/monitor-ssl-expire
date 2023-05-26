#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import datetime
from sanic import Sanic
from sanic.response import json, HTTPResponse
from apscheduler.schedulers.asyncio import AsyncIOScheduler

root_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
if root_path not in sys.path:
    sys.path.insert(0, root_path)

from utils import settings
from utils.customLogging import customLogger
from certificateMonitor import certificateMonitor

app = Sanic(__name__)

app.config.update(settings.global_settings)
app.config.update(settings.email_settings)
app.config.update(settings.dingtalk_settings)


@app.listener('before_server_start')
async def initCornJob(app, loop):
    scheduler = AsyncIOScheduler()
    # 每天早上 10点30分 执行一次计划任务
    scheduler.add_job(certificateMonitor.main, 'cron', hour=10, minute=30, second=0, timezone='Asia/Shanghai')
    # 每天下午 16点30分 执行一次计划任务
    scheduler.add_job(certificateMonitor.main, 'cron', hour=16, minute=30, second=0, timezone='Asia/Shanghai')
    # 一分钟执行一次(常用于测试的时候使用)
    scheduler.add_job(certificateMonitor.main, 'interval', minutes=1, timezone="Asia/Shanghai")
    scheduler.start()
    customLogger.info("APScheduled task has been started...")


@app.route("/")
async def index(request):
    return HTTPResponse("Hello Sanic Server...")


@app.route("/healthz", methods=["GET"])
async def health_check(request):
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return json({"status": "UP", "statusCode": "200", "currentTime": current_time})


def checkAlertChannelIsOpen():
    """
    检查是否开启了告警通道。0:关闭,1:开启
    """
    isEmailChannel = settings.email_settings["APP_MAIL_OPEN"]
    isFeishuChannel = settings.feishu_settings["APP_FS_OPEN"]
    isDingtalkChannel = settings.dingtalk_settings["APP_DINGTALK_OPEN"]
    customLogger.info(
        f"告警通道开启情况如下(1为开启,0为关闭): isEmailChannel: {isEmailChannel}, isDingtalkChannel: {isDingtalkChannel}, isFeishuChannel: {isFeishuChannel}"
    )
    if isEmailChannel == "1":
        customLogger.info(f"当前开启的告警通道为 email !")
    elif isFeishuChannel == "1":
        customLogger.info(f"当前开启的告警通道为 feishu !")
    elif isDingtalkChannel == "1":
        customLogger.info(f"当前开启的告警通道为 dingding !")
    elif isEmailChannel != "1" and isDingtalkChannel != "1" and isFeishuChannel != "1":
        customLogger.error(f"当前没有开启任意一个告警通道或者开启通道开关错误,请检查或至少开启一个告警通道然后运行该 APP ...")
        sys.exit(1)


if __name__ == "__main__":
    customLogger.info("Starting Sanic Server...")

    checkAlertChannelIsOpen()

    if app.config["APP_ENV"] == "dev":
        APP_MODE = True
    elif app.config["APP_ENV"] == "prod":
        APP_MODE = False
    else:
        APP_MODE = False

    app.run(host=app.config["APP_HOST"], port=int(app.config["APP_PORT"]), dev=APP_MODE, access_log=False)
