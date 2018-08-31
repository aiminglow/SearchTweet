# -*- coding: utf-8 -*-

from scrapy.selector import Selector
from SearchTweet.items import Tweet, User
from datetime import datetime

agu_no_html = open("F:\Python\PythonWorkSpace\practiceSpider\\agu_no_html.html")



def prase_tweets_block(html_page):
    page = Selector(html_page)
    items = page.xpath('//li[@data-item-type="tweet"]/div').extract()
    for item in prase_tweet_item(items):
        yield item

def prase_tweet_item(items):
    for item in items:
        tweet = Tweet()
        # tweet ID
        ID = item.xpath('.//@data-tweet-id').extract()
        if not ID:
            continue
        tweet['ID'] = ID[0]

        # tweet-url
        tweet['url'] = item.xpath('.//@data-permalink-path').extract()

        #tweet datetime ?which timezone it is?
        tweet['datetime'] = datetime.fromtimestamp(
            int(item.xpath('.//small[@class="time"]/a/span/@data-time').extract_first())
            ).strftime('%Y-%m-%d %H:%M:%S')
        
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
        tweet['text'] = ' '.join(
            item.xpath('.//div[@class="js-tweet-text-container"]/p//text()').extract()
            ).replace(' # ', '#').replace(' @ ', '@')

        if ''==tweet['text']:
            continue

        # get user id
        tweet['user_id'] = item.xpath('.//@data-user-id').extract()[0]
        tweet['usernameTweet'] = item.xpath('.//@data-screen-name').extract_first()

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
        images = item.xpath('.//div[@class="AdaptiveMedia-photoContainer js-adaptive-photo "]/@data-image-url').extract()
        if images:
            tweet['has_image'] = True
            tweet['images'] = images

        # videos
        videos = item.xpath('.//video/@src').extract()
        if videos:
            tweet['has_video'] = True
            tweet['videos'] = videos

        #summary card
        sumfullcard = item.xpath('.//div[@data-card-name="summary_large_image"]/@data-full-card-iframe-url').extract()
        sumurl = item.xpath('.//div[@data-card-name="summary_large_image"]/@data-card-url').extract()
        if sumurl:
            tweet['has_summary'] = True
            tweet['sumfullcard'] = sumfullcard
            tweet['sumurl'] = sumurl
        
        if True:
            user = User()
            user['ID'] = tweet['user_id']
            user['name'] = item.xpath('.//@data-name').extract_first()
            user['screen_name'] = tweet['usernameTweet']
            user['avatar'] = item.xpath('.//img[@class="avatar js-action-profile-avatar"]/@src').extract_first()


        yield item