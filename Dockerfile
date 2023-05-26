FROM python:3.11.2
LABEL Author="ayunwSky"

ENV PYTHONIOENCODING=utf-8 \
    TZ=Asia/Shanghai \
    DEBIAN_FRONTEND=noninteractive

RUN mkdir -p /data/monitor-ssl-expire/src/

COPY src/ /data/monitor-ssl-expire/src
COPY requirements.txt /data/monitor-ssl-expire/
COPY startApp.sh /startApp.sh

RUN apt install -y tzdata \
    && ln -fs /usr/share/zoneinfo/${TZ} /etc/localtime \
    && echo ${TZ} > /etc/timezone \
    && dpkg-reconfigure --frontend noninteractive tzdata \
    && pip install --no-cache-dir -r /data/monitor-ssl-expire/requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple \
    && chmod +x /startApp.sh \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /data/monitor-ssl-expire

EXPOSE 8080

CMD ["/startApp.sh"]
