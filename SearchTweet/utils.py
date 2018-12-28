# -*- coding: utf-8 -*-

import os
import mysql.connector
from mysql.connector import connect
import logging
from scrapy.conf import settings
from mysql.connector import errorcode

logger = logging.getLogger(__name__)

class MySqlUtil(object):

    def __init__(self, con_now=False):
        if con_now:
            self.connect()
            
    def connect(self):
        self.conn = connect(auth_plugin='mysql_native_password', user=settings['MYSQLUSER'], password=settings['MYSQLPWD']\
                    , host=settings['MYSQLHOST'], port=settings['MYSQLPORT'], database=settings['MYSQLDB'], buffered=True)
        self.cur = self.conn.cursor(dictionary=True)
    
    def insert_before(self):
        self.cur.execute('SET autocommit=0')
        self.cur.execute('SET unique_checks=0')
        self.cur.execute('SET foreign_key_checks=0')

    def insert_after(self):
        self.conn.commit()
        self.cur.execute('SET foreign_key_checks=1')
        self.cur.execute('SET unique_checks=1')
        self.cur.close()
        self.conn.close()
        logger.debug('MySql commit and connector/cursor close !')

    def commit(self):
        self.conn.commit()
    
    def close(self):
        self.cur.close()
        self.conn.close()

    # 更新taskqueue表的状态
    def update_status(self, task_id=None, keywords=None, status=1):
        assert task_id is not None, "[%s] task_id can not be None Type!" % (self.update_status.__name__)
        update_sql = 'update '+ settings['TASK_TABLE'] +' set status=%s where id=%s'
        try:
            self.cur.execute(update_sql, (status, task_id))
            self.insert_after()
        except mysql.connector.Error as err:
            logger.info('Update task status id=%s status=%s failed cause: %s' % (status, task_id, str(err)))
        else:
            logger.info('TASK: Task id='+str(task_id)+' keywords='+keywords+' status has been modify to [' + str(status) + ']')


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
    msu = MySqlUtil(True)
    query_keywords = 'select id,keywords,begintime,endtime,`now`,`status` from '+ settings['TASK_TABLE'] +' where id=(select min(id) from taskqueue where status!=1 and status!=2)'
    try:
        msu.cur.execute(query_keywords)
        result = msu.cur.fetchall()
        if result is not None:
            # 如果能够查到结果，将结果集list的第一条的状态设置为2
            msu.update_status(result[0]['id'], result[0]['keywords'], status=2)
            return result[0]       #返回值是result[0]，类型为dict，而不是result，类型为list
        else:
            logger.info('STOP: No Task, Stop Crawl.')
            return None
        msu.close()
    except mysql.connector.Error as err:
        msu.close()
        logger.info('Select keyword from task error: ' + str(err))

# 给spider类提供的方法：换掉字符串里面的单引号、双引号和反斜杠
def escape_text(s:str):
    s = s.replace('\\', '\\\\').replace("'", "\\\'").replace('"', '\\\"')
    return s
