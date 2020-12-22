#!/usr/bin/env python
# -*- coding:utf-8 -*-
import re 
import sys
import urllib
import requests
import random
import csv
import codecs
from bs4 import BeautifulSoup  
from urllib import unquote
from decimal import Decimal
import time
reload(sys)
sys.setdefaultencoding("utf-8")
import urllib3
urllib3.disable_warnings()


# write to csv file
def write_to_csv(filename, head_line, *info_list):
    with open(filename, 'w') as f:
        f.write(codecs.BOM_UTF8)
        writer = csv.writer(f)
        writer.writerow(head_line.split('\t'))
        for row in info_list:
            row_list = row.split('\t')
            writer.writerow(row_list)


def search_movie(movie_name,movie_year):
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
    #print r.status_code
    douban_headers['Cookie'] = r.cookies
    soup = BeautifulSoup(r.text.encode('utf-8'), 'lxml')
    if movie_year == '':
        all_subuject_result = soup.find_all(attrs={'class' : 'result'})[0:1]
    else:
        all_subuject_result = soup.find_all(attrs={'class' : 'result'})[0:3]
    data = {}
    data['name'] = movie_name
    data['chn_title'] = 'Not found in douban'
    data['link'] = 'N/A'
    data['subject_id'] = 'N/A'
    data['year'] = 'N/A'
    data['rating_score'] = 'N/A'
    data['rating_total_nums'] = 'N/A'
    data['director'] = 'N/A'
    data['actor'] = 'N/A'
    if all_subuject_result:
        for result in all_subuject_result:
            #print result
            title = result.find_all(attrs={'class' : 'title'})[0]
            # movie title info
            chn_title = title.h3.a.text.strip()
            # movie year
            year = title.find_all(attrs={'class' : 'subject-cast'})[0].text.split('原名:')[1].split('/')[-1].replace(' ','')
            #print ("movie_year:{}" .format(movie_year))
            #print ("year:{}" .format(year))
            year_minus = abs(int(movie_year)-int(year)) if movie_year != '' else 3
            #if year_minus <= 1 and movie_name == chn_title:
            if year_minus <= 2 or movie_year == '':
                # movie rating, link, subject_id
                rating_info = result.find_all(attrs={'class' : 'rating-info'})[0]
                link = title.h3.a['href']
                link_decode = unquote(link)
                link = re.match(r'^.*url=(.*?)&query=.*$', link_decode).group(1)
                subject_id = re.match(r'^.*url=(https://movie.douban.com/subject/)?([0-9]+)/&query=.*$', link_decode).group(2)
                # movie rating info
                rating_total_nums = rating_info.find_all('span', attrs={"class": None})[0].text
                rating_total_nums = re.sub(r'(\(|\))', '', rating_total_nums).replace('人评价','')
                if rating_total_nums and '暂无评分' not in rating_total_nums and '尚未' not in rating_total_nums:
                    rating_score = rating_info.find_all('span', attrs={"class": "rating_nums"})[0].text
                else:
                    rating_score = rating_total_nums
                #print "o-year:{0} m-year:{1}" .format(year,movie_year)
                # director, actor
                subject_cast_list = title.find_all(attrs={'class' : 'subject-cast'})[0].text.split('原名:')[1].split('/')
                director = subject_cast_list[1].replace(' ','')
                actor = subject_cast_list[-2].replace(' ','')
                data['name'] = movie_name
                data['chn_title'] = chn_title
                data['link'] = link
                data['subject_id'] = subject_id
                data['year'] = year
                data['rating_score'] = rating_score
                data['rating_total_nums'] = rating_total_nums
                data['director'] = director
                data['actor'] = actor
                break
            else:
                continue
    return data


def main():
    movie_info_list = []
    with open('movie.name','rU') as f:
        for line in f:
            movie_info = line.strip()
            p = re.compile(r'^(.*?)[\.| |\s]?([0-9]{4})\.?.*$')
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
            data = search_movie(movie_name,movie_year)
            #print "{0};{1};{2};{3};{4}" .format(data['name'], data['chn_title'], data['year'],
            print "{:<10}[{}][{}][{}][{}][{}][{}][{}]" .format(data['subject_id'], data['name'], data['chn_title'], 
                                                data['year'],
                                                data['rating_score'], data['rating_total_nums'],
                                                data['director'], data['actor'])
            info_line = "{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}".format(data['subject_id'], data['name'],
                                                data['chn_title'], data['year'],
                                                data['rating_score'], data['rating_total_nums'],
                                                data['director'], data['actor'])
            movie_info_list.append(info_line)
            sleeptime = random.uniform(0, 5)
            sleeptime = Decimal(sleeptime).quantize(Decimal('0.00'))
            time.sleep(sleeptime)
            #print "{0} {1}" .format(movie_name,movie_year)
        return movie_info_list


if __name__ == '__main__':
    # write to movie.csv
    f_csv = 'movie_info.csv'
    head_instruction = "dbid\toriginal_name\tdb_chn_title\tyear\trating_score\trating_num\tdirector\tactor"
    movie_info_list = main()
    write_to_csv(f_csv, head_instruction, *movie_info_list)
