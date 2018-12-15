# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
import random
from scrapy.conf import settings
# from scrapy.dupefilter import RFPDupeFilter
# from SearchTweet.utils import MYSQLDB, update_status

# 利用中间件，重写父类方法，关闭过滤重复的方法
# class UpdateTaskStatusDupefilter(RFPDupeFilter):
#     def __init__(self, path=None):
#         self.urls_seen = set()
#         RFPDupeFilter.__init__(self, path)

#     def request_seen(self, request, spider):
#         if request.url in self.urls_seen:
#             update_status(task_id=int(spider.task_msg['id']), status=1)
#             MYSQLDB.close()
#             return True
#         else:
#             self.urls_seen.add(request.url)



class RandomUserAgentMiddleware(object):

    # 随机设置 User-agent
    def process_request( self, request, spider ):
        ua = random.choice(settings['USERAGENTLIST'])
        if ua:
            request.headers.setdefault( 'User-Agent', ua)