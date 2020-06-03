# -*- coding: utf-8 -*-
import re

import scrapy
from scrapy.selector import Selector
import datetime
import time
import requests
from weibo_redis.items import InformationItem, TweetsItem, FansItem, URLItem
from scrapy_redis.spiders import RedisSpider
from scrapy.http import Request
# from scrapy.http.cookies import CookieJar
from lxml import etree


class Spider(RedisSpider):
    name = "informationSpider"
    host = "https://weibo.cn"
    redis_key = "informationSpider:start_urls"

    start_urls = [
        # 2388955087,  # 首都网警
        # 2185009762
        2014433131
    ]
    comment_url = []
    tweets_url = []
    attitude_url = []

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url=u"https://weibo.cn/u/%s" % url, meta={"ID": url}, callback=self.parse)
            yield Request(url=u"https://weibo.cn/u/%s?page=1" % url, meta={"ID": url}, callback=self.tweets_parse)

    def parse(self, response):

        information_items = InformationItem()
        selector = Selector(response)

        try:
            text = selector.xpath('body/div[@class="u"]/div[@class="tip2"]').get()

            if text:
                num_tweets = re.findall(u'\u5fae\u535a\[(\d+)\]', text)
                num_follows = re.findall(u'\u5173\u6ce8\[(\d+)\]', text)
                num_fans = re.findall(u'\u7c89\u4e1d\[(\d+)\]', text)

                if num_tweets:
                    information_items["Num_Tweets"] = int(num_tweets[0])

                if num_follows:
                    information_items["Num_Follows"] = int(num_follows[0])

                if num_fans:
                    information_items["Num_Fans"] = int(num_fans[0])

                information_items["_id"] = response.meta["ID"]
                url_detail_info = "https://weibo.cn/%s/info" % response.meta["ID"]
        except:
            print(time.asctime(time.localtime(time.time())), "parse except")
            pass

        # get cookies from scrapy response
        Cookie2 = str(response.request.headers.getlist('Cookie'))
        cookie = {}
        # change string type to dict
        for line in Cookie2.split(';'):
            key, value = line.split('=', 1)
            cookie[key] = value

        try:
            r = requests.get(url_detail_info, cookies=cookie)  # cookie's type need dict

            if r.status_code == 200:
                selector = etree.HTML(r.content)
                text1 = ";".join(selector.xpath('body/div[@class="c"]/text()'))
                nickname = re.findall(u'\u6635\u79f0[:|\uff1a](.*?);', text1)
                gender = re.findall(u'\u6027\u522b[:|\uff1a](.*?);', text1)
                place = re.findall(u'\u5730\u533a[:|\uff1a](.*?);', text1)  # place（include province and city）
                birthday = re.findall(u'\u751f\u65e5[:|\uff1a](.*?);', text1)  #
                url = re.findall(u'\u4e92\u8054\u7f51[:|\uff1a](.*?);', text1)  #

                if nickname:
                    information_items["NickName"] = nickname[0]

                if gender:
                    information_items["Gender"] = gender[0]

                if place:
                    place = place[0].split(" ")
                    information_items["Province"] = place[0]
                    if len(place) > 1:
                        information_items["City"] = place[1]
                if birthday:
                    try:
                        birthday = datetime.datetime.strptime(birthday[0], "%Y-%m-%d")
                        today = datetime.date.today().year
                        age = today - birthday.year
                        information_items["Birthday"] = birthday - datetime.timedelta(hours=8)
                        information_items["Age"] = age
                    except:
                        pass

                if url:
                    information_items["URL"] = url[0]

                yield information_items
        except:
            print(time.asctime(time.localtime(time.time())), "detail except")
            pass

    def tweets_parse(self, response):
        selector = Selector(response)
        tweet_item = TweetsItem()

        tweets = selector.xpath('body/div[@class="c" and @id]')

        for tweet in tweets:
            try:
                id_comp = tweet.xpath('@id').get()
                id = re.sub('M_', '', id_comp)  # Get comment ID
                yield Request(url=u"https://weibo.cn/attitude/%s?&page=1" % id, meta={"Com_ID": id},
                              callback=self.attitude_parse)  # Crawl attitude page

                links = tweet.xpath('div/a/@href').getall()
                for link in links:
                    if 'comment' in link:
                        tmp_link = link
                        comment_link = re.sub('#cmtfrm', '&page=1', tmp_link)
                        self.comment_url.append(comment_link)

                for url in self.comment_url:
                    yield Request(url=url, meta={"item": tweet_item},
                                  callback=self.comments_parse)  # crawl comment page

                url_next = selector.xpath(
                    u'body//div[@class="pa" and @id="pagelist"]/form/div/a[text()="\u4e0b\u9875"]/@href'
                    # get next page url
                ).get()
                if url_next:
                    yield Request(url=self.host + url_next, callback=self.tweets_parse)
            except:
                print(time.asctime(time.localtime(time.time())), "tweet except")
                pass

    def comments_parse(self, response):
        selector = Selector(response)

        comments_ids = selector.xpath('//div[@class="c" and @id]/a/@href').getall()
        try:

            for comment_id in comments_ids:
                elem = re.findall('/u/(\d+)', comment_id)
                if elem:
                    ID = int(elem[0])
                    yield Request(url="https://weibo.cn/u/%s" % ID, meta={"ID": ID}, callback=self.parse)

            url_next = selector.xpath(
                u'body//div[@class="pa" and @id="pagelist"]/form/div/a[text()="\u4e0b\u9875"]/@href'
                # get next page url
            ).get()

            if url_next:
                yield Request(url=self.host + url_next, callback=self.comments_parse)
            else:
                print("comment finished")

        except:
            print("comments_parse except")
            pass

    def attitude_parse(self, response):
        selector = Selector(response)

        comments_ids = selector.xpath('//div[@class="c"]/a/@href').getall()

        for comment_id in comments_ids:
            elem = re.findall('/u/(\d+)', comment_id)
            if elem:
                ID = int(elem[0])
                yield Request(url="https://weibo.cn/u/%s" % ID, meta={"ID": ID}, callback=self.parse)

        url_next = selector.xpath(
            u'body//div[@class="pa" and @id="pagelist"]/form/div/a[text()="\u4e0b\u9875"]/@href'  # get next page url
        ).get()

        if url_next:
            yield Request(url=self.host + url_next, callback=self.attitude_parse)
