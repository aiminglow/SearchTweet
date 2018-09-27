# -*- coding: utf-8 -*-

from scrapy.spiders import CrawlSpider, Rule
from scrapy import http
from scrapy.selector import Selector
from SearchTweet.items import Tweet, User
from datetime import datetime
import re
import json
import time
import logging
from scrapy.conf import settings
try:
    from urllib import quote  # Python 2.X
except ImportError:
    from urllib.parse import quote  # Python 3+
from SearchTweet.utils import get_keyword, escape_text

logger = logging.getLogger(__name__)

class SearchTweet(CrawlSpider):

    name = 'search_tweet'
    allowed_domains = ['twitter.com']

    def __init__(self, query='', lang='', crawl_user=True, top_tweet=False):
        
        # 要想在这里关闭spider，要给方法传入spider对象，但是这时候spider的init方法还没执行完呢，对象还没创建呢！
        # 所以说，这个task_msg的位置不好。
        # self.task_msg = get_keyword()
        # self.query = self.gen_query(self.task_msg)
        self.url = "https://twitter.com/i/search/timeline?l={}".format(lang)

        if not top_tweet:
            self.url = self.url + '&f=tweets'

        self.url = self.url + '&q=%s&src=typed&max_position=%s'

        self.crawl_user = crawl_user

    # 用从taskqueue表查询的结果中的keywords、begintime、endtime三个字段组成要进行查询的query
    def gen_query(self, task:dict):
        tmp = '%s since:%s until:%s'
        task_now = task['now'].strftime('%Y-%m-%d')
        # 如果task表的now字段不是默认值，而是修改过的，说明之前运行在这一条中断了，继续搜索这一条
        if('1980-01-01' != task_now):
            # 搜索的keywords前面加上 $ 符号，能够更精准的搜索股票相关的tweet
            return tmp % ('$' + task['keywords'], task['begintime'].strftime('%Y-%m-%d'), task_now)
        else:    
            return tmp % ('$' + task['keywords'], task['begintime'].strftime('%Y-%m-%d'), task['endtime'].strftime('%Y-%m-%d'))


    def start_requests(self):
        # 调用utils的方法get_keyword，获得task任务，其中包括查询关键词keywords和查询时间范围
        self.task_msg = get_keyword()
        self.query = self.gen_query(self.task_msg)
        url = self.url % (quote(self.query), '')
        logger.info('Prepare to crawl THE FIRST PAGE with url: ' + url)
        yield  http.Request(url, 
                            meta={'proxy' : 'http://127.0.0.1:8118'},
                            headers=settings['DEFAULT_REQUEST_HEADERS'],
                            #cookies=settings['DEFAULT_COOKIE'],
                            callback=self.parse_page)
    
    def parse_page(self, response):
        # handle current page
        data = json.loads(response.body, encoding='utf-8')
        for item in self.prase_tweets_block(data['items_html']):
            yield item
        
        # the next page
        min_postion = data['min_position']
        # 如果没有下一页，设置上一个任务状态为1：已完成，并且取一个新的关键词进行查询
        if None == min_postion:
            self.task_msg = get_keyword(self.task_msg['id'])  # 需要设置一个参数可以填或者不填的get_keyword方法，
                                           # 爬虫init的时候不传参，调用parse_page的时候需要传上一个task_msg的id，让方法把这条的状态置为1：已完成
            self.query = self.gen_query(self.task_msg)
            logger.info('Prepare to crawl a new page with A NEW QUERY: ' + self.query)

        url = self.url % (quote(self.query), min_postion)            
        logger.debug('Prepare to crawl A NEW PAGE with URL: ' + url)
        yield http.Request(url,
                            meta={'proxy' : 'http://127.0.0.1:8118'},
                            headers=settings['DEFAULT_REQUEST_HEADERS'],
                            #cookies=settings['DEFAULT_COOKIE'],
                            callback=self.parse_page)
            
        
    def prase_tweets_block(self, html_page):
        page = Selector(text=html_page)
        items = page.xpath('//li[@data-item-type="tweet"]/div')
        for item in self.prase_tweet_item(items):
            yield item

    def prase_tweet_item(self, items):
        for item in items:
            tweet = Tweet()
            # tweet ID
            ID = item.xpath('.//@data-tweet-id').extract()
            if not ID:
                continue
            tweet['ID'] = ID[0]

            # tweet-url
            tweet['url'] = item.xpath('.//@data-permalink-path').extract_first()

            #tweet datetime ?which timezone it is?
            tweet_datetime = item.xpath('.//small[@class="time"]/a/span/@data-time').extract_first()
            if None is not datetime:
                tweet['datetime'] = datetime.fromtimestamp(int(tweet_datetime)).strftime('%Y-%m-%d %H:%M:%S')
            else:
                tweet['datetime'] = datetime(1980,1,1,0,0,0).strftime('%Y-%m-%d %H:%M:%S')
            
            # tweet text. why the # and @ has space ?     
            # can i drop the url-text:pic.twitter.com/qlynswoJLc with regular expression ?
            '''中兴通讯5月23日公告称，由于美国商务部工业与安全局激活拒绝令，本公司\r\n
                    A股 股份自2018年4月17日开市起停牌并将维持停牌。 
                    5月30日，明晟公司(MSCI)发布临时公告称，东方园林、海南橡胶、中国中铁、太钢不锈和中兴通讯将暂时
                    不被纳入MSCI 中国指数，也将从MSCI\r\n
                                A股 全球通指数和MSCI中国\r\n
                                            A股 大盘指数剔除\r\n
                                                        pic.twitter.com/qlynswoJLc \r\n
            '''
            dirty_text = escape_text(''.join(item.xpath('.//div[@class="js-tweet-text-container"]/p//text()').extract()
             ).replace('\n','').replace(' # ', '#'))
            tweet['text'] = re.sub(r'pic.*','', dirty_text)

            if ''==tweet['text']:
                continue

            # get user id
            tweet['user_id'] = item.xpath('.//@data-user-id').extract()[0]
            # tweet['usernameTweet'] = item.xpath('.//@data-screen-name').extract_first()

            # number of reply retweet favorite
            nbr_reply = item.xpath(
                './/span[@class="ProfileTweet-action--reply u-hiddenVisually"]/span[@class="ProfileTweet-actionCount"]/@data-tweet-stat-count').extract_first()
            if nbr_reply:
                tweet['nbr_reply'] = int(nbr_reply)
            else:
                tweet['nbr_reply'] = 0

            nbr_retweet = item.css('span.ProfileTweet-action--retweet > span.ProfileTweet-actionCount').xpath(
                '@data-tweet-stat-count').extract_first()
            if nbr_retweet:
                tweet['nbr_retweet'] = int(nbr_retweet)
            else:
                tweet['nbr_retweet'] = 0

            nbr_favorite = item.css('span.ProfileTweet-action--favorite > span.ProfileTweet-actionCount').xpath(
                '@data-tweet-stat-count').extract_first()
            if nbr_favorite:
                tweet['nbr_favorite'] = int(nbr_favorite)
            else:
                tweet['nbr_favorite'] = 0

            # is reply.  is retweet: my first page have no retweeted tweet
            is_reply = item.xpath('.//div[@class="ReplyingToContextBelowAuthor"]').extract()
            tweet['is_reply'] = is_reply != []

            is_retweet = item.xpath('.//span[@class="js-retweet-text"]').extract()
            tweet['is_retweet'] = is_retweet != []

            # images
            images = item.xpath('.//div[@class="AdaptiveMedia-photoContainer js-adaptive-photo "]/@data-image-url').extract_first()
            if images:
                # tweet['has_image'] = True
                tweet['images'] = images

            # videos
            # videos = item.xpath('.//video/@src').extract()
            # if videos:
            #     tweet['has_video'] = True
            #     tweet['videos'] = videos

            # summary card
            sumfullcard = item.xpath('.//div[@data-card-name="summary_large_image"]/@data-full-card-iframe-url').extract_first()
            sumurl = item.xpath('.//div[@data-card-name="summary_large_image"]/@data-card-url').extract_first()
            if sumurl:
                # tweet['has_summary'] = True
                tweet['sumfullcard'] = sumfullcard
                tweet['sumurl'] = sumurl

            # only crawl top tweet
            yield tweet

            # crawl_user
            if self.crawl_user:
                user = User()
                user['ID'] = tweet['user_id']
                user['name'] = escape_text(item.xpath('.//@data-name').extract_first())
                user['screen_name'] = item.xpath('.//@data-screen-name').extract_first()
                user['avatar'] = item.xpath('.//img[@class="avatar js-action-profile-avatar"]/@src').extract_first()

                yield user

            