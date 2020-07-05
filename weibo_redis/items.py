# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

from scrapy import Field
from scrapy import Item

class UserItem(scrapy.Item):
    """ User Information"""
    _id = Field()  # user ID
    nick_name = Field()
    gender = Field()
    province = Field()
    city = Field()

    brief_introduction = Field()
    birthday = Field()
    age = Field()
    tweets_num = Field()
    follows_num = Field()
    fans_num = Field()
    sex_orientation = Field()
    sentiment = Field()  # sentiment status
    vip_level = Field()
    authentication = Field()
    person_url = Field()
    labels = Field()
    crawl_time = Field()   # crawl timestamp



class InformationItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    _id = Field()  # user_id
    nickName = Field()
    gender = Field()
    province = Field()
    city = Field()
    birthday = Field()
    brief_introduction = Field()  #
    age = Field()
    num_Tweets = Field()
    num_Follows = Field()
    num_Fans = Field()
    person_url = Field()         #url link
    num_comments = Field()  #num of comments
    num_attitudes = Field()  #num of attitudes
    authentication = Field()  # authentication
    vip_level = Field()  # vip level
    sentiment = Field()  #
    sex_orientation = Field()  #
    labels = Field()
    crawl_time = Field()   # crawl timestamp


class TweetItem(Item):
    """Tweet information """
    _id = Field()  # tweet id
    weibo_url = Field()  # tweet URL
    created_at = Field()  # tweet publish time
    like_num = Field()  # num of likes
    repost_num = Field()  # num of repost
    comment_num = Field()  # num of comment
    content = Field()  # tweet content
    user_id = Field()  # owner id of tweet
    tool = Field()  # publish from which tool
    image_url = Field()  # picture url
    video_url = Field()  # vedio url
    origin_weibo = Field()  # origin tweet，only repost tweet own
    location_map_info = Field()  # location
    crawl_time = Field()  # crawl timestamp

class RelationshipItem(Item):
    """ Relationship """
    _id = Field()
    fan_id = Field()  # fan's id
    followed_id = Field()  # follower's id
    crawl_time = Field()  # # crawl timestamp


class CommentItem(Item):
    """
    tweet comment
    """
    _id = Field()
    comment_user_id = Field()  # 评论用户的id
    content = Field()  # 评论的内容
    weibo_id = Field()  # 评论的微博的url
    created_at = Field()  # 评论发表时间
    like_num = Field()  # 点赞数
    crawl_time = Field()   # crawl timestamp
