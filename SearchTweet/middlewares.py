# -*- coding: utf-8 -*-


import random
from scrapy.conf import settings
import base64


class ProxyMiddleware(object):

    def process_request(self, request, spider):
        proxy = random.choice(settings["PROXIES"])
        if proxy['user_pwd'] is not None:
            request.meta['proxy'] = "http://%s" % proxy['ip_port']
            request.meta['proxy'] = "https://%s" % proxy['ip_port']
            encoded_user_pwd = base64.encodestring(proxy['user_pwd'])
            request.headers['Proxy-Authorization'] = 'Basic ' + encoded_user_pwd
        else:
            request.meta['proxy'] = "http://%s" % proxy['ip_port']


class RandomUserAgentMiddleware(object):

    # 随机设置 User-agent
    def process_request(self, request, spider ):
        ua = random.choice(settings['USERAGENTLIST'])
        if ua:
            request.headers.setdefault('User-Agent', ua)
