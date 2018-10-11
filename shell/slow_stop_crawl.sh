#!/bin/bash

SHELLPATH=$(pwd)
STOPFILE=$SHELLPATH/stop_crawl.flag

function check(){
    count=$(ps -aux | grep task_crawl | grep -v "grep" | grep -v "slow_stop_crawl" | wc -l )
    if [ 0 -eq ${count} ]
    then
        echo -e "\033[41;37m Task has stopped, wait shell close, spider will close later \033[0m"
        exit 0
    fi
}

if [ ! -f ${STOPFILE} ]
then
    touch ${STOPFILE}
fi
echo "Touch ${STOPFILE}"
echo "Closing spider slowly."
for ((i=0;i<12;i++))
do
    check
    sleep 5
done
echo -e "\033[41;37m Task shell have not closed within 1 minute, wait shell close. \033[0m"
exit 1