# -*- coding: utf-8 -*-

import os
import mysql.connector
from mysql.connector import connect
import logging
from scrapy.conf import settings
from mysql.connector import errorcode

logger = logging.getLogger(__name__)

class MYSQLDB(object):
    user = settings['MYSQLUSER']
    pwd = settings['MYSQLPWD']
    conn = connect(auth_plugin='mysql_native_password', user=user, password=pwd, host='localhost', database='spider_data', buffered=True)
    cur = conn.cursor(dictionary=True)

    @staticmethod
    def close():
        MYSQLDB.cur.close()
        MYSQLDB.conn.close()
        logger.info('MySQL connector and cursor closed !')



def mkdirs(dirs):
    ''' Create `dirs` if not exist. '''
    if not os.path.exists(dirs):
        os.makedirs(dirs)


'''
从taskqueue表查找一条状态status不为1：已经查找完成 或 2：正在查找，被锁住 的记录；
并且将状态设置为2：被锁，防止其他爬虫同时使用这一条。返回一个dict
!!! 方法需要改成，可选填参数，从而适应第一次get_keyword和上一个爬虫爬完了，需要更改task表状态然后在get_keyword
'''
def get_keyword():
    cur = MYSQLDB.cur

    query_keywords = 'select id,keywords,`table_name`,begintime,endtime,`now`,`status` from taskqueue where id=(select min(id) from taskqueue where status!=1 and status!=2)'
    try:
        cur.execute(query_keywords)
        result = cur.fetchall()
        if(None != result):
            # 如果能够查到结果，将结果集list的第一条的状态设置为2
            update_status(task_id=result[0]['id'], status=2)
            return result[0]       #返回值是result[0]，类型为dict，而不是result，类型为list
        else:
            logger.info('STOP: No Task, Stop Crawl.')
            return None
    except mysql.connector.Error as err:
        logger.info('Select keyword from task error: ' + str(err))
        return None


# 更新taskqueue表的状态
def update_status(task_id=None, status=1):
    conn = MYSQLDB.conn
    cur = MYSQLDB.cur
    if(None != task_id):
        if not isinstance(task_id, int):
            task_id = int(task_id)
        if not isinstance(status, int):
            status = int(status)
    update_sql = 'update taskqueue set status=%s where id=%s'
    try:
        cur.execute(update_sql, (status, task_id))
        conn.commit()
    except mysql.connector.Error as err:
        logger.info('Update task status id=%s status=%s failed cause: %s' % (status, task_id, str(err)))
    else:
        logger.debug('Update task status id=%s status=%s ' % (status, task_id))

# 给spider类提供的方法：换掉字符串里面的单引号、双引号和反斜杠
def escape_text(s:str):
    s = s.replace('\\', '\\\\').replace("'", "\\\'").replace('"', '\\\"')
    return s
    
