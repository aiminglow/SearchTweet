# -*- coding: utf-8 -*-


BOT_NAME = 'SearchTweet'

SPIDER_MODULES = ['SearchTweet.spiders']
NEWSPIDER_MODULE = 'SearchTweet.spiders'

# mysql connector配置和任务队列，推特内容，推特用户的表名
MYSQLUSER='my1988'
MYSQLPWD='mysql1988'
MYSQLHOST='localhost'
MYSQLPORT=3306
MYSQLDB='spider_data'
TASK_TABLE='taskqueue'
TWEET_TABLE='stockinfo'
USER_TABLE='tweetuser'

LOG_ENABLED = True
LOG_FILE = './log/debug.log'
LOG_ENCODING = 'UTF-8'
LOG_LEVEL = 'INFO'

ITEM_PIPELINES = {
    #'SearchTweet.pipelines.SaveToFilePipeline':100,
    #'SearchTweet.pipelines.SaveToMongoPipeline':100,
    'SearchTweet.pipelines.SaveToMySqlPipeline':100,
    'SearchTweet.pipelines.DefaultValuesPipeline':50,
}

UserAgent_List = [ "your useragent1", "your useragent2" ]

PROXIES = [
    {'ip_port':'127.0.0.1:8118', 'user_pwd':None},
]

DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware' : None,
    'SearchTweet.middlewares.RandomUserAgentMiddleware' : 400,
    # 'SearchTweet.middlewares.ProxyMiddleware' : 390
}

DEFAULT_REQUEST_HEADERS = {" ": " "}

# settings for where to save data on disk
SAVE_TWEET_PATH = './Data/tweet/'
SAVE_USER_PATH = './Data/user/'

COOKIES_ENABLED = False
