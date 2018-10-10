# -*- coding: utf-8 -*-

from scrapy.conf import settings
from SearchTweet.utils import mkdirs
from SearchTweet.items import Tweet, User
import os
import logging
import json
import mysql.connector
from mysql.connector import errorcode
from SearchTweet.utils import MYSQLDB, update_status
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
logger = logging.getLogger(__name__)

class SaveToMySqlPipeline(object):

    def __init__(self):
        self.conn = MYSQLDB.conn
        self.cur = MYSQLDB.cur
        
    def find_one_tweet(self, tweet_id:str, table_name:str):
        query_tweet_sql = "select tweet_id from "+ table_name +" where tweet_id='"+ tweet_id +"'"
        try:
            id = self.cur.execute(query_tweet_sql)
        except mysql.connector.Error as err:
            logger.info('find one tweet failed cause: ' + str(err))
            return False
        
        if(None == id):
            return False
        else:
            return True
        
    def insert_one_tweet(self, item:Tweet, spider):
        query = spider.query
        tweet_id = item['ID']
        if(None == tweet_id):
            return None
        insert_tweet_sql = "insert ignore into "+ spider.task_msg['table_name'] +"(keywords,tweet_id,url,`datetime`,`text`,user_id,nbr_retweet,nbr_favorite,nbr_reply,is_reply,is_retweet,images,sumfullcard,sumurl) "
        insert_tweet_sql += "values('{0}','{1}','{2}','{3}','{4}','{5}',{6},{7},{8},{9},{10},'{11}','{12}','{13}')"
        insert_tweet_sql = insert_tweet_sql.format(query, tweet_id, item["url"], item["datetime"], item["text"], item["user_id"], item["nbr_retweet"], item["nbr_favorite"], item["nbr_reply"], item["is_reply"], item["is_retweet"], item["images"], item["sumfullcard"], item["sumurl"])
        try:
            self.cur.execute(insert_tweet_sql)
            # self.conn.commit()
        except mysql.connector.Error as err:
            logger.info("FAILED：" + str(err) + " SQL: " + insert_tweet_sql)
        else:
            logger.debug("SUCCESS:insert one TWEET "+ tweet_id +" success with "+ query)
            

    def find_one_user(self, user_id:str):
        query_user_sql = "select user_id from tweetuser where user_id='"+ user_id +"'"
        try:
            id = self.cur.execute(query_user_sql)
        except mysql.connector.Error as err:
            logger.info('find one user failed cause: ' + str(err))
            return False
        
        if(None == id):
            return False
        else:
            return True

    def insert_one_user(self, item:User):
        user_id = item['ID']
        if(None == item["ID"]):
            return None
        insert_user_sql = "insert ignore into tweetuser(user_id,`name`,screen_name,avatar) "
        insert_user_sql += "values('%s','%s','%s','%s')"
        insert_user_sql = insert_user_sql % (item["ID"], item["name"], item["screen_name"], item["avatar"])
        try:
            self.cur.execute(insert_user_sql)
            # self.conn.commit
        except mysql.connector.Error as err:
            logger.info("FAILED：" + str(err) + " SQL: " + insert_user_sql)
        else:
            logger.debug("SUCCESS:insert one USER "+ user_id +" success")
            
    
    def process_item(self, item, spider):
        # 如果表不存在，就调用create_table创建这个表
        table_name = spider.task_msg['table_name']
        if not self.is_table_exist(table_name):
            self.create_table(table_name)
        if isinstance(item, Tweet):
            # 执行sql查重，如果重复则不插入。这里insert使用了ignore，所以可以不使用查重方法，下面插入User同理
            # if not self.find_one_tweet(item['ID'], table_name):
            #     self.insert_one_tweet(item, spider)
            self.insert_one_tweet(item, spider)
        elif isinstance(item, User):
            # if not self.find_one_user(item['ID']):
            #     self.insert_one_user(item)
            self.insert_one_user(item)
        else:
            logger.error("Item is neither tweet nor user !")

    def is_table_exist(self, table_name):
        query_table_sql = "SELECT table_name FROM information_schema.TABLES WHERE table_name='"+ table_name +"'"
        try:
            self.cur.execute(query_table_sql)
            result = self.cur.fetchall()
            if(([] == result) or (None == result)):
                return False
            else:
                return True
        except mysql.connector.Error as err:
            logger.info('Query table_name failed cause: %s', str(err))
            return False
        
        

    def create_table(self, table_name):
        create_table_sql = settings['TWEET_TABLE'] % (table_name)
        try:
            self.cur.execute(create_table_sql)
        except mysql.connector.Error as err:
            logger.info('Create table %s failed cause: %s' % (table_name, str(err)))

    def close_spider(self, spider):
        update_status(task_id=int(spider.task_msg['id']), status=1)
        logger.info('TASK: Task id='+str(spider.task_msg['id'])+' keywords='+spider.task_msg['keywords']+' status has been modify to [1]')
        MYSQLDB.close()
        logger.info('CLOSE: There is a duplicate url, prepare to close spider')
        
class DefaultValuesPipeline(object):
    def process_item(self, item, spider):
        if isinstance(item, Tweet):
            item.setdefault('images', '-1')
            item.setdefault('sumfullcard', '-1')
            item.setdefault('sumurl', '-1')
        return item

class SaveToFilePipeline(object):
    ''' pipeline that save data to disk '''
    def __init__(self):
        self.saveTweetPath = settings['SAVE_TWEET_PATH']
        self.saveUserPath = settings['SAVE_USER_PATH']
        mkdirs(self.saveTweetPath) # ensure the path exists
        mkdirs(self.saveUserPath)


    def process_item(self, item, spider):
        if isinstance(item, Tweet):
            savePath = os.path.join(self.saveTweetPath, item['ID'])
            if os.path.isfile(savePath):
                pass # simply skip existing items
                ### or you can rewrite the file, if you don't want to skip:
                # self.save_to_file(item,savePath)
                # logger.info("Update tweet:%s"%dbItem['url'])
            else:
                self.save_to_file(item,savePath)
                logger.debug("Add tweet:%s" %item['url'])

        elif isinstance(item, User):
            savePath = os.path.join(self.saveUserPath, item['ID'])
            if os.path.isfile(savePath):
                pass # simply skip existing items
                ### or you can rewrite the file, if you don't want to skip:
                # self.save_to_file(item,savePath)
                # logger.info("Update user:%s"%dbItem['screen_name'])
            else:
                self.save_to_file(item, savePath)
                logger.debug("Add user:%s" %item['screen_name'])

        else:
            logger.info("Item type is not recognized! type = %s" %type(item))


    def save_to_file(self, item, fname):
        ''' input: 
                item - a dict like object
                fname - where to save
        '''
        with open(fname,'w') as f:
            json.dump(dict(item), f)
