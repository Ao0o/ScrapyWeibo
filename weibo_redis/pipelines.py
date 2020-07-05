# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

# class WeiboRedisPipeline:
#     def process_item(self, item, spider):
#         return item
#
#


import pymongo
from weibo_redis.items import InformationItem, UserItem, TweetItem, RelationshipItem, CommentItem


class WeiboRedisPipeline:
    UserItemdb = 'User'
    Tweetdb = 'Tweets'
    Relationshipdb = 'Relationship'
    CommentItemdb = 'Comment'


    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):

        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE', 'items')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):

        if isinstance(item, UserItem):
            try:
                self.db[self.UserItemdb].insert_one(dict(item))
            except Exception:
                pass
        elif isinstance(item, TweetItem):
            try:
                self.db[self.Tweetdb].insert_one(dict(item))
            except Exception:
                pass
        elif isinstance(item, RelationshipItem):
            try:
                self.db[self.Relationshipdb].insert_one(dict(item))
            except Exception as e:
                self.logger.error(e)
                pass
        elif isinstance(item, CommentItem):
            try:
                self.db[self.CommentItemdb].insert_one(dict(item))
            except Exception as e:
                self.logger.error(e)
                pass

        return item
