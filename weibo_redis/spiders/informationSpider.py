# -*- coding: utf-8 -*-

"""
A simple demo
full scrapy crawl  in other spyder
"""
import re

import scrapy
from scrapy.selector import Selector
import datetime
import time
import requests
from weibo_redis.items import InformationItem, UserItem, TweetItem, RelationshipItem, CommentItem
from scrapy_redis.spiders import RedisSpider
from scrapy.http import Request
# from scrapy.http.cookies import CookieJar
from lxml import etree
from weibo_redis.redis_urls import add_redis_url
from weibo_redis.spiders.utils import time_fix, extract_weibo_content, extract_comment_content



class Spider(RedisSpider):
    name = "informationSpider"
    host = "https://weibo.cn"
    redis_key = "informationSpider:start_urls"
    base_url = "https://weibo.cn"

    start_urls = [
        # 2388955087,  # 首都网警
        # 2185009762
        2014433131
    ]
    # start_url = [f"https://weibo.cn/{user_id}/follow?page=180" for user_id in start_urls]
    comment_url = []
    tweets_url = []
    attitude_url = []

    def start_requests(self):
        for url in self.start_urls:
            # yield Request(url=u"https://weibo.cn/u/%s" % url, meta={"ID": url}, callback=self.parse)
            yield Request(url=u"https://weibo.cn/u/%s?page=1" % url, meta={"ID": url}, callback=self.tweets_parse)

    # def parse(self, response):
    #
    #     information_items = InformationItem()
    #     selector = Selector(response)
    #
    #     try:
    #         text = selector.xpath('body/div[@class="u"]/div[@class="tip2"]').get()
    #
    #         if text:
    #             num_tweets = re.findall(u'\u5fae\u535a\[(\d+)\]', text)
    #             num_follows = re.findall(u'\u5173\u6ce8\[(\d+)\]', text)
    #             num_fans = re.findall(u'\u7c89\u4e1d\[(\d+)\]', text)
    #
    #             if num_tweets:
    #                 information_items["num_Tweets"] = int(num_tweets[0])
    #
    #             if num_follows:
    #                 information_items["num_Follows"] = int(num_follows[0])
    #
    #             if num_fans:
    #                 information_items["num_Fans"] = int(num_fans[0])
    #
    #             information_items["_id"] = response.meta["ID"]
    #             url_detail_info = "https://weibo.cn/%s/info" % response.meta["ID"]
    #             # print(type(url_detail_info))
    #             # add_redis_url('user_spider', url_detail_info)
    #     except:
    #         print(time.asctime(time.localtime(time.time())), "parse except")
    #         pass
    #
    #     # get cookies from scrapy response
    #     Cookie2 = str(response.request.headers.getlist('Cookie'))
    #     header = response.request.headers.getlist('User-Agent')[-1]
    #     header = {'User-Agent': header}
    #
    #     cookie = {}
    #     # # change string type to dict
    #     for line in Cookie2.split(';'):
    #         key, value = line.split('=', 1)
    #         cookie[key] = value
    #
    #     try:
    #         r = requests.get(url_detail_info, cookies=cookie, headers=header)  # cookies's & headers's type need dict
    #
    #         if r.status_code == 200:
    #             selector = etree.HTML(r.content)
    #             text1 = ";".join(selector.xpath('body/div[@class="c"]/text()'))
    #             nickname = re.findall(u'\u6635\u79f0[:|\uff1a](.*?);', text1)
    #             gender = re.findall(u'\u6027\u522b[:|\uff1a](.*?);', text1)
    #             place = re.findall(u'\u5730\u533a[:|\uff1a](.*?);', text1)  # place（include province and city）
    #             birthday = re.findall(u'\u751f\u65e5[:|\uff1a](.*?);', text1)  #
    #             url = re.findall(u'\u4e92\u8054\u7f51[:|\uff1a](.*?);', text1)  #
    #             if nickname:
    #                 information_items["nickName"] = nickname[0]
    #
    #             if gender:
    #                 information_items["gender"] = gender[0]
    #
    #             if place:
    #                 place = place[0].split(" ")
    #                 information_items["province"] = place[0]
    #                 if len(place) > 1:
    #                     information_items["city"] = place[1]
    #             if birthday:
    #                 try:
    #                     birthday = datetime.datetime.strptime(birthday[0], "%Y-%m-%d")
    #                     today = datetime.date.today().year
    #                     age = today - birthday.year
    #                     information_items["birthday"] = birthday - datetime.timedelta(hours=8)
    #                     information_items["age"] = age
    #                 except:
    #                     pass
    #             if url:
    #                 information_items["person_url"] = url[0]
    #
    #             yield information_items
    #     except:
    #         print(time.asctime(time.localtime(time.time())), "detail except")
    #         pass

    def parse(self, response):
        user_item = UserItem()
        user_item['crawl_time'] = int(time.time())
        selector = Selector(response)
        user_item['_id'] = re.findall('(\d+)/info', response.url)[0]
        user_info_text = ";".join(selector.xpath('body/div[@class="c"]//text()').extract())
        nick_name = re.findall('昵称;?:?(.*?);', user_info_text)
        gender = re.findall('性别;?:?(.*?);', user_info_text)
        place = re.findall('地区;?:?(.*?);', user_info_text)
        brief_introduction = re.findall('简介;?:?(.*?);', user_info_text)
        birthday = re.findall('生日;?:?(.*?);', user_info_text)
        sex_orientation = re.findall('性取向;?:?(.*?);', user_info_text)
        sentiment = re.findall('感情状况;?:?(.*?);', user_info_text)
        vip_level = re.findall('会员等级;?:?(.*?);', user_info_text)
        authentication = re.findall('认证;?:?(.*?);', user_info_text)
        labels = re.findall('标签;?:?(.*?)更多>>', user_info_text)
        if nick_name and nick_name[0]:
            user_item["nick_name"] = nick_name[0].replace(u"\xa0", "")
        if gender and gender[0]:
            user_item["gender"] = gender[0].replace(u"\xa0", "")
        if place and place[0]:
            place = place[0].replace(u"\xa0", "").split(" ")
            user_item["province"] = place[0]
            if len(place) > 1:
                user_item["city"] = place[1]
        if brief_introduction and brief_introduction[0]:
            user_item["brief_introduction"] = brief_introduction[0].replace(u"\xa0", "")
        if birthday and birthday[0]:

            try:
                user_item['birthday'] = birthday[0]
                birthday = datetime.datetime.strptime(birthday[0], "%Y-%m-%d")
                today = datetime.date.today().year
                age = today - birthday.year
                user_item["age"] = age
            except:
                pass

        if sex_orientation and sex_orientation[0]:
            if sex_orientation[0].replace(u"\xa0", "") == gender[0]:
                user_item["sex_orientation"] = "同性恋"
            else:
                user_item["sex_orientation"] = "异性恋"
        if sentiment and sentiment[0]:
            user_item["sentiment"] = sentiment[0].replace(u"\xa0", "")
        if vip_level and vip_level[0]:
            user_item["vip_level"] = vip_level[0].replace(u"\xa0", "")
        if authentication and authentication[0]:
            user_item["authentication"] = authentication[0].replace(u"\xa0", "")
        if labels and labels[0]:
            user_item["labels"] = labels[0].replace(u"\xa0", ",").replace(';', '').strip(',')
        request_meta = response.meta
        request_meta['item'] = user_item
        yield Request(self.base_url + '/u/{}'.format(user_item['_id']),
                      callback=self.parse_further_information,
                      meta=request_meta, dont_filter=False, priority=1)
        yield Request(self.base_url + '/{}'.format(user_item['_id'] + '/follow?page=1'),
                      callback=self.fellow_parse,
                      meta=request_meta, dont_filter=False, priority=3)

    def parse_further_information(self, response):
        text = response.text
        user_item = response.meta['item']
        tweets_num = re.findall('微博\[(\d+)\]', text)
        if tweets_num:
            user_item['tweets_num'] = int(tweets_num[0])
        follows_num = re.findall('关注\[(\d+)\]', text)
        if follows_num:
            user_item['follows_num'] = int(follows_num[0])
        fans_num = re.findall('粉丝\[(\d+)\]', text)
        if fans_num:
            user_item['fans_num'] = int(fans_num[0])
        yield user_item

    def tweets_parse(self, response):
        selector = Selector(response)
        tweets = selector.xpath('body/div[@class="c" and @id]')

        # 这种写法当初始page不是1的时候会导致爬取不完全，程序鲁棒性不强

        # if response.url.endswith('page=1'):
        #     all_page = re.search(r'/>&nbsp;1/(\d+)页</div>', response.text)
        #     if all_page:
        #         all_page = all_page.group(1)
        #         all_page = int(all_page)
        #         for page_num in range(2, all_page + 1):
        #             page_url = response.url.replace('page=1', 'page={}'.format(page_num))
        #             yield Request(page_url, self.tweets_parse, dont_filter=True, meta=response.meta)
        tree_node = etree.HTML(response.body)
        tweet_nodes = tree_node.xpath('//div[@class="c" and @id]')

        try:
            for tweet_node in tweet_nodes:
                tweet_item = TweetItem()
                tweet_item['crawl_time'] = int(time.time())
                tweet_repost_url = tweet_node.xpath('.//a[contains(text(),"转发[")]/@href')[0]
                user_tweet_id = re.search(r'/repost/(.*?)\?uid=(\d+)', tweet_repost_url)
                tweet_item['weibo_url'] = 'https://weibo.cn/{}/{}'.format(user_tweet_id.group(2),
                                                                          user_tweet_id.group(1))
                tweet_item['user_id'] = user_tweet_id.group(2)
                tweet_item['_id'] = user_tweet_id.group(1)
                create_time_info_node = tweet_node.xpath('.//span[@class="ct"]')[-1]
                create_time_info = create_time_info_node.xpath('string(.)')
                if "来自" in create_time_info:
                    tweet_item['created_at'] = time_fix(create_time_info.split('来自')[0].strip())
                    tweet_item['tool'] = create_time_info.split('来自')[1].strip()
                else:
                    tweet_item['created_at'] = time_fix(create_time_info.strip())

                like_num = tweet_node.xpath('.//a[contains(text(),"赞[")]/text()')[-1]
                tweet_item['like_num'] = int(re.search('\d+', like_num).group())

                repost_num = tweet_node.xpath('.//a[contains(text(),"转发[")]/text()')[-1]
                tweet_item['repost_num'] = int(re.search('\d+', repost_num).group())

                comment_num = tweet_node.xpath(
                    './/a[contains(text(),"评论[") and not(contains(text(),"原文"))]/text()')[-1]
                tweet_item['comment_num'] = int(re.search('\d+', comment_num).group())

                images = tweet_node.xpath('.//img[@alt="图片"]/@src')
                if images:
                    tweet_item['image_url'] = images

                videos = tweet_node.xpath('.//a[contains(@href,"https://m.weibo.cn/s/video/show?object_id=")]/@href')
                if videos:
                    tweet_item['video_url'] = videos

                map_node = tweet_node.xpath('.//a[contains(text(),"显示地图")]')
                if map_node:
                    map_node = map_node[0]
                    map_node_url = map_node.xpath('./@href')[0]
                    map_info = re.search(r'xy=(.*?)&', map_node_url).group(1)
                    tweet_item['location_map_info'] = map_info

                repost_node = tweet_node.xpath('.//a[contains(text(),"原文评论[")]/@href')
                if repost_node:
                    tweet_item['origin_weibo'] = repost_node[0]

                all_content_link = tweet_node.xpath('.//a[text()="全文" and contains(@href,"ckAll=1")]')
                if all_content_link:
                    all_content_url = self.base_url + all_content_link[0].xpath('./@href')[0]
                    yield Request(all_content_url, callback=self.parse_all_content, meta={'item': tweet_item},
                                  priority=1)
                else:
                    tweet_html = etree.tostring(tweet_node, encoding='unicode')
                    tweet_item['content'] = extract_weibo_content(tweet_html)
                    yield tweet_item
            for tweet in tweets:
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
        except Exception as e:
            self.logger.error(e)

    def parse_all_content(self, response):
        tree_node = etree.HTML(response.body)
        tweet_item = response.meta['item']
        content_node = tree_node.xpath('//*[@id="M_"]/div[1]')[0]
        tweet_html = etree.tostring(content_node, encoding='unicode')
        tweet_item['content'] = extract_weibo_content(tweet_html)
        yield tweet_item

    #
    def comments_parse(self, response):
        # selector = Selector(response)

        # comments_ids = selector.xpath('//div[@class="c" and @id]/a/@href').getall()

        if response.url.endswith('page=1'):
            all_page = re.search(r'/>&nbsp;1/(\d+)页</div>', response.text)
            if all_page:
                all_page = all_page.group(1)
                all_page = int(all_page)
                all_page = all_page if all_page <= 50 else 50
                for page_num in range(2, all_page + 1):
                    page_url = response.url.replace('page=1', 'page={}'.format(page_num))
                    yield Request(page_url, self.comments_parse, dont_filter=False, meta=response.meta)
        try:
            tree_node = etree.HTML(response.body)
            comment_nodes = tree_node.xpath('//div[@class="c" and contains(@id,"C_")]')
            for comment_node in comment_nodes:
                comment_user_url = comment_node.xpath('.//a[contains(@href,"/u/")]/@href')
                if not comment_user_url:
                    continue
                comment_item = CommentItem()
                comment_item['crawl_time'] = int(time.time())
                comment_item['weibo_id'] = response.url.split('/')[-1].split('?')[0]
                comment_item['comment_user_id'] = re.search(r'/u/(\d+)', comment_user_url[0]).group(1)

                if comment_item['comment_user_id']:
                    ID = int(comment_item['comment_user_id'])
                    yield Request(url="https://weibo.cn/%s/info" % ID, meta={"ID": ID}, callback=self.parse)

                comment_item['content'] = extract_comment_content(etree.tostring(comment_node, encoding='unicode'))
                comment_item['_id'] = comment_node.xpath('./@id')[0]
                created_at_info = comment_node.xpath('.//span[@class="ct"]/text()')[0]
                like_num = comment_node.xpath('.//a[contains(text(),"赞[")]/text()')[-1]
                comment_item['like_num'] = int(re.search('\d+', like_num).group())
                comment_item['created_at'] = time_fix(created_at_info.split('\xa0')[0])
                yield comment_item

        # try:
        #
        #     for comment_id in comments_ids:
        #         elem = re.findall('/u/(\d+)', comment_id)
        #         if elem:
        #             ID = int(elem[0])
        #             yield Request(url="https://weibo.cn/%s/info" % ID, meta={"ID": ID}, callback=self.parse)
        #
        #     url_next = selector.xpath(
        #         u'body//div[@class="pa" and @id="pagelist"]/form/div/a[text()="\u4e0b\u9875"]/@href'
        #         # get next page url
        #     ).get()
        #
        #     if url_next:
        #         yield Request(url=self.host + url_next, callback=self.comments_parse)
        #     else:
        #         print("comment finished")


        except Exception as e:
            self.logger.error(e)
            print("comments_parse except")
            pass

    def attitude_parse(self, response):
        selector = Selector(response)

        comments_ids = selector.xpath('//div[@class="c"]/a/@href').getall()

        try:
            if comments_ids:
                for comment_id in comments_ids:
                    elem = re.findall('/u/(\d+)', comment_id)
                    if elem:
                        ID = int(elem[0])
                        yield Request(url="https://weibo.cn/%s/info" % ID, meta={"ID": ID}, callback=self.parse)

            url_next = selector.xpath(
                u'body//div[@class="pa" and @id="pagelist"]/form/div/a[text()="\u4e0b\u9875"]/@href'
                # get next page url
            ).get()

            if url_next:
                yield Request(url=self.host + url_next, callback=self.attitude_parse)
        except:
            print(time.asctime(time.localtime(time.time())), "attitude except")

    def fellow_parse(self, response):
        try:
            if response.url.endswith('page=1'):
                all_page = re.search(r'/>&nbsp;1/(\d+)页</div>', response.text)
                if all_page:
                    all_page = all_page.group(1)
                    all_page = int(all_page)
                    for page_num in range(2, all_page + 1):
                        page_url = response.url.replace('page=1', 'page={}'.format(page_num))
                        yield Request(page_url, self.fellow_parse, dont_filter=True, meta=response.meta, priority=4)
        except Exception as e:
            self.logger.error(e)
            print("fellow_parse1 except")
            pass
        try:
            selector = Selector(response)
            urls = selector.xpath('//a[text()="关注他" or text()="关注她" or text()="取消关注"]/@href').extract()
            uids = re.findall('uid=(\d+)', ";".join(urls), re.S)
            ID = re.findall('(\d+)/follow', response.url)[0]
            for uid in uids:
                relationships_item = RelationshipItem()
                relationships_item['crawl_time'] = int(time.time())
                relationships_item["fan_id"] = ID
                relationships_item["followed_id"] = uid
                relationships_item["_id"] = ID + '-' + uid
                yield relationships_item
        except Exception as e:
            self.logger.error(e)
            print("fellow_parse2 except")
            pass

        # url_next = selector.xpath(
        #     u'body//div[@class="pa" and @id="pagelist"]/form/div/a[text()="\u4e0b\u9875"]/@href'
        #     # get next page url
        # ).get()
        # if url_next:
        #     yield Request(url=self.host + url_next, callback=self.fellow_parse)
