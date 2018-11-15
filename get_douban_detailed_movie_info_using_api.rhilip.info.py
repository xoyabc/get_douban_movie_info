#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re  
import sys  
import urllib  
import requests
import random
import json
import time
from urllib import unquote
from decimal import Decimal
from requests.packages.urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
reload(sys)
sys.setdefaultencoding("utf-8")

s = requests.Session()
retries = Retry(total=5,
                backoff_factor=0.5,
                status_forcelist=[ 500, 502, 503, 504 ])
s.mount('http://', HTTPAdapter(max_retries=retries))
s.mount('https://', HTTPAdapter(max_retries=retries))

headers = {
         'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.81 Safari/537.36',
         'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
         'Accept-Encoding': 'gzip, deflate, sdch',
         'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4,en-GB;q=0.2,zh-TW;q=0.2',
    }

def get_data(subject):
    api_url = 'https://api.rhilip.info/tool/movieinfo/gen?url=https://movie.douban.com/subject/' 
    api_request_url = '{0}{1}' .format(api_url, subject)
    r = s.get(api_request_url, headers=headers)
    data = r.text
    json_data = json.loads(data)
    movie_info['error'] = json_data.get('error', 'not_found_in_douban')
    movie_info['name'] = json_data.get('chinese_title', 'N/A')
    movie_info['year'] = json_data.get('year', 'N/A')
    try:
        movie_info['region'] = json_data.get('region', ['N/A'])[0]
    except IndexError:
        movie_info['region'] = "N/A"
    try:
        movie_info['language'] = json_data.get('language', ['N/A'])[0]
    except IndexError:
        movie_info['language'] = "N/A"
    movie_info['douban_rating_average'] = json_data['douban_rating_average']
    movie_info['douban_votes'] = json_data['douban_votes']
    try:
        movie_info['genre'] = "" .join(json_data.get('genre', ['N/A'])).split()[0]
    except IndexError:
        movie_info['genre'] = "N/A"
    try:
        movie_info['cast'] = "" .join(json_data.get('cast', ['N/A'])).split()[0]
    except IndexError:
        movie_info['cast'] = "N/A"
    try:
        movie_info['director'] = "" .join(json_data.get('director', ['N/A'])).split()[0]
    except IndexError:
        movie_info['director'] = "N/A"
    try:
        imdb_rating = json_data['imdb_rating']
        movie_info['imdb_score'] = imdb_rating.split('/')[0]
        movie_info['imdb_rating_num'] = imdb_rating.split()[2]
    except KeyError:
        movie_info['imdb_score'] = "N/A"
        movie_info['imdb_rating_num'] = "N/A"
    # print year, director_without_eng_name, cast, genre, imdb_score, imdb_rating_num
    return movie_info

if __name__ == '__main__':
    movie_info = {}
    with open('movie.list','rU') as f:
        for subject_id in f:
            subject_id = subject_id.strip()
            try:
                data = get_data(subject_id)
                #print "{0} {1}" .format(subject_id, data['error'])
                if data['error'] is not None:
                    print "{0} {1}" .format(subject_id,data['error'])
                else:
                    print "{0} {1} {2} {3} {4}" .format(subject_id, data['name'], 
                                                data['year'], data['region'], data['language'])
                                                #data['genre'], data['cast'], data['director'])
            except Exception:
                print "{0} not_found_in_douban" .format(subject_id)
            sleeptime = random.uniform(2, 5)
            sleeptime = Decimal(sleeptime).quantize(Decimal('0.00'))
            time.sleep(sleeptime)
            #print "{0} {1}" .format(movie_name,movie_year)
