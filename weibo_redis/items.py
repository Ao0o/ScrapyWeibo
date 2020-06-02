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
    _id = Field()  # 用户ID
    NickName = Field()  # 昵称
    Gender = Field()  # 性别
    Province = Field()  # 所在省
    City = Field()  # 所在城市
    Birthday = Field()  # 生日
    Age = Field() #年龄
    Num_Tweets = Field()  # 微博数
    Num_Follows = Field()  # 关注数
    Num_Fans = Field()  # 粉丝数
    URL = Field()  # 首页链接


class TweetsItem(scrapy.Item):
    """ 微博信息 """
    _id = Field()  # 用户ID-微博ID
    ID = Field()  # 用户ID
    Like = Field() #点赞数
    Content = Field()  # 微博内容

    PubTime = Field()  # 发表时间


class FansItem(scrapy.Item):
    _id = Field()
    fans = Field()

class URLItem(scrapy.Item):
    crawled_url = Field()
