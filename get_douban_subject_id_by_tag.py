#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests
import sys
import re
import random
import time
from bs4 import BeautifulSoup
# solve SNIMissingWarning, InsecurePlatformWarning on urllib3 when using < Python 2.7.9
import urllib3
urllib3.disable_warnings()

url = "https://movie.douban.com/j/new_search_subjects"
subject_list = []
#num = 0


douban_headers = {
     'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.81 Safari/537.36',
     'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
     'Accept-Encoding': 'gzip, deflate, sdch',
     'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4,en-GB;q=0.2,zh-TW;q=0.2',
     'Connection': 'keep-alive',
     'DNT': '1',
     'HOST': 'movie.douban.com',
     'Cookie': 'iv5LdR0AXBc'
}


def write_to_file(file, *info_list):
    with open(file, 'w')  as f:
        f.writelines(str(line) + "\n" for line in info_list)


def get_subject(start, end):
    while start <= end:
        print (start)
        payload = {
        'sort': 'T',
        'range': '0,10',
        'tags': '1989',
        'start': start,
        }
        resp = requests.get(url, params=payload, headers=douban_headers, verify=False)
        json_data= resp.json()['data']
        
        for item in json_data:
            subject_list.append(item['id'])
            print (item['id'])
        time.sleep(1 + random.randint(5, 10))
        start += 20
    return subject_list

if __name__ == '__main__':
    subject_list = get_subject(0, 20)
    write_to_file('douban_subjects', *subject_list)
