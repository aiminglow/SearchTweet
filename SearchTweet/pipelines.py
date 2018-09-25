# -*- coding: utf-8 -*-

from scrapy.conf import settings
from SearchTweet.utils import mkdirs
from SearchTweet.items import Tweet, User
import os
import logging
import json
import mysql.connector
from mysql.connector import errorcode
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
logger = logging.getLogger(__name__)

class SaveToMySqlPipeline(object):

    def __init__(self):
        user = settings["MYSQLUSER"]
        pwd = settings["MYSQLPWD"]
        self.conn = mysql.connector.connect(user=user, password=pwd, 
                    host="localhost", database="spider_data", buffered=True)
        self.cur = self.conn.cursor(dictionary=True)
        
    def find_one_tweet(self, tweet_id:str, table_name:str):
        query_tweet_sql = "select tweet_id from "+ table_name +" where tweet_id='"+ tweet_id +"'"
        try:
            id = self.cur.execute(query_tweet_sql)
        except mysql.connector.Error as err:
            return False
        
        if(None == id):
            return False
        else:
            return True
        
    def insert_one_tweet(self, item:Tweet, spider):
        
        if(None == item["ID"]):
            return None
        insert_tweet_sql = "insert ignore into "+ spider.task_msg['table_name'] +"(keywords,tweet_id,url,`datetime`,`text`,user_id,nbr_retweet,nbr_favorite,nbr_reply,is_reply,is_retweet,images,sumfullcard,sumurl) "
        insert_tweet_sql += "values('{0}','{1}','{2}','{3}','{4}','{5}',{6},{7},{8},{9},{10},'{11}','{12}','{13}')"
        try:
            self.cur.execute(insert_tweet_sql.format(spider.query, item["ID"], item["url"], item["datetime"], item["text"], item["user_id"], item["nbr_retweet"], item["nbr_favorite"], item["nbr_reply"], item["is_reply"], item["is_retweet"], item["images"], item["sumfullcard"], item["sumurl"]))
            self.conn.commit()
        except mysql.connector.Error as err:
            logger.info(err)
        else:
            logger.info("insert one tweet success")
            

    def find_one_user(self, user_id:str):
        query_user_sql = "select user_id from tweetuser where user_id='"+ user_id +"'"
        try:
            id = self.cur.execute(query_user_sql)
        except mysql.connector.Error as err:
            return False
        
        if(None == id):
            return False
        else:
            return True

    def insert_one_user(self, item:User):
        if(None == item["ID"]):
            return None
        insert_user_sql = "insert ignore into tweetuser(user_id,`name`,screen_name,avatar) "
        insert_user_sql += "values('%s','%s','%s','%s')"
        try:
            self.cur.execute(insert_user_sql % (item["ID"], item["name"], item["screen_name"], item["avatar"]))
        except mysql.connector.Error as err:
            logger.info(err)
        else:
            logger.info("insert one user success")
            self.conn.commit
    
    def process_item(self, item, spider):
        # 如果表不存在，就调用create_table创建这个表
        table_name = spider.task_msg['table_name']
        if not self.is_table_exist(table_name):
            self.create_table(table_name)
        if isinstance(item, Tweet):
            if not self.find_one_tweet(item['ID'], table_name):
                self.insert_one_tweet(item, spider)
            
        elif isinstance(item, User):
            if not self.find_one_user(item['ID']):
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
            logger.info('query table_name failed cause: %s', (err))
            return False
        
        

    def create_table(self, table_name):
        create_table_sql = settings['TWEET_TABLE'] % (table_name)
        try:
            self.cur.execute(create_table_sql)
        except mysql.connector.Error as err:
            logger.info('create table %s failed cause: %s' % (table_name, err))
        
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
