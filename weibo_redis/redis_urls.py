import datetime
import redis
import sys


def add_redis_url(spider_name, url):
    r = redis.Redis(host = '127.0.0.1', port = 6379, decode_responses=True)
    for key in r.scan_iter(f"{spider_name}*"):
        r.delete(key)
    print(f'Add urls to {spider_name}:start_urls')
    r.lpush(f'{spider_name}:start_urls', url)
    # print('Added:', url)
