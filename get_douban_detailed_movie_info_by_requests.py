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
from headers_config import USERAGENT_CONFIG
import time
reload(sys)
sys.setdefaultencoding("utf-8")
import urllib3
urllib3.disable_warnings()


# header content
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

# write to csv file
def write_to_csv(filename, head_line, *info_list):
    with open(filename, 'w') as f:
        f.write(codecs.BOM_UTF8)
        writer = csv.writer(f)
        writer.writerow(head_line.split('\t'))
        for row in info_list:
            row_list = row.split('\t')
            writer.writerow(row_list)


def get_celebrity_detailed_info(celebrity_id):
    celebrity_info = {}
    if 'celebrity' not in celebrity_id:
        celebrity_info['error'] = 'invalid format'
        return celebrity_info
    else:
        celebrity_info['error'] = None
    url_link = 'https://movie.douban.com{0}' .format(celebrity_id)
    try:
        random_useragent = random.choice(USERAGENT_CONFIG)
        r = requests.get(url_link, headers={'User-Agent': random_useragent} ,verify=False)
    except:
        r = requests.get(url_link, headers=douban_headers ,verify=False)
    soup = BeautifulSoup(r.text.encode('utf-8'), 'lxml')
    try:
        #soup_fans = soup.select('div[id="fans"]')[0].h2.find(text=re.compile("影迷".decode("utf-8"))).split('\n')[1]
        #celebrity_info['fans'] = re.match(r'^.*?([0-9]+).*$', soup_fans).group(1)
        soup_fans = soup.select('span[id="fans_count"]')[0].text
        celebrity_info['fans'] = soup_fans
    except:
        celebrity_info['fans'] = 'N/A'

    celebrity_info['celebrity_name'] = re.sub(u' \(豆瓣\)', '' ,soup.title.text.strip()).split()[0]
    #print "celebrity_name:{}" .format(celebrity_info['celebrity_name'])
    
    try:
        gender_anchor = soup.find("span", text=re.compile("性别".decode("utf-8")))
        gender = gender_anchor.next_element.next_element.strip().split('\n')[1].strip() 
    except AttributeError:
        gender = 'N/A'

    try:
        constellation_anchor = soup.find("span", text=re.compile("星座".decode("utf-8")))
        constellation = constellation_anchor.next_element.next_element.strip().split('\n')[1].strip()      
    except AttributeError:
        constellation = 'N/A'
    
    try:
        birthday_anchor = soup.find("span", text=re.compile("出生日期".decode("utf-8")))
        birthday = birthday_anchor.next_element.next_element.strip().split('\n')[1].strip()    
    except:
        birthday = 'N/A'
    
    try:
        birth_place_anchor = soup.find("span", text=re.compile("出生地".decode("utf-8")))
        birth_place = birth_place_anchor.next_element.next_element.strip().split('\n')[1].strip()    
    except AttributeError:
        birth_place = 'N/A'
    
    try:
        profession_anchor = soup.find("span", text=re.compile("职业".decode("utf-8")))
        profession = profession_anchor.next_element.next_element.strip().split('\n')[1].strip()    
    except AttributeError:
        profession = 'N/A'
    
    try:
        other_foreign_name_anchor = soup.find("span", text=re.compile("更多外文名".decode("utf-8")))
        other_foreign_name = other_foreign_name_anchor.next_element.next_element.strip().split('\n')[1].strip()    
    except:
        other_foreign_name = 'N/A'
    
    try:
        other_chinese_name_anchor = soup.find("span", text=re.compile("更多中文名".decode("utf-8")))
        #other_chinese_name = other_chinese_name_anchor.next_element.next_element.strip().split('\n')[1].strip()
        other_chinese_name = "/".join([ x for x in other_chinese_name_anchor.next_element.next_element.strip().split('\n')[1].strip().split('/') if '昵称xxx' in x ])
    except:
        other_chinese_name = 'N/A'
    
    try:
        imdb_number = soup.find("a", href=re.compile("https://www.imdb.com/name".decode("utf-8"))).text
    except:
        imdb_number = 'N/A'

    return celebrity_info


def get_movie_base_info(subject):
    
    url_link = 'https://movie.douban.com/subject/{0}' .format(subject)
    #url_link = 'https://movie.douban.com/subject/1296500'
    # request douban
    try:
        random_useragent = random.choice(USERAGENT_CONFIG)
        r = requests.get(url_link, headers={'User-Agent': random_useragent} ,verify=False)
    except:
        r = requests.get(url_link, headers=douban_headers ,verify=False)
    finally:
        if r.status_code == 200:
            movie_info['error'] = None
        else:
            movie_info['error'] = 'request error'
            return movie_info
    # store the html data to soup
    soup = BeautifulSoup(r.text.encode('utf-8'), 'lxml')
    # deal with page not found
    if re.search(u'你想访问的页面不存在', soup.prettify()):
        movie_info['error'] = 'movie_not_found'
        return movie_info
    # get release date
    pattern = re.compile(r'(?P<r_date>.*)\((?P<r_region>.*)\)')
    release_date = r_date = r_region = None
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
    movie_info['release_date'] = release_date
    # year
    try:
        soup_year = soup.h1.find_all('span', attrs={"class": "year"})[0].text
        movie_info['year'] = re.match(r'^.*([0-9]{4}).*$', soup_year).group(1)
    except IndexError:
        movie_info['year'] = 'N/A'
    # rating_info
    try:
        rating_info = soup.find_all(attrs={'class' : 'rating_sum'})[0].text.strip()
    except IndexError:
        rating_info = "无评分项"
    # type, name, duration, director, actor, genre, ratingCount, ratingValue
    script_json = soup.find_all(attrs={'type' : 'application/ld+json'})[0].contents[0].strip()
    movie_json = json.loads(script_json, strict=False)
    movie_info['type'] = movie_json.get('@type', 'N/A')
    #movie_info['name'] = movie_json.get('name', 'N/A').split()[0]
    movie_info['name'] = re.sub(u' \(豆瓣\)', '' ,soup.title.text.strip())
    actor_id = director_id = 'N/A'
    try:
        movie_info['duration'] = 'N/A' if movie_json['duration'] == '' else movie_json.get('duration', 'N/A').replace('PT', '')
    except Exception:
        movie_info['duration'] = 'N/A' 
    try:
        director =  movie_json['director'][0].get('name', 'N/A').split()[0]
        director_id = movie_json['director'][0].get('url', 'N/A')
    except IndexError:
        director = 'N/A'
    try:
        actor  = movie_json['actor'][0].get('name', 'N/A').split()[0]
        actor_id = movie_json['actor'][0].get('url', 'N/A')
    except IndexError:
        actor  = 'N/A'
    try:
        movie_info['genre'] = 'N/A' if len(movie_json.get('genre')) < 1 else "/".join(movie_json.get('genre', ['N/A']))
    except IndexError:
        movie_info['genre']  = 'N/A'
    ratingValue = movie_json['aggregateRating']['ratingValue']
    ratingCount = movie_json['aggregateRating']['ratingCount']
    if ratingCount == '0':
        ratingValue = rating_info
        ratingCount = rating_info
    movie_info['ratingValue'] = ratingValue
    movie_info['ratingCount'] = ratingCount
    # directedBy, cast, region, language, imdb
    subuject_info_result = soup.find_all(attrs={'id' : 'info'})[0]
    directedBy_id = cast_id = 'N/A'
    try:
        directedBy = subuject_info_result.find('a', attrs={"rel": "v:directedBy"}).text
    except AttributeError:
        directedBy = 'N/A'
    # get directedBy celebrity id
    try:
        if 'celebrity' in subuject_info_result.find('a', attrs={"rel": "v:directedBy"})['href']:
            directedBy_id = subuject_info_result.find('a', attrs={"rel": "v:directedBy"})['href']
    except TypeError:
        directedBy_id = 'N/A'
    print "directedBy_id:{}" .format(directedBy_id)
    try:
        cast = subuject_info_result.find('a', attrs={"rel": "v:starring"}).text
    except AttributeError:
        cast = 'N/A'
    # get cast celebrity id
    try:
        if 'celebrity' in subuject_info_result.find('a', attrs={"rel": "v:starring"})['href']:
            cast_id = subuject_info_result.find('a', attrs={"rel": "v:starring"})['href']
    except TypeError:
        cast_id = 'N/A'
    print "cast_id:{}" .format(cast_id)
    #duration = subuject_info_result.find('span', attrs={"property": "v:runtime"}).text.replace(' ', '')
    subject_base_info_list = subuject_info_result.contents
    # init language and imdb_number in case the corresponding key does not exist
    movie_info['language'] = 'N/A'
    movie_info['imdb_number'] = 'N/A'
    for i,v in enumerate(subject_base_info_list):
        if v.string is not None and '制片国家/地区:' in v.string:
            movie_info['region'] = subject_base_info_list[i+1].string.strip().split('/')[0].replace(" ", "")
        if v.string is not None and '语言:' in v.string:
            movie_info['language'] = subject_base_info_list[i+1].string.strip().split('/')[0].replace(" ", "")
        if v.string is not None and 'IMDb:' in v.string:
            movie_info['imdb_number'] = subject_base_info_list[i+1].string.strip()
    '''
    other solutions to  get region, Language ,imdb_number
    # Method 1
    info_list = subuject_info_result.text.split()
    for i,v in enumerate(info_list):
        if '导演:' in v:
            print info_list[i+1]
        elif '主演:' in v:
            print info_list[i+1]
        elif '片国家/地区:' in v:
            print info_list[i+1]
        elif '语言:' in v:
            print info_list[i+1]
        elif 'IMDb链接:' in  v:
            print info_list[i+1]
    # Method 2
    { v: info_list[i+1] for i,v in enumerate(info_list) if ':' in v }
    '''
    # Method 3
    #html = r.content.decode('utf-8')
    #re.findall(u'''语言:</span>(.*)<br/>''', html)[0]
    #re.findall(u'''<span class="pl">制片国家/地区:</span>(.*)<br/>''', html)[0]
    #re.findall(u'''<span class="pl">IMDb链接:</span> <a href="https://www.imdb.com/title/tt[0-9]+" target="_blank" rel="nofollow">(.*)</a><br>''', html)[0]
    # deal with director
    if directedBy == 'N/A':
        movie_info['director'] = director
    else:
        movie_info['director'] = directedBy
    # deal with actor
    # add 'cast != actor' to deal with the subject when first starring in 'v:starring' is not in accord with the 
    # first element of "actor" list in 'application/ld+json', such as https://movie.douban.com/subject/1299832/
    if cast == 'N/A' or cast != actor:
        movie_info['actor'] = actor
    else:
        movie_info['actor'] = cast
    # get fans of director
    if directedBy_id == 'N/A':
        movie_info['director_fans'] = get_celebrity_detailed_info(director_id).get('fans', 0)
    else:
        movie_info['director_fans'] = get_celebrity_detailed_info(directedBy_id).get('fans', 0)
    # get fans of actor
    if cast_id == 'N/A':
        movie_info['actor_fans'] = get_celebrity_detailed_info(actor_id).get('fans', 0)
    else:
        movie_info['actor_fans'] = get_celebrity_detailed_info(cast_id).get('fans', 0)
    
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
                    movie_info = "{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}\t{8}\t{9}\t{10}\t{11}\t{12}\t{13}\t{14}\t{15}" \
                                            .format(
                                                subject_id,data['type'],
                                                data['name'],data['year'],data['duration'],
                                                data['ratingValue'],
                                                data['ratingCount'], data['region'],
                                                data['release_date'],
                                                data['language'],data['genre'], data['actor'],
                                                data['actor_fans'], data['director'],
                                                data['director_fans'], data['imdb_number'])
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
    # douban movie subject id
    f = 'movie.list'
    f_csv = 'movie.csv'
    head_instruction = "subject_id\ttype\t中文名\t年份\t片长\t评分\t评价人数\t国家\t上映日期(中国大陆)\t语言\t类型\t主演\t主演收藏数\t导演\t导演收藏数\tIMDB编号"
    movie_info_list = get_movie_detailed_info(f)
    write_to_csv(f_csv, head_instruction, *movie_info_list)
