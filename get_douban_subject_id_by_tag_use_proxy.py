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


ua_list = [
"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.109 Safari/537.36",
"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.75 Safari/537.36",
"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36",
"Mozilla / 5.0(Windows NT 6.1;WOW64) AppleWebKit / 537.36(KHTML, likeGecko) Chrome / 45.0.2454.101Safari / 537.36"
]


cookie_list = [
'KREXrOwvBwk',
'IzkGAslma08',
'I9kGAslma08',
'I9k3Aslma08',
]

proxies = {
"https": "https://110.90.214.226:12101",
"https": "https://110.90.215.9:12101",
}


# write the list to result file
def write_to_file(file, *info_list):
    with open(file, 'w')  as f:
        f.writelines(str(line) + "\n" for line in info_list)


# get douban subject
def get_subject(tag, start, end):
    while start <= end:
        user_agent = random.choice(ua_list)
        cookie = random.choice(cookie_list)
        #print (user_agent,cookie)
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
        print (start)
        payload = {
        'sort': 'T',
        'range': '0,10',
        'tags': tag,
        'start': start,
        }
        try:
            resp = requests.get(url, params=payload, headers=douban_headers, verify=False, proxies=proxies)
            json_data= resp.json()['data']
            print (resp.status_code)
            print (resp.json())
            # retry if response data is 'data'
            if not isinstance (json_data, list):
                resp = requests.get(url, params=payload, headers=douban_headers, verify=False, proxies=proxies)
                json_data= resp.json()['data']
            print (resp.status_code)
            print (resp.json())
            for item in json_data:
                subject_list.append(item['id'])
                print (item['id'])
        except Exception as e:
            print(e)
        time.sleep(1 + random.randint(39, 65))
        start += 20
    return subject_list


if __name__ == '__main__':
    subject_list = get_subject('2019', 2580, 3980)
    #subject_list = get_subject('2019', 2280, 3980)
    write_to_file('douban_subjects', *subject_list)
