#!/bin/bash

DATE=$(date +'%Y%m%d')
TIMESTAMP=$(date +%s)
docker build -t monitor-ssl-expire:v${DATE}-v${TIMESTAMP} -f ./Dockerfile .
cat ./docker-compose.yml | grep -Eo v[0-9]{8}\-v[0-9]{10} | xargs -i sed -i s@{}@v${DATE}-v${TIMESTAMP}@g docker-compose.yml
