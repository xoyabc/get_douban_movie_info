#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re  
import sys  
import urllib  
import requests
import random
import json
import csv
import codecs
from bs4 import BeautifulSoup  
from urllib import unquote
from decimal import Decimal
import time
reload(sys)
sys.setdefaultencoding("utf-8")


# write to csv file
def write_to_csv(filename, head_line, *info_list):
    with open(filename, 'w') as f:
        f.write(codecs.BOM_UTF8)
        writer = csv.writer(f)
        writer.writerow(head_line.split('\t'))
        for row in info_list:
            row_list = row.split('\t')
            writer.writerow(row_list)


def get_movie_base_info(subject):
    # header content
    douban_headers = {
         'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.81 Safari/537.36',
         'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
         'Accept-Encoding': 'gzip, deflate, sdch',
         'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4,en-GB;q=0.2,zh-TW;q=0.2',
         'Connection': 'keep-alive',
         'DNT': '1',
         'HOST': 'movie.douban.com',
         'Cookie': 'iv6LdR0AXBc'
    }
    
    url_link = 'https://movie.douban.com/subject/{0}/awards/' .format(subject)
    print url_link
    #url_link = 'https://movie.douban.com/subject/1296500'
    # request douban
    r = requests.get(url_link, headers=douban_headers)
    if r.status_code == 200:
        movie_info['error'] = None
    else:
        movie_info['error'] = 'request error'
    # store the html data to soup
    soup = BeautifulSoup(r.text.encode('utf-8'), 'lxml')
    # deal with page not found
    if re.search(u'你想访问的页面不存在', soup.prettify()):
        movie_info['error'] = 'movie_not_found'
        return movie_info
    try:
        for date in soup.select('span[property="v:initialReleaseDate"]'):
            r_date = pattern.search(date.text).group('r_date')
            r_region = pattern.search(date.text).group('r_region').encode('utf-8')
            #print r_region, r_date
            if '中国大陆'.decode('utf-8').encode("utf-8") in r_region:
                release_date = r_date
                # get first release date
                break
    except:
        pass
    # get award info
    award_info = []
    print soup.select('div[class="awards"]')[0:2]
    #if len(soup.select('ul[class="award"]')[0:2]) > 0:
        #for i in soup.select('ul[class="award"]')[0:2]:
        #    award_info.append(" / ".join([ x.text.replace('\n','') for x in i.find_all('li')[0:2]]))
        #movie_info['award'] = "award".join(award_info)
    if len(soup.select('ul[class="award"]')[0:2]) > 0:
        for i in soup.select('div[class="awards"]')[0:2]:
            ff_name = i.h2.a.text
            ff_year = i.h2.span.text
            #ff_unit = i.select('ul[class="award"]')[0].find('li').text
            for j in i.select('ul[class="award"]'):
                ff_unit = j.find('li').text
                ff_info = "{0}{1} / {2}" .format(ff_name, ff_year, ff_unit)
                print ff_info
                #if '柏林'.decode('utf-8') in ff_name:
                if re.search(pattern, ff_name):
                    award_info.append(ff_info)
        movie_info['award'] = "award".join(award_info)
    else:
        movie_info['award'] = 'N/A'
    #if ratingCount == '0':
    #    ratingValue = rating_info
    #    ratingCount = rating_info
    # deal with director
    return movie_info

def get_movie_detailed_info(f):
    with open(f,'rU') as f:
        movie_info_list = []
        for subject_id in f:
            subject_id = subject_id.strip()
            #data = get_movie_base_info(subject_id)
            try:
                data = get_movie_base_info(subject_id)
                # print "{0} {1}" .format(subject_id, data['error'])
                if data['error'] is not None:
                    movie_info = "{0}\t{1}" .format(subject_id,data['error'])
                else:
                    movie_info = "{0}\t{1}" \
                                            .format(
                                                subject_id,data['award'])
            except Exception:
                movie_info = "{0}\tinternal_running_error" .format(subject_id)
            movie_info_list.append(movie_info)
            print movie_info_list
            #sleeptime = random.uniform(0, 2)
            sleeptime = random.uniform(0, 3)
            sleeptime = Decimal(sleeptime).quantize(Decimal('0.00'))
            time.sleep(sleeptime)
    return movie_info_list


if __name__ == '__main__':
    movie_info = {}
    # (戛纳|威尼斯|柏林|奥斯卡|圣丹斯){1,}.*?([奖节]){1,}
    pattern = re.compile(ur'(\u621b\u7eb3|\u5a01\u5c3c\u65af|\u67cf\u6797|\u5965\u65af\u5361|\u5723\u4e39\u65af){1,}.*?([\u5956\u8282]){1,}')
    # douban movie subject id
    f = 'movie.list'
    f_csv = 'movie.csv'
    head_instruction = "subject_id\t获奖情况"
    movie_info_list = get_movie_detailed_info(f)
    write_to_csv(f_csv, head_instruction, *movie_info_list)
