# -*- coding: utf-8 -*-

from scrapy.conf import settings
from SearchTweet.utils import mkdirs
from SearchTweet.items import Tweet, User
import os
import logging
import json
import mysql.connector
from mysql.connector import errorcode
from SearchTweet.utils import MySqlUtil, update_status

logger = logging.getLogger(__name__)

class SaveToMySqlPipeline(object):


    def __init__(self):
        self.msu = MySqlUtil()
        self.count = 0
        self.MYSQLCACHE = 100
            
    def insert_one_tweet(self, item:Tweet, spider):
        query = spider.query
        tweet_id = item['ID']
        if(None == tweet_id):
            return
        insert_tweet_sql = "insert ignore into "+ settings['TWEET_TABLE']\
                           + "(keywords,tweet_id,url,`datetime`,`text`,user_id,nbr_retweet,nbr_favorite,nbr_reply,is_reply,is_retweet,images,sumfullcard,sumurl) "\
                           + "values('{0}','{1}','{2}','{3}','{4}','{5}',{6},{7},{8},{9},{10},'{11}','{12}','{13}')"
        insert_tweet_sql = insert_tweet_sql.format(query, tweet_id, item["url"], item["datetime"], item["text"], item["user_id"], item["nbr_retweet"]\
                           , item["nbr_favorite"], item["nbr_reply"], item["is_reply"], item["is_retweet"], item["images"], item["sumfullcard"], item["sumurl"])

        def _insert_one_tweet(self):
            try:
                self.msu.cur.execute(insert_tweet_sql)
            except mysql.connector.Error as err:
                logger.info("FAILED：" + str(err) + " SQL: " + insert_tweet_sql)
            else:
                logger.debug("SUCCESS:insert one TWEET "+ tweet_id +" success with "+ query)
        self.insert(_insert_one_tweet)
            
    def insert_one_user(self, item:User):
        user_id = item['ID']
        if(None == item["ID"]):
            return None
        insert_user_sql = "insert ignore into "+ settings["USER_TABLE"] +" (user_id,`name`,screen_name,avatar) "
        insert_user_sql += "values('%s','%s','%s','%s')"
        insert_user_sql = insert_user_sql % (item["ID"], item["name"], item["screen_name"], item["avatar"])

        def _insert_one_user(self):
            try:
                self.msu.cur.execute(insert_user_sql)
            except mysql.connector.Error as err:
                logger.info("FAILED：" + str(err) + " SQL: " + insert_user_sql)
            else:
                logger.debug("SUCCESS:insert one USER "+ user_id +" success")
        self.insert(_insert_one_user)

    def insert(self, insert_method):
        if self.count == 0:
            self.msu.connect()
            self.msu.insert_before()
        if self.count <= self.MYSQLCACHE:
            insert_method(self)
            self.count += 1
        elif self.count > self.MYSQLCACHE:
            self.msu.insert_after()
            self.count = 0
            
    def process_item(self, item, spider):
        if isinstance(item, Tweet):
            self.insert_one_tweet(item, spider)
        elif isinstance(item, User):
            self.insert_one_user(item)
        else:
            logger.error("Item is neither tweet nor user !")

    def close_spider(self, spider):
        update_status(int(spider.task_msg['id']), spider.task_msg['keywords'], 1)
        
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
