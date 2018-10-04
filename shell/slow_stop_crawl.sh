#!/bin/bash

WAITMIN=2
if [ -n "$1" ]
then
    let WAITMIN=$1
else
    echo 'You have not enter how many minute you will wait, auto set it 2 minute.'
fi
WAIT=$((${WAITMIN} * 12))
SHELLPATH=$(pwd)
STOPFILE=$SHELLPATH/stop_crawl.flag

function check(){
    count=$(ps -aux | grep task_crawl | grep -v "grep" | grep -v "slow_stop_crawl" | wc -l )
    if [ 0 -eq ${count} ]
    then
        echo 0 > ${STOPFILE}
        echo -e "\033[41;37m Spider has stopped, write [0] to ${STOPFILE} \033[0m"
        exit 0
    fi

}

echo 1 > ${STOPFILE}
echo "Write [1] to ${STOPFILE}"
echo "Closing spider slowly."
for ((i=0;i<${WAIT};i++))
do
    check
    sleep 5
done
echo -e "\033[41;37m Spider have not closed within ${WAITMIN} minute, wait shell close, it will close later. \033[0m"
exit 1