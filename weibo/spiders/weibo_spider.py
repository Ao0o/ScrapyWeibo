# encoding=utf-8

import re

import scrapy
from scrapy.selector import Selector
import datetime
from weibo.items import InformationItem, TweetsItem, FansItem


class Spider(scrapy.Spider):
    name = "weibo"
    host = "https://weibo.cn"

    start_urls = [
        # 2388955087  # 首都网警
        5882024506, 5725875852
    ]

    scrawl_ID = set(start_urls)  # 记录待爬的微博ID
    finish_ID = set()  # 记录已经爬取的微博ID

    def start_requests(self):

        while self.scrawl_ID.__len__():
            ID = self.scrawl_ID.pop()
            self.finish_ID.add(ID)
            ID = str(ID)


            fans_items = FansItem()
            fans_items["_id"] = ID

            url_information = "https://weibo.cn/u/%s" % ID

            url_tweets = "https://weibo.cn/%s/profile?filter=1&page=1" % ID

            url_fans = "https://weibo.cn/%s/fans" % ID
            yield scrapy.http.Request(url=url_fans, meta={"item": fans_items}, callback=self.fans_parse)  # 爬取粉丝

            yield scrapy.http.Request(url=url_information, meta={"ID": ID}, callback=self.parse)  # 爬取个人信息

            yield scrapy.http.Request(url=url_tweets, meta={"ID": ID}, callback=self.tweets_parse)  # 爬取微博

    def parse(self, response):

        information_items = InformationItem()
        selector = Selector(response)
        text = selector.xpath('body/div[@class="u"]/div[@class="tip2"]').get()

        if text:
            num_tweets = re.findall(u'\u5fae\u535a\[(\d+)\]', text)
            num_follows = re.findall(u'\u5173\u6ce8\[(\d+)\]', text)  # 关注数
            num_fans = re.findall(u'\u7c89\u4e1d\[(\d+)\]', text)  # 粉丝数

            if num_tweets:
                information_items["Num_Tweets"] = int(num_tweets[0])

            if num_follows:
                information_items["Num_Follows"] = int(num_follows[0])

            if num_fans:
                information_items["Num_Fans"] = int(num_fans[0])

            information_items["_id"] = response.meta["ID"]
            url_detail_info = "https://weibo.cn/%s/info" % response.meta["ID"]
            yield scrapy.http.Request(url=url_detail_info, meta={"item": information_items},
                                 callback=self.detail_info_parse)  # 爬取个人详细信息

    def detail_info_parse(self, response):
        information_items = response.meta['item']
        selector = Selector(response)
        text1 = ";".join(selector.xpath('body/div[@class="c"]/text()').getall())
        nickname = re.findall(u'\u6635\u79f0[:|\uff1a](.*?);', text1)
        gender = re.findall(u'\u6027\u522b[:|\uff1a](.*?);', text1)
        place = re.findall(u'\u5730\u533a[:|\uff1a](.*?);', text1)  # 地区（包括省份和城市）
        birthday = re.findall(u'\u751f\u65e5[:|\uff1a](.*?);', text1)  # 生日
        url = re.findall(u'\u4e92\u8054\u7f51[:|\uff1a](.*?);', text1)  # 首页链接
        # marriage = re.findall(u'\u611f\u60c5\u72b6\u51b5[:|\uff1a](.*?);', text1)  # 婚姻状况

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
            except Exception:
                pass
        if url:
            information_items["URL"] = url[0]

        yield information_items

    def tweets_parse(self, response):
        selector = Selector(response)
        tweets = selector.xpath('body/div[@class="c" and @id]')
        for tweet in tweets:
            tweet_items = TweetsItem()
            id = tweet.xpath('@id').get()

            content = tweet.xpath('div/span[@class="ctt"]/text()').getall()
            pass

            # like = re.findall(u'\u8d5e\[(\d+)\]', tweet.getall())
            # comment = re.findall(u'\u8bc4\u8bba\[(\d+)\]', tweet.getall())
            # others = tweet.xpath('div/span[@class="ct"]/text()').get()  # 求时间和使用工具（手机或平台）

            # tweet_items["ID"] = response.meta["ID"]
            # tweet_items["_id"] = response.meta["ID"] + "-" + id
            #
            # if content:
            #     tweet_items["Content"] = content[0]

    def fans_parse(self, response):
        items = response.meta["item"]
        selector = Selector(response)
        text2 = selector.xpath(
            u'body//table/tr/td/a[text()="\u5173\u6ce8\u4ed6" or text()="\u5173\u6ce8\u5979"]/@href'  # 关注他or关注她
        ).getall()

        for elem in text2:
            elem = re.findall('uid=(\d+)', elem)
            if elem:
                ID = int(elem[0])
                if ID not in self.finish_ID:
                    self.scrawl_ID.add(ID)

        url_next = selector.xpath(
            u'body//div[@class="pa" and @id="pagelist"]/form/div/a[text()="\u4e0b\u9875"]/@href'  # 下一页
        ).getall()

        while self.scrawl_ID.__len__():
            ID = self.scrawl_ID.pop()
            self.finish_ID.add(ID)
            ID = str(ID)
            url_information = "https://weibo.cn/u/%s" % ID

            yield scrapy.http.Request(url=url_information, meta={"ID": ID}, callback=self.parse)

        if url_next:
                yield scrapy.http.Request(url=self.host + url_next[0], meta={"item": items},
                                     callback=self.fans_parse)
        else:
            yield items


