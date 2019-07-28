#!/usr/bin/env python
# -*- coding:utf-8 -*-
import re  
import sys  
import urllib  
import requests
import random
from bs4 import BeautifulSoup  
from urllib import unquote
from decimal import Decimal
import time
reload(sys)
sys.setdefaultencoding("utf-8")


def serach_movie(movie_name,movie_year):
    # header content
    douban_headers = {
         'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.81 Safari/537.36',
         'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
         'Accept-Encoding': 'gzip, deflate, sdch',
         'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4,en-GB;q=0.2,zh-TW;q=0.2',
         'Connection': 'keep-alive',
         'DNT': '1',
         'HOST': 'www.douban.com',
         'Cookie': 'iv5LdR0AXBc'
    }
    
    #url_link = 'https://www.douban.com/search?cat=1002&q=B.A.Pass.2013'
    url_link = 'https://www.douban.com/search?cat=1002&q={0} {1}' .format(movie_name,movie_year)
    r = requests.get(url_link, headers=douban_headers)
    douban_headers['Cookie'] = r.cookies
    soup = BeautifulSoup(r.text.encode('utf-8'), 'lxml')
    all_subuject_result = soup.find_all(attrs={'class' : 'result'})[0:1]
    data = {}
    if all_subuject_result:
        for result in all_subuject_result:
            #print result
            title = result.find_all(attrs={'class' : 'title'})[0]
            rating_info = result.find_all(attrs={'class' : 'rating-info'})[0]
            # movie title info
            chn_title = title.h3.a.text.strip()
            link = title.h3.a['href']
            link_decode = unquote(link)
            link = re.match(r'^.*url=(.*?)&query=.*$', link_decode).group(1)
            subject_id = re.match(r'^.*url=(https://movie.douban.com/subject/)?([0-9]+)/&query=.*$', link_decode).group(2)
            year = title.find_all(attrs={'class' : 'subject-cast'})[0].text.split('原名:')[1].split('/')[-1].replace(' ','')
            # movie rating info
            rating_total_nums = rating_info.find_all('span', attrs={"class": None})[0].text
            rating_total_nums = re.sub(r'(\(|\))', '', rating_total_nums)
            if rating_total_nums and '暂无评分' not in rating_total_nums and '尚未' not in rating_total_nums:
                rating_score = rating_info.find_all('span', attrs={"class": "rating_nums"})[0].text
            else:
                rating_score = rating_total_nums
            #print "o-year:{0} m-year:{1}" .format(year,movie_year)
            data['name'] = movie_name
            data['chn_title'] = chn_title
            data['link'] = link
            data['subject_id'] = subject_id
            data['year'] = year
            data['rating_score'] = rating_score
            data['rating_total_nums'] = rating_total_nums
            #print movie_name,original_name_format,movie_name_new
    else:
        data['name'] = movie_name
        data['chn_title'] = 'Not found in douban'
        data['link'] = 'N/A'
        data['subject_id'] = 'N/A'
        data['year'] = 'N/A'
        data['rating_score'] = 'N/A'
        data['rating_total_nums'] = 'N/A'
    #print data
    return data

with open('movie.name','rU') as f:
    for line in f:
        movie_info = line.strip()
        p = re.compile(r'^(.*)(\.|\s)([0-9]{4})\.?.*$')
        match_obj = p.match(movie_info)
        if match_obj is not None:
            movie_name = match_obj.group(1)
            movie_year = match_obj.group(2)
            #print "{0} {1}" .format(match_obj.group(1),match_obj.group(2))
        else:
            movie_name = re.match(r'^(.*)([0-9]{4})?\.?(720p|1080p)?.*$', movie_info).group(1)
            if re.search("\.", movie_name):
                movie_name = re.sub(r'([0-9]{4})', '' ,movie_name)
            movie_year = ''
        data = serach_movie(movie_name,movie_year)
        #print "{0};{1};{2};{3};{4}" .format(data['name'], data['chn_title'], data['year'],
        print "{:<10}[{}][{}][{}][{}][{}]" .format(data['subject_id'], data['name'], data['chn_title'], 
                                            data['year'],
                                            data['rating_score'], data['rating_total_nums'])
        sleeptime = random.uniform(0, 5)
        sleeptime = Decimal(sleeptime).quantize(Decimal('0.00'))
        time.sleep(sleeptime)
        #print "{0} {1}" .format(movie_name,movie_year)
