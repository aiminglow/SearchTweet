# -*- coding: utf-8 -*-

import mysql.connector
from mysql.connector import connect

user = 'dev'
pwd = 'maisekou'
conn = connect(user=user, password=pwd, host='localhost', database='spider_data', buffered=True)
cur = conn.cursor(dictionary=True)
# query_keywords = 'select id,keywords,pre_table_name,begintime,endtime,`now`,`status` from taskqueue where id=(select min(id) from taskqueue where status!=1 and status!=2)'
query_keywords = 'select * from taskqueue'
try:
    cur.execute(query_keywords)
    print(cur.column_names)
    # result = []
    # print(type(result))
    # for val in cur.fetchall():
        # print(val)
        # result.append(val)
    result = cur.fetchall()
    print(type(result[0]))
    print(result[0]['id'])
except mysql.connector.Error as err:
    print('select keyword from task error: ' + str(err))
finally:
    cur.close()
    conn.close()
    