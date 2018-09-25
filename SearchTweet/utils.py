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
def get_keyword(task_id=-1):
    user = settings['MYSQLUSER']
    pwd = settings['MYSQLPWD']
    conn = connect(user=user, password=pwd, host='localhost', database='spider_data', buffered=True)
    cur = conn.cursor(dictionary=True)
    # 如果传入task_id参数，这个任务就认定是已经爬取完成了，这期间爬取的时间段很长，不知道爬到什么时候，
    # 不过幸亏是分页形式的查询，所以如果因为网络原因终端，前一页的内容已经存到了数据库了。
    # 本来计划将一个keyword的查询的时间分割成几个部分，然后分给不同的爬虫，让他们一起爬取，
    # 但是考虑到status状态字段设计起来太复杂了，所以不准备用这种方法了。
    # 而且之后用上了redis这种MQ以后，用一个生成任务的脚本不断给redis提供将时间分开的task，然后爬虫直接从redis取任务，
    # 这样各个模块之间多清楚啊，不用在这里捣鼓mysql的那一个字段了，也不用考虑数据库的锁和事务的问题了。

    #这里只需要对查出来的keywords、begintime、endtime做处理将他们结合起来就OK了
    if(-1 != task_id):
        update_status(conn, cur, task_id, status=1)
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
    
