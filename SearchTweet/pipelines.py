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
        self.cur = self.conn.cursor()

    def find_one_tweet(self, tweet_id):
        query_tweet_sql = "select tweet_id from search_tweet where tweet_id='"+ tweet_id +"'"
        try:
            id = self.cur.execute(query_tweet_sql)
        except mysql.connector.Error as err:
            return False
        
        if(None == id):
            return False
        else:
            return True
        
    def insert_one_tweet(self, item:Tweet, spider):
        
        if(None == item["tweet_id"]):
            return None
        insert_tweet_sql = "insert into searchtweet(keywords,tweet_id,url,`datetime`,`text`,user_id,nbr_retweet,nbr_favorite,nbr_reply,is_reply,is_retweet,images,sumfullcard,sumurl) "
        insert_tweet_sql += "values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        try:
            self.cur.execute(insert_tweet_sql,data = (spider.query, item["ID"], item["url"], item["datetime"], item["text"], item["user_id"], item["nbr_retweet"], item["nbr_favorite"], item["nbr_reply"], item["is_reply"], item["is_retweet"], item["images"], item["sumfullcard"], item["sumurl"]))
        except mysql.connector.Error as err:
            logger.info(err)
        else:
            logger.info("insert one tweet success")
            self.conn.commit

    def find_one_user(self, user_id):
        query_user_sql = "select user_id from tweet_user where user_id='"+ user_id +"'"
        try:
            id = self.cur.execute(query_user_sql)
        except mysql.connector.Error as err:
            return False
        
        if(None == id):
            return False
        else:
            return True

    def insert_one_user(self, User):
        if(None == item["user_id"]):
            return None
        insert_user_sql = "insert into tweetuser(user_id,`name`,screen_name,avatar) "
        insert_user_sql += "values(%s,%s,%s,%s)"
        try:
            self.cur.execute(insert_user_sql,data = (item["ID"], item["name"], item["screen_name"], item["avatar"]))
        except mysql.connector.Error as err:
            logger.info(err)
        else:
            logger.info("insert one user success")
            self.conn.commit
    
    def process_item(self, item, spider):
        return None
    

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
