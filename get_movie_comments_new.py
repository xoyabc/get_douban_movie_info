#!/usr/bin/env python3
import requests
import csv
import time
import random
import re
from bs4 import BeautifulSoup
from datetime import datetime
from decimal import Decimal

# 设置请求头，模拟浏览器访问
headers = {
         'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.81 Safari/537.36',
         'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
         'Accept-Encoding': 'gzip, deflate, sdch',
         'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4,en-GB;q=0.2,zh-TW;q=0.2',
         'Connection': 'keep-alive',
         'DNT': '1',
         'HOST': 'movie.douban.com',
         'Cookie': 'bid=20uJiaW_t90; __utmc=30149280; _vwo_uuid_v2=D58A38170FFC668C0CB18C36B0C691B37|cd739ae2795d08a093853c5a52a8dde1; viewed="36180769_35017678"; push_doumail_num=0; __utmv=30149280.5752; _pk_id.100001.4cf6=cc7b5c9ceec1371f.1776999850.; ll="108288"; __utmc=223695111; push_noty_num=0; ct=y; dbcl2="57525233:vUDckBOfmAM"; ck=t-SR; frodotk_db="f7c52970416f98a5e74f7c50c44ec9ef"; __utmz=30149280.1781417962.59.38.utmcsr=search.douban.com|utmccn=(referral)|utmcmd=referral|utmcct=/book/subject_search; ap_v=0,6.0; __utmz=223695111.1781418005.47.43.utmcsr=search.douban.com|utmccn=(referral)|utmcmd=referral|utmcct=/movie/subject_search; __utma=30149280.1078343254.1776908118.1781417962.1781422205.60; __utmb=30149280.0.10.1781422205; __utma=223695111.561227052.1776999850.1781418005.1781422205.48; __utmb=223695111.0.10.1781422205; _pk_ref.100001.4cf6=%5B%22%22%2C%22%22%2C1781422205%2C%22https%3A%2F%2Fsearch.douban.com%2Fmovie%2Fsubject_search%3Fsearch_text%3D%E5%85%9A%E5%90%8C%E4%BC%90%E5%BC%82%26cat%3D1002%22%5D; _pk_ses.100001.4cf6=1'
    }


# 随机休息若干秒
def random_sleep ():
    if line_num < 20:
        sleeptime = random.uniform(1, 3)
    elif line_num >= 20 and line_num < 50:
        sleeptime = random.uniform(6, 9)
    else:
        sleeptime = random.uniform(28, 38)
    sleeptime = Decimal(sleeptime).quantize(Decimal('0.00'))
    time.sleep(float(sleeptime))


def read_movie_ids_from_file(filename):
    """
    从文件中读取电影ID列表
    :param filename: 包含电影ID的文件路径
    :return: 电影ID列表
    """
    movie_ids = []
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                # 去除空白字符和空行
                movie_id = line.strip()
                if movie_id:
                    movie_ids.append(movie_id)
        print(f"从文件 {filename} 成功读取 {len(movie_ids)} 个电影ID")
        return movie_ids
    except Exception as e:
        print(f"读取电影ID文件失败: {e}")
        return []

def get_movie_comments(movie_id, total=100):
    """
    获取单个豆瓣电影的评论
    :param movie_id: 电影ID
    :param total: 需要获取的评论总数
    :return: 评论列表，每条个评论包含movie_id字段
    """
    comments = []
    page = 0
    count_per_page = 20  # 每页20条评论
    
    while len(comments) < total:
        # 计算还需要多少条评论
        remaining = total - len(comments)
        if remaining < count_per_page:
            count = remaining
        else:
            count = count_per_page
            
        # 计算总评论条数
        comment_url = f"https://movie.douban.com/subject/{movie_id}/comments"
        # 发送请求
        response = requests.get(comment_url, headers=headers)
        response.raise_for_status()  # 检查请求是否成功
        
        # 解析HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        text = soup.find('li', class_='is-active').find('span').text
        try:
            match = re.search(r'\((\d+)\)', text)
            if match:
                number = int(match.group(1))
            # 构造评论页URL
            if number <= 100:
                url = f"https://movie.douban.com/subject/{movie_id}/comments?start={page*count_per_page}&limit={count}&status=P&sort=new_score"
            else:
                url = f"https://movie.douban.com/subject/{movie_id}/comments?start={page*count_per_page}&limit={count}&status=P&sort=time"
            # 发送请求
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # 检查请求是否成功
            
            # 解析HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            comment_items = soup.find_all('div', class_='comment-item')
            
            # 如果没有评论了，退出循环
            if not comment_items:
                break
                
            # 提取评论信息
            for item in comment_items:
                # 昵称
                nickname_tag = item.find('span', class_='comment-info').find('a')
                nickname = nickname_tag.text.strip() if nickname_tag else "未知用户"
                
                # 评论时间
                comment_time_tag = item.find('a', class_='comment-time')
                comment_time = comment_time_tag['title'].strip() if comment_time_tag else "未知时间"
                
                # 评价星级
                rating = item.find('span', class_='rating')
                if rating:
                    rating_class = rating['class'][0]
                    # 从类名中提取星级，如"allstar50"表示5星
                    star = int(rating_class.replace('allstar', '')) // 10
                else:
                    star = "未评分"
                
                # 评论内容
                comment_content_tag = item.find('span', class_='short')
                comment_content = comment_content_tag.text.strip() if comment_content_tag else ""
                
                # 评论IP地址
                comment_ip_tag = item.find('span', class_='comment-location')
                if comment_ip_tag:
                    ip_info = comment_ip_tag.text.strip().split(' ')[0] if ' ' in comment_ip_tag.text.strip() else comment_ip_tag.text.strip()
                else:
                    ip_info = "未知IP"
                
                # 添加到评论列表，包含movie_id字段
                comments.append({
                    'movie_id': movie_id,
                    '昵称': nickname,
                    '评论时间': comment_time,
                    '评论内容': comment_content,
                    '评价星级': star,
                    '评价IP': ip_info
                })
                
                # 如果已达到目标数量，退出循环
                if len(comments) >= total:
                    break
            
            print(f"电影 {movie_id} 已获取 {len(comments)}/{total} 条评论")
            
            # 翻页
            page += 1
            
            # 控制爬取速度，避免被封IP
            random_sleep()
            
        except Exception as e:
            print(f"获取电影 {movie_id} 评论失败: {e}")
            break
    
    return comments

def save_to_csv(all_comments, filename=None):
    """
    将所有电影的评论保存到一个CSV文件
    :param all_comments: 所有电影的评论列表
    :param filename: 文件名，默认为当前时间+comments.csv
    """
    if not all_comments:
        print("没有评论可保存")
        return
        
    # 生成默认文件名
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"douban_multi_movie_comments_{timestamp}.csv"
    
    # 写入CSV文件
    try:
        with open(filename, 'w', encoding='utf-8-sig', newline='') as f:
            # 定义CSV字段，包含movie_id
            fieldnames = ['movie_id', '昵称', '评论时间', '评论内容', '评价星级', '评价IP']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            
            # 写入表头
            writer.writeheader()
            
            # 写入所有评论数据
            for comment in all_comments:
                writer.writerow(comment)
        
        print(f"所有评论已成功保存到 {filename}，共 {len(all_comments)} 条")
        
    except Exception as e:
        print(f"保存CSV文件失败: {e}")

if __name__ == "__main__":
    # 电影ID文件路径
    movie_ids_file = 'movie.list'

    # 获取文件行数
    with open(movie_ids_file,'r') as f:
        line_num = sum(1 for line in f)
        f.seek(0)  # 重置文件指针到文件开始

    # 从文件读取电影ID
    movie_ids = read_movie_ids_from_file(movie_ids_file)
    
    if not movie_ids:
        print("没有有效的电影ID，程序退出")
        exit()
    
    # 每个电影需要获取的评论数量
    comments_per_movie = 100
    
    all_comments = []
    
    # 遍历每个电影ID，获取评论
    for movie_id in movie_ids:
        print(f"\n开始获取电影ID为 {movie_id} 的最新 {comments_per_movie} 条评论...")
        movie_comments = get_movie_comments(movie_id, comments_per_movie)
        all_comments.extend(movie_comments)
        # 电影之间增加一点延迟
        time.sleep(1)
    
    # 保存所有评论到CSV
    if all_comments:
        save_to_csv(all_comments)
    else:
        print("未能获取到任何评论")
    
