#!/bin/bash


cd ../
nohup scrapy crawl $1 >./log/nohup.out 2>&1 &
