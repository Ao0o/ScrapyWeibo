缺少setting.py文件，自行设置，添加自己的cookie。

参考：

```python
# -*- coding: utf-8 -*-

# Scrapy settings for weibo project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'weibo'

SPIDER_MODULES = ['weibo.spiders']
NEWSPIDER_MODULE = 'weibo.spiders'

ROBOTSTXT_OBEY = False

DOWNLOAD_DELAY = 1

COOKIES_ENABLED = False

DEFAULT_REQUEST_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36',
    'Cookie':'Your Cookies',

}
ITEM_PIPELINES = {
   'weibo.pipelines.WeiboPipeline': 300,
}
MONGO_URI = 'mongodb://127.0.0.1:27017'
MONGO_DATABASE = 'weibo'
AUTOTHROTTLE_START_DELAY = 0.5


```

