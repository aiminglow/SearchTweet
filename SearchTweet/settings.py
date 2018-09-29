# -*- coding: utf-8 -*-

# Scrapy settings for SearchTweet project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://doc.scrapy.org/en/latest/topics/settings.html
#     https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://doc.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'SearchTweet'

SPIDER_MODULES = ['SearchTweet.spiders']
NEWSPIDER_MODULE = 'SearchTweet.spiders'

MYSQLUSER='my1988'
MYSQLPWD='mysql1988'

TWEET_TABLE='''create table %s (
            id int(13) primary key not null auto_increment comment '主键，自增',
            keywords varchar(50) not null comment '查询这条tweet时使用的关键词和时间区间的组合',
            tweet_id char(20) not null comment 'tweet的唯一id',
            url varchar(40) not null comment 'tweet对应的url的suf部分，twitter.com+url 即可访问对应的tweet',
            `datetime` timestamp comment 'tweet发出时间',
            `text` varchar(280) comment 'tweet文字内容',
            user_id varchar(25) comment '本条tweet的用户id，对应tweet_user表里的主键。之后不会使用到联合查询，为了插入效率，不设置外键，减少插入过程的约束检查时间',
            nbr_retweet int(6) comment '转发数',
            nbr_favorite int(6) comment '点赞数',
            nbr_reply int(6) comment '回复数',
            is_reply boolean comment '本条tweet是不是一条回复',
            is_retweet boolean comment '本条tweet是不是一条转发',
            images varchar(120) comment '包含的图片的tweet的图片的url',
            sumfullcard varchar(80) comment 'twitter.com将tweet中包含的summary card单独存成一个html，他们都有一个自己的url，这里存的是summary card的html的url，这个html包括summary card的标题，summary，图片，domain等信息',
            sumurl varchar(80) comment '点击summary card跳转到的url',
            unique index `tweet_id_unique_index` (`tweet_id`) comment 'tweet_id的唯一索引，用来查重')
            engine=InnoDB DEFAULT CHARSET=utf8mb4;
            '''

LOG_ENABLED = True
LOG_FILE = './log/debug.log'
LOG_ENCODING = 'UTF-8'
LOG_LEVEL = 'INFO'

ITEM_PIPELINES = {
    #'SearchTweet.pipelines.SaveToFilePipeline':100,
    #'SearchTweet.pipelines.SaveToMongoPipeline':100, # replace `SaveToFilePipeline` with this to use MongoDB
    'SearchTweet.pipelines.SaveToMySqlPipeline':100, # replace `SaveToFilePipeline` with this to use MySQL
    'SearchTweet.pipelines.DefaultValuesPipeline':50,
}

DUPEFILTER_CLASS ='SearchTweet.middlewares.UpdateTaskStatusDupefilter'

DEFAULT_REQUEST_HEADERS = {
    'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    'Accept-Language': "zh-CN,zh;q=0.9,en;q=0.8",
    "Accept-Encoding":"gzip, deflate, br",
    #"Connection":"keep-alive",
    #"Host":"baidu.cn",
    #"Referer":"http://ris.szpl.gov.cn/bol/projectdetail.aspx",
    "User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/68.0.3440.106 Chrome/68.0.3440.106 Safari/537.36",
    #"Origin":"http://baidu.com",
    'Upgrade-Insecure-Requests':'1',
    'Content-Type':'application/x-www-form-urlencoded'}

DEFAULT_COOKIE = ['_twitter_sess=you cookie']


# settings for where to save data on disk
SAVE_TWEET_PATH = './Data/tweet/'
SAVE_USER_PATH = './Data/user/'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'SearchTweet (+http://www.yourdomain.com)'

# Obey robots.txt rules
# ROBOTSTXT_OBEY = True

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://doc.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
#DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
#}

# Enable or disable spider middlewares
# See https://doc.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'SearchTweet.middlewares.SearchtweetSpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#DOWNLOADER_MIDDLEWARES = {
#    'SearchTweet.middlewares.SearchtweetDownloaderMiddleware': 543,
#}

# Enable or disable extensions
# See https://doc.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See https://doc.scrapy.org/en/latest/topics/item-pipeline.html
#ITEM_PIPELINES = {
#    'SearchTweet.pipelines.SearchtweetPipeline': 300,
#}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'
