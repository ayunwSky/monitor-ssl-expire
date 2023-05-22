#!/bin/bash

DATE=$(date +'%Y%m%d')
TIMESTAMP=$(date +%s)

# pip 配置代理后拷贝该Dockerfile来构建镜像
# cp ./Dockerfiles/Dockerfile-withproxy ./Dockerfile

# 使用国内 pip 源的Dockerfile
cp ./Dockerfiles/Dockerfile-noproxy ./Dockerfile
docker build -t monitor-ssl-expire:v${DATE}-v${TIMESTAMP} -f ./Dockerfile .
cat ./docker-compose.yml | grep -Eo v[0-9]{8}\-v[0-9]{10} | xargs -i sed -i s@{}@v${DATE}-v${TIMESTAMP}@g docker-compose.yml
rm -f ./Dockerfile
