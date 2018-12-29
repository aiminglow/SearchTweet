# -*- coding: utf-8 -*-


from scrapy import Item, Field


class Tweet(Item):
    ID = Field()
    url = Field()
    datetime = Field()
    text = Field()
    user_id = Field()

    nbr_retweet = Field()
    nbr_favorite = Field()
    nbr_reply = Field()

    is_reply = Field()
    is_retweet = Field()

    images = Field()

    # videos = Field()

    sumfullcard = Field()
    sumurl = Field()


class User(Item):
    ID = Field()
    name = Field()
    screen_name = Field()
    avatar = Field()
