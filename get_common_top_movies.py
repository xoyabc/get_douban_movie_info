#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import csv
import re
import os
'''
1，csv文件存放在子目录 data 中
2，00_all_movies.csv 为影片详细信息数据文件
3，01_IMDbtop250.csv 为 IMDB top250 影片信息文件
4，07_Douban_top250_movies.csv 为豆瓣 top250 片信息文件
5，common_movies.csv 存放共同影片
'''

# 获取豆瓣条目ID
def get_dbid_from_csv(filename, rowname):
    file = os.path.join('.', 'data', filename)
    pattern = re.compile(r'(?P<db_id>\d+)')
    with open(file, 'r', newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        k = rowname
        LIST_DB = [ pattern.search(row[k]).group('db_id') for row in reader ]
        return (LIST_DB)


# 使用递归获取共同影片
def get_common_data(l1, *info_list): 
    for l in info_list: 
        common_list = [] 
        for i in l:
            if len(list(filter(lambda x: x == i, l1))) > 0:
                common_list.append(i) 
        # 将 common_list 赋给 l1, 动态更新 l1，后面查找共同元素时，从已有的共同元素( l1 )里面查找
        l1 = common_list 
    return common_list


# 获取各个榜单影片排名
def get_rank_list(filename, douban_=False, CC_=False):
    rank_file = os.path.join('.', 'data', filename)
    f_db = open(rank_file, 'r', encoding='utf-8-sig')
    reader = csv.DictReader(f_db) 
    if douban_:
        pattern = re.compile(r'(?P<db_id>\d+)')
        rank_dict = { pattern.search(row['链接']).group('db_id'): (i+1) for i,row in enumerate(list(reader)) }
    elif CC_:
        rank_dict = { row['dbid']: row['spine'] for row in reader }
    else:
        rank_dict = { row['dbid']: row['rank'] for row in reader }
    return rank_dict


# 写入到csv文件
# 使用 encoding='utf-8-sig' 避免 windows 下中文乱码
def write_to_csv(filename, head_line, *info_list):
    file = os.path.join('.', 'data', filename)
    with open(file, 'w', encoding='utf-8-sig') as f:
        fnames = head_line
        writer = csv.DictWriter(f, fieldnames=fnames)
        writer.writeheader()
        writer.writerows(info_list)

# 查找共同影片详细信息
def search_movie(db_file, new_file, *info_list):
    # get rank info
    db_rank = get_rank_list('07_Douban_top250_movies.csv', douban_=True)
    imdb_rank = get_rank_list('01_IMDbtop250.csv')

    # get detailed movie info
    file = os.path.join('.', 'data', db_file)
    with open(file, 'r', encoding='utf-8-sig') as f:
            l = [] 
            reader = csv.DictReader(f) 
            for row in reader: 
                for i in info_list:  
                    if row['subject_id'] == i:
                        row['IMDB_rank'] = imdb_rank[i]
                        row['db_rank'] = db_rank[i]
                        l.append(row) 
            head_line = ['subject_id', 'type', '中文名', '年份', '片长', '评分', '评价人数', '国家', '语言', '类型', '主演', '导演', 'IMDB编号', 'IMDB_rank', 'db_rank']
            write_to_csv(new_file, head_line, *l)

if __name__ == '__main__':
    MOVIE_LISTS=[]
    LIST_DB= get_dbid_from_csv('07_Douban_top250_movies.csv', '链接')
    LIST_IMDB= get_dbid_from_csv('01_IMDbtop250.csv', 'dbid')
    MOVIE_LISTS.append(LIST_DB)
    common_movies = get_common_data(LIST_IMDB, *MOVIE_LISTS)
    search_movie('00_all_movies.csv', 'common_movies.csv', *common_movies)
