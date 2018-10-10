#!/bin/bash

NOHUPOUT=./nohup.out

nohup ./task_crawl.sh $1 > ${NOHUPOUT} 2>&1 &
