#!/bin/bash

SPIDER_NAME=$1
echo ${SPIDER_NAME}

function check(){
    count=$(ps -aux | grep ${SPIDER_NAME} | grep -v "grep" | grep -v "task_crawl" | wc -l )
    if [ ${count} -gt 0 ]
    then
        echo 'spider still alive'
    else
        echo 'spider is not alive'
        cd ../
        nohup scrapy crawl ${SPIDER_NAME} 2>&1 &
    fi
}

check

while true
do
    sleep 3
    check
done
