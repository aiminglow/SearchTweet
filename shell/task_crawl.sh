#!/bin/bash

SPIDER_NAME=$1
echo ${SPIDER_NAME}
SHELLPATH=$(pwd)
STOPFILE=$SHELLPATH/stop_crawl.flag
SCRAPYPATH=$SHELLPATH/..
LOGPATH=$SHELLPATH/../log

function check(){
    count=$(ps -aux | grep ${SPIDER_NAME} | grep -v "grep" | grep -v "task_crawl" | wc -l )
    if [ ${count} -gt 0 ]
    then
        echo "[$(date +"%Y-%m-%d %H:%M:%S")][SHELL]Spider is still alive."
    else
        echo "[$(date +"%Y-%m-%d %H:%M:%S")][SHELL]Spider is not alive."
        echo "[$(date +"%Y-%m-%d %H:%M:%S")][SHELL]Start crawl task [${num}]."
        cd ${SCRAPYPATH}
        scrapy crawl ${SPIDER_NAME}
        echo "[$(date +"%Y-%m-%d %H:%M:%S")][SHELL]Spider crawl task [${num}] complete."
    fi
}


echo 0 > ${STOPFILE}
for ((num=1;num>-1;num++))
do
    cd ${SHELLPATH}
    line=$(head -1 stop_crawl.flag)
    echo ${line}
    if [ 1 -eq ${line} ]
    then
        exit 0
    fi
    sleep 2
    check
done
