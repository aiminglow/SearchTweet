#!/bin/bash

SPIDER_NAME=$1
SHELLPATH=$(pwd)
STOPFILE=$SHELLPATH/stop_crawl.flag
SCRAPYPATH=$SHELLPATH/..
NOHUPOUT=$SHELLPATH/../log/nohup.out

function check(){
    count=$(ps -aux | grep ${SPIDER_NAME} | grep -v "grep" | grep -v "task_crawl" | wc -l )
    if [ ${count} -eq 0 ]
    then
        cd ${SCRAPYPATH}
        nohup scrapy crawl ${SPIDER_NAME} >${NOHUPOUT} 2>&1 &
    fi
}


echo 0 > ${STOPFILE}
while true
do
    cd ${SHELLPATH}
    line=$(head -1 stop_crawl.flag)
    echo ${line}
    if [ 1 -eq ${line} ]
    then
        exit 0
    fi
    check
    sleep 10
done
