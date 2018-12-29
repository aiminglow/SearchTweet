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
        self.task_msg = get_keyword()
        self.query = self.gen_query(self.task_msg)

        self.url = "https://twitter.com/i/search/timeline?l={}".format(lang)
        if not top_tweet:
            self.url = self.url + '&f=tweets'
        self.url = self.url + '&q=%s&src=typed&max_position=%s'

        self.crawl_user = crawl_user

    # 用从taskqueue表查询的结果中的keywords、begintime、endtime三个字段组成要进行查询的query
    def gen_query(self, task: dict):
        tmp = '%s since:%s until:%s'
        task_now = task['now'].strftime('%Y-%m-%d')
        # 如果task表的now字段不是默认值，而是修改过的，说明之前运行在这一条中断了，继续搜索这一条
        if '1980-01-01' != task_now:
            return tmp % (task['keywords'], task['begintime'].strftime('%Y-%m-%d'), task_now)
        else:
            return tmp % (task['keywords'], task['begintime'].strftime('%Y-%m-%d'), task['endtime'].strftime('%Y-%m-%d'))

    def start_requests(self):
        url = self.url % (quote(self.query), '')
        logger.info(
            'Prepare to crawl THE FIRST PAGE with keywords: ' + self.query)
        yield http.Request(url, callback=self.parse_page)

    def parse_page(self, response):
        # 回调这个函数之后，首先处理返回的json数据，json中的items_html是这一页的内容
        data = json.loads(response.body, encoding='utf-8')
        for item in self.prase_tweets_block(data['items_html']):
            yield item

        # 从json的min_position可以获得前往下一页的参数，对应下一条URL的max_position参数
        min_position = data['min_position']
        url = self.url % (quote(self.query), min_position)
        logger.debug(
            'Prepare to crawl A NEW PAGE with keywords[' + self.query + '] and min_position[' + min_position + ']')
        yield http.Request(url, callback=self.parse_page)

    def prase_tweets_block(self, html_page):
        page = Selector(text=html_page)
        items = page.xpath('//li[@data-item-type="tweet"]/div')
        for item in self.prase_tweet_item(items):
            yield item

    def prase_tweet_item(self, items):
        for item in items:
            tweet = Tweet()
            # tweet ID:这个ID具有唯一性
            ID = item.xpath('.//@data-tweet-id').extract()
            if not ID:
                continue
            tweet['ID'] = ID[0]

            tweet['url'] = item.xpath(
                './/@data-permalink-path').extract_first()

            tweet_datetime = item.xpath(
                './/small[@class="time"]/a/span/@data-time').extract_first()
            if None is not datetime:
                tweet['datetime'] = datetime.fromtimestamp(
                    int(tweet_datetime)).strftime('%Y-%m-%d %H:%M:%S')
            else:
                tweet['datetime'] = datetime(
                    1980, 1, 1, 0, 0, 0).strftime('%Y-%m-%d %H:%M:%S')

            '''
            下面这段内容是原封不动的复制tweet正文的内容：
            中兴通讯5月23日公告称，由于美国商务部工业与安全局激活拒绝令，本公司\r\n
                    A股 股份自2018年4月17日开市起停牌并将维持停牌。 
                    5月30日，明晟公司(MSCI)发布临时公告称，东方园林、海南橡胶、中国中铁、太钢不锈和中兴通讯将暂时
                    不被纳入MSCI 中国指数，也将从MSCI\r\n
                                A股 全球通指数和MSCI中国\r\n
                                            A股 大盘指数剔除\r\n
                                                        pic.twitter.com/qlynswoJLc \r\n
            '''
            # tweet的正文中包含大量的\n\r 空格和换行，有些正文最后还会有 pic.twitter.com开头的url，
            # 底下的escape_text方法负责删除换行和其他无用信息
            dirty_text = escape_text(''.join(item.xpath(
                './/div[@class="js-tweet-text-container"]/p//text()').extract()).replace('\n', '').replace(' # ', '#'))
            tweet['text'] = re.sub(r'pic.*', '', dirty_text)

            if '' == tweet['text']:
                continue

            tweet['user_id'] = item.xpath('.//@data-user-id').extract()[0]
            # tweet['usernameTweet'] = item.xpath('.//@data-screen-name').extract_first()

            # 回复的数量
            nbr_reply = item.xpath(
                './/span[@class="ProfileTweet-action--reply u-hiddenVisually"]/span[@class="ProfileTweet-actionCount"]/@data-tweet-stat-count').extract_first()
            if nbr_reply:
                tweet['nbr_reply'] = int(nbr_reply)
            else:
                tweet['nbr_reply'] = 0

            # 转发的数量
            nbr_retweet = item.css('span.ProfileTweet-action--retweet > span.ProfileTweet-actionCount').xpath(
                '@data-tweet-stat-count').extract_first()
            if nbr_retweet:
                tweet['nbr_retweet'] = int(nbr_retweet)
            else:
                tweet['nbr_retweet'] = 0

            # 点赞（喜欢）的数量
            nbr_favorite = item.css('span.ProfileTweet-action--favorite > span.ProfileTweet-actionCount').xpath(
                '@data-tweet-stat-count').extract_first()
            if nbr_favorite:
                tweet['nbr_favorite'] = int(nbr_favorite)
            else:
                tweet['nbr_favorite'] = 0

            # 是否是回复别人的一条评论（回复别人tweet的评论也算是一条tweet）
            is_reply = item.xpath(
                './/div[@class="ReplyingToContextBelowAuthor"]').extract()
            tweet['is_reply'] = is_reply != []

            # 是否是转发别人的推特
            is_retweet = item.xpath(
                './/span[@class="js-retweet-text"]').extract()
            tweet['is_retweet'] = is_retweet != []

            # 不存图片，存图片的URL
            images = item.xpath(
                './/div[@class="AdaptiveMedia-photoContainer js-adaptive-photo "]/@data-image-url').extract_first()
            if images:
                tweet['images'] = images

            # 视频
            # videos = item.xpath('.//video/@src').extract()
            # if videos:
            #     tweet['has_video'] = True
            #     tweet['videos'] = videos

            # summary card: 其他app转发到tweet的概要卡片，
            # 通产包含一张图片，一个标题，一句概要，点击则进入另外一个链接（这个概要卡片由twitter维护，卡片有自己的twitter.com域名下的URL）
            # 程序存储的分别是卡片URL，点击之后跳转的URL
            sumfullcard = item.xpath(
                './/div[@data-card-name="summary_large_image"]/@data-full-card-iframe-url').extract_first()
            sumurl = item.xpath(
                './/div[@data-card-name="summary_large_image"]/@data-card-url').extract_first()
            if sumurl:
                # tweet['has_summary'] = True
                tweet['sumfullcard'] = sumfullcard
                tweet['sumurl'] = sumurl

            yield tweet

            # 用户信息
            if self.crawl_user:
                user = User()
                user['ID'] = tweet['user_id']
                user['name'] = escape_text(
                    item.xpath('.//@data-name').extract_first())
                user['screen_name'] = item.xpath(
                    './/@data-screen-name').extract_first()
                user['avatar'] = item.xpath(
                    './/img[@class="avatar js-action-profile-avatar"]/@src').extract_first()

                yield user
