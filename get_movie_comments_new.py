#!/usr/bin/env python3
import requests
import csv
import time
import random
from bs4 import BeautifulSoup
from datetime import datetime
from decimal import Decimal

# 设置请求头，模拟浏览器访问
#headers = {
#    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
#}


headers = {
         'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.81 Safari/537.36',
         'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
         'Accept-Encoding': 'gzip, deflate, sdch',
         'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4,en-GB;q=0.2,zh-TW;q=0.2',
         'Connection': 'keep-alive',
         'DNT': '1',
         'HOST': 'movie.douban.com',
         'Cookie': '__utmc=223695111; _vwo_uuid_v2=DC1819A9385ACA561B32B51177989F115|33c368c4b7f6b3f563c632a4119a2951; Hm_lpvt_19fc7b106453f97b6a84d64302f21a04=1692380997; __utmc=30149280; push_doumail_num=0; __utmv=30149280.5752; _vwo_uuid_v2=DC1819A9385ACA561B32B51177989F115|33c368c4b7f6b3f563c632a4119a2951; bid=QQBZ5tbKfPc; _pk_id.100001.4cf6=15476aa0687612b3.1749580254.; __yadk_uid=c9ojKFU97DPTVMc0XOhxDb81RTYS0jkf; _ga_Y4GN1R87RG=GS2.1.s1757864605$o13$g0$t1757864605$j60$l0$h0; ll="108288"; ct=y; _ga=GA1.2.696822769.1681311745; _ga_PRH9EWN86K=GS2.2.s1761318662$o2$g0$t1761318662$j60$l0$h0; dbcl2="57525233:sltNE/LoMI4"; ck=cXdw; frodotk_db="dd0d9bf6bee11ec19728d3e43ca35c43"; push_noty_num=0; ap_v=0,6.0; _pk_ref.100001.4cf6=%5B%22%22%2C%22%22%2C1761497018%2C%22https%3A%2F%2Fsearch.douban.com%2Fmovie%2Fsubject_search%3Fsearch_text%3D%E8%B5%9D%E5%93%81%26cat%3D1002%22%5D; _pk_ses.100001.4cf6=1; __utma=30149280.696822769.1681311745.1761495178.1761497018.517; __utmb=30149280.0.10.1761497018; __utmz=30149280.1761497018.517.304.utmcsr=search.douban.com|utmccn=(referral)|utmcmd=referral|utmcct=/movie/subject_search; __utma=223695111.696822769.1681311745.1761495178.1761497018.459; __utmb=223695111.0.10.1761497018; __utmz=223695111.1761497018.459.339.utmcsr=search.douban.com|utmccn=(referral)|utmcmd=referral|utmcct=/movie/subject_search'
    }

# 随机休息若干秒
def random_sleep ():
    sleeptime = random.uniform(2, 5)
    sleeptime = Decimal(sleeptime).quantize(Decimal('0.00'))
    time.sleep(sleeptime)

def get_movie_comments(movie_id, total=100):
    """
    获取豆瓣电影评论
    :param movie_id: 电影ID
    :param total: 需要获取的评论总数
    :return: 评论列表
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
            
        # 构造评论页URL
        url = f"https://movie.douban.com/subject/{movie_id}/comments?start={page*count_per_page}&limit={count}&status=P&sort=time"
        
        try:
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
                nickname = item.find('span', class_='comment-info').find('a').text.strip()
                
                # 评论时间
                comment_time = item.find('span', class_='comment-time')['title'].strip()
                
                # 评价星级
                rating = item.find('span', class_='rating')
                if rating:
                    rating_class = rating['class'][0]
                    # 从类名中提取星级，如"allstar50"表示5星
                    star = int(rating_class.replace('allstar', '')) // 10
                else:
                    star = "未评分"
                
                # 评论内容
                comment_content = item.find('span', class_='short').text.strip()
                
                # 评论IP地址和时间
                comment_ip_time = item.find('span', class_='comment-location').text.strip()
                # 分割IP和时间
                if ' ' in comment_ip_time:
                    ip_info, _ = comment_ip_time.split(' ', 1)
                else:
                    ip_info = comment_ip_time
                
                # 添加到评论列表
                comments.append({
                    '昵称': nickname,
                    '评论时间': comment_time,
                    '评论内容': comment_content,
                    '评价星级': star,
                    '评价IP': ip_info
                })
                
                # 如果已达到目标数量，退出循环
                if len(comments) >= total:
                    break
            
            print(f"已获取 {len(comments)}/{total} 条评论")
            
            # 翻页
            page += 1
            
            # 控制爬取速度，避免被封IP
            random_sleep()
            
        except Exception as e:
            print(f"获取评论失败: {e}")
            break
    
    return comments

def save_to_csv(comments, filename=None):
    """
    将评论保存到CSV文件
    :param comments: 评论列表
    :param filename: 文件名，默认为当前时间+comments.csv
    """
    if not comments:
        print("没有评论可保存")
        return
        
    # 生成默认文件名
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"douban_comments_{timestamp}.csv"
    
    # 写入CSV文件
    try:
        with open(filename, 'w', encoding='utf-8-sig', newline='') as f:
            # 定义CSV字段
            fieldnames = ['昵称', '评论时间', '评论内容', '评价星级', '评价IP']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            
            # 写入表头
            writer.writeheader()
            
            # 写入评论数据
            for comment in comments:
                writer.writerow(comment)
        
        print(f"评论已成功保存到 {filename}")
        
    except Exception as e:
        print(f"保存CSV文件失败: {e}")

if __name__ == "__main__":
    # 示例：获取《肖申克的救赎》的评论，电影ID为1292052
    movie_id = "1440610"  # 可以替换为其他电影的ID
    comment_count = 100    # 获取100条评论
    
    print(f"开始获取电影ID为 {movie_id} 的最新 {comment_count} 条评论...")
    comments = get_movie_comments(movie_id, comment_count)
    
    if comments:
        save_to_csv(comments)
    else:
        print("未能获取到评论")
