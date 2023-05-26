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
    scheduler.start()
    customLogger.info("APScheduled task has been started...")


@app.route("/")
async def index(request):
    return HTTPResponse("Hello Sanic Server...")


@app.route("/healthz", methods=["GET"])
async def health_check(request):
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return json({"status": "UP", "statusCode": "200", "currentTime": current_time})


if __name__ == "__main__":
    customLogger.info("Starting Sanic Server...")

    if app.config["APP_ENV"] == "dev":
        APP_MODE = True
    elif app.config["APP_ENV"] == "prod":
        APP_MODE = False
    else:
        APP_MODE = False

    app.run(host=app.config["APP_HOST"], port=int(app.config["APP_PORT"]), dev=APP_MODE, access_log=False)
