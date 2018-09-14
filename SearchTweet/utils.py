# -*- coding: utf-8 -*-

import os
import mysql.connector
from mysql.connector import connect
from logging import Logger
from scrapy.conf import settings
from mysql.connector import errorcode

def mkdirs(dirs):
    ''' Create `dirs` if not exist. '''
    if not os.path.exists(dirs):
        os.makedirs(dirs)
'''
从taskqueue表查找一条状态status不为1：已经查找完成 或 2：正在查找，被锁住 的记录；
并且将状态设置为2：被锁，防止其他爬虫同时使用这一条。返回一个dict
!!! 方法需要改成，可选填参数，从而适应第一次get_keyword和上一个爬虫爬完了，需要更改task表状态然后在get_keyword
'''
def get_keyword(*task_id):
    user = settings['MYSQLUSER']
    pwd = settings['MYSQLPWD']
    conn = connect(user=user, password=pwd, host='localhost', database='spider_data', buffered=True)
    cur = conn.cursor(dictionary=True)
    # 如果传入task_id参数，说明这个任务已经完成，将这条任务状态设置为1：已完成
    if(None != task_id):
        update_status(conn, cur, task_id[0], status=1)
    query_keywords = 'select id,keywords,`table_name`,begintime,endtime,`now`,`status` from taskqueue where id=(select min(id) from taskqueue where status!=1 and status!=2)'
    try:
        cur.execute(query_keywords)
        result = cur.fetchall()
        if(None != result):
            # 如果能够查到结果，将结果集list的第一条的状态设置为2
            update_status(conn, cur, result[0]['id'], status=2)
        return result[0]       #返回值是result[0]，类型为dict，而不是result，类型为list
    except mysql.connector.Error as err:
        print('select keyword from task error: ' + str(err))
        return None
    finally:
        cur.close()
        conn.close()


# 更新taskqueue表的状态
def update_status(conn, cur, task_id, status=1):
    if(None != task_id):
        if not isinstance(task_id, int):
            task_id = int(task_id)
        if not isinstance(status, int):
            status = int(status)
    update_sql = 'update taskqueue set status=%s where id=%s'
    try:
        cur.execute(update_sql, (status, task_id))
    except mysql.connector.Error as err:
        print('update task status id=%s status=%s failed: %s', (status, task_id),str(err))
    
