# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

from scrapy import Field


class InformationItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    _id = Field()  # user_id
    NickName = Field()
    Gender = Field()
    Province = Field()
    City = Field()
    Birthday = Field()
    Age = Field()
    Num_Tweets = Field()
    Num_Follows = Field()
    Num_Fans = Field()
    URL = Field() #url link


class TweetsItem(scrapy.Item):
    """ tweet information """
    _id = Field()  # tweet ID
    ID = Field()  # user ID
    Like = Field() # num of attitude
    Content = Field()  # content

    PubTime = Field()  # published time


class FansItem(scrapy.Item):
    _id = Field()
    fans = Field()

class URLItem(scrapy.Item):
    crawled_url = Field()
