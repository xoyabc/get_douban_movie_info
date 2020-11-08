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

RESULT = {}
movie_info_file = "movie_info.txt"
TITLE = [
'subject_id', 'movie_type', 'movie_name', 'person_id', 'position',
'celebrity_name', 'fans_num'
]


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

def get_data():
    global RESULT
    try:
        fd = open(movie_info_file, 'rU')
        data = fd.read()
        RESULT_DICT = json.loads(data, strict=False)
    except Exception as e:
        pass
    else:
        if not RESULT:
            RESULT = RESULT_DICT
        fd.close()
    return RESULT


# store the movie info to file
def store_to_file(**DICT):
    fd = open(movie_info_file, 'w')
    try:
        fd.write(json.dumps(DICT))
    except Exception as e:
        err_msg = "Write error,errmsg: {}" .format(e)
        return err_msg, False
    finally:
        fd.close()
    ok_msg = "save to {} succeed" .format(movie_info_file)
    return ok_msg, True


def get_celebrity_detailed_info(celebrity_id):
    celebrity_info = {}
    if 'celebrity' not in celebrity_id:
        celebrity_info['error'] = 'invalid format'
        return celebrity_info
    else:
        celebrity_info['error'] = None
    url_link = 'https://movie.douban.com{0}' .format(celebrity_id)
    r = requests.get(url_link, headers=douban_headers)
    soup = BeautifulSoup(r.text.encode('utf-8'), 'lxml')
    soup_fans = soup.select('div[id="fans"]')[0].h2.find(text=re.compile("影迷".decode("utf-8"))).split('\n')[1]
    try:
        celebrity_info['fans'] = re.match(r'^.*?([0-9]+).*$', soup_fans).group(1)
    except:
        celebrity_info['fans'] = 'N/A'

    celebrity_info['celebrity_name'] = re.sub(u' \(豆瓣\)', '' ,soup.title.text.strip())
    
    try:
        gender_anchor = soup.find("span", text=re.compile("性别".decode("utf-8")))
        celebrity_info['gender'] = gender_anchor.next_element.next_element.strip().split('\n')[1].strip() 
    except AttributeError:
        celebrity_info['gender'] = 'N/A'

    try:
        constellation_anchor = soup.find("span", text=re.compile("星座".decode("utf-8")))
        celebrity_info['constellation'] = constellation_anchor.next_element.next_element.strip().split('\n')[1].strip()      
    except AttributeError:
        celebrity_info['constellation'] = 'N/A'
    
    try:
        birthday_anchor = soup.find("span", text=re.compile("出生日期".decode("utf-8")))
        celebrity_info['birthday'] = birthday_anchor.next_element.next_element.strip().split('\n')[1].strip()    
    except AttributeError:
        celebrity_info['birthday'] = 'N/A'

    try:
        birthday_anchor = soup.find("span", text=re.compile("生卒日期".decode("utf-8")))
        celebrity_info['birthday'] = birthday_anchor.next_element.next_element.strip().split('\n')[1].strip().split()[0]
        celebrity_info['deathday'] = birthday_anchor.next_element.next_element.strip().split('\n')[1].strip().split()[2]
    except AttributeError:
        celebrity_info['deathday'] = 'N/A'

    try:
        birth_place_anchor = soup.find("span", text=re.compile("出生地".decode("utf-8")))
        celebrity_info['birth_place'] = birth_place_anchor.next_element.next_element.strip().split('\n')[1].strip()    
    except AttributeError:
        celebrity_info['birth_place'] = 'N/A'
    
    try:
        profession_anchor = soup.find("span", text=re.compile("职业".decode("utf-8")))
        celebrity_info['profession'] = profession_anchor.next_element.next_element.strip().split('\n')[1].strip()    
    except AttributeError:
        celebrity_info['profession'] = 'N/A'
    
    try:
        other_foreign_name_anchor = soup.find("span", text=re.compile("更多外文名".decode("utf-8")))
        foreign_nick_name = "/".join([ x for x in other_foreign_name_anchor.next_element.next_element.strip().split('\n')[1].strip().split('/ ') if '昵称' in x ])
        celebrity_info['other_foreign_name'] = 'N/A' if chinese_nick_name == '' else foreign_nick_name
    except:
        celebrity_info['other_foreign_name'] = 'N/A'
    
    try:
        other_chinese_name_anchor = soup.find("span", text=re.compile("更多中文名".decode("utf-8")))
        #other_chinese_name = other_chinese_name_anchor.next_element.next_element.strip().split('\n')[1].strip()
        chinese_nick_name = "/".join([ x for x in other_chinese_name_anchor.next_element.next_element.strip().split('\n')[1].strip().split('/ ') if '昵称' in x ])
        celebrity_info['other_chinese_name'] = 'N/A' if chinese_nick_name == '' else chinese_nick_name
    except:
        celebrity_info['other_chinese_name'] = 'N/A'
    
    try:
        imdb_number = soup.find("a", href=re.compile("https://www.imdb.com/name".decode("utf-8"))).text
        celebrity_info['imdb_number'] = imdb_number
    except:
        celebrity_info['imdb_number'] = 'N/A'

    sleeptime = random.uniform(0, 3)
    sleeptime = Decimal(sleeptime).quantize(Decimal('0.00'))
    time.sleep(sleeptime)

    return celebrity_info


def get_movie_detailed_info(f):
    with open(f,'rU') as f:
        movie_info_list = []
        for subject_id in f:
            subject_id = subject_id.strip()
            url_link = 'https://movie.douban.com/subject/{0}' .format(subject_id)
            r = requests.get(url_link, headers=douban_headers)
            if r.status_code == 200:
                movie_error = None
            else:
                movie_error = 'request error'
            # store the html data to soup
            soup = BeautifulSoup(r.text.encode('utf-8'), 'lxml')
            # deal with page not found
            if re.search(u'你想访问的页面不存在', soup.prettify()):
                movie_error = 'movie_not_found'
            # get type, name, director info, actor info
            script_json = soup.find_all(attrs={'type' : 'application/ld+json'})[0].get_text()
            movie_json = json.loads(script_json, strict=False)
            movie_type = movie_json.get('@type', 'N/A')
            movie_name = re.sub(u' \(豆瓣\)', '' ,soup.title.text.strip())
            # directedBy, cast
            subuject_info_result = soup.find_all(attrs={'id' : 'info'})[0]
            try:
                directedBy = subuject_info_result.find('a', attrs={"rel": "v:directedBy"}).text
            except AttributeError:
                directedBy = 'N/A'
            try:
                cast = subuject_info_result.find('a', attrs={"rel": "v:starring"}).text
            except AttributeError:
                cast = 'N/A'
            if movie_error is not None:
                movie_info = "{0}\t{1}" .format(subject_id, movie_error)
                movie_info_list.append(movie_info)
            else:
                # get director actor celebrity id
                # match chinese character
                pattern =re.compile(u"[\u4e00-\u9fa5]+")
                position_list = ['director', 'actor']
                # init vars
                person_id = gender = constellation = birthday = deathday = birth_place = profession \
                          = other_foreign_name = other_chinese_name = imdb_number = 'N/A'
                fans_num = 0
                print '---导演---\n'
                for i in position_list:
                    position = '导演' if i == 'director' else '主演'
                    if len(movie_json[i]) == 0:
                        celebrity_name = directedBy if i == 'director' else cast
                        movie_info = "{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}\t{8}\t{9}\t{10}\t{11}\t{12} \
                                      \t{13}\t{14}\t{15}" .format(subject_id, movie_type, movie_name, person_id, 
                                                                  position, celebrity_name, fans_num, gender, 
                                                                  constellation, birthday, deathday, birth_place,
                                                                  profession, other_foreign_name, other_chinese_name,
                                                                  imdb_number)
                        movie_info_list.append(movie_info)
                        print movie_name, movie_type, celebrity_name
                    else:
                        for person in  movie_json[i][0:2]:
                            name = person.get('name', 'N/A')
                            person_id = person.get('url', 'N/A')
                            if len(re.findall(pattern, name)) == 0:
                                # get original name if chinese name does not exist
                                celebrity_name = name
                            else:
                                # get chinese name
                                celebrity_name = person.get('name', 'N/A').split()[0]
                            RESULT = get_data()
                            if person_id in RESULT:
                                err_msg = "{} is already added" .format(person_id)
                                celebrity_info = RESULT[person_id]
                                print err_msg
                            else:
                                celebrity_info = get_celebrity_detailed_info(person_id)
                                RESULT[person_id] = celebrity_info
                                store_to_file(**RESULT)
                            fans_num = celebrity_info['fans']
                            gender = celebrity_info['gender']
                            constellation = celebrity_info['constellation']
                            birthday = celebrity_info['birthday']
                            deathday = celebrity_info['deathday']
                            birth_place = celebrity_info['birth_place']
                            profession = celebrity_info['profession']
                            other_foreign_name = celebrity_info['other_foreign_name']
                            other_chinese_name = celebrity_info['other_chinese_name']
                            imdb_number = celebrity_info['imdb_number']

                            movie_info = "{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}\t{8}\t{9} \
                                          \t{10}\t{11}\t{12}\t{13}\t{14}\t{15}"  \
                                         .format(subject_id, movie_type, movie_name, person_id, position,
                                                celebrity_name, fans_num, gender, constellation, birthday,
                                                deathday, birth_place, profession, other_foreign_name,
                                                other_chinese_name, imdb_number)
                            movie_info_list.append(movie_info)
                            print subject_id, movie_type, movie_name, position, celebrity_name, person_id, fans_num, gender, constellation, birthday, deathday, birth_place, profession, other_foreign_name, other_chinese_name, imdb_number
            sleeptime = random.uniform(0, 3)
            sleeptime = Decimal(sleeptime).quantize(Decimal('0.00'))
            time.sleep(sleeptime)
    return movie_info_list


if __name__ == '__main__':
    # douban movie subject id
    f = 'movie.list'
    f_csv = 'movie.csv'
    head_instruction = "subject_id\ttype\t中文名\tcelebrity_id\tposition\tcelebrity_name\t收藏数 \
                        \t性别\t星座\t出生日期\t逝世日期\t出生地\t职业\t更多外文名\t更多中文名\timdb编号"
    movie_info_list = get_movie_detailed_info(f)
    write_to_csv(f_csv, head_instruction, *movie_info_list)
