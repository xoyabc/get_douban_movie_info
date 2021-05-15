#!/usr/bin/env python3
import requests
from urllib.parse import urlencode
import re
import csv
import time
import random
from decimal import Decimal
import  http.cookiejar

BID_LIST_LEN = 500
BID_LEN = 11
BIDS = []
cookies=http.cookiejar.CookieJar()


def gen_bids():
    bids = []
    for i in range(BID_LIST_LEN):
        bid = []
        for x in range(BID_LEN):
            bid.append(chr(random.randint(65, 90)))
        bids.append("".join(bid))
    return bids


# 随机休息若干秒
def random_sleep ():
    sleeptime = random.uniform(5, 25)
    sleeptime = Decimal(sleeptime).quantize(Decimal('0.00'))
    time.sleep(sleeptime)

# 获取网页请求数据
def get_one(num):
    headers = {
         'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.81 Safari/537.36',
         'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
         'Accept-Encoding': 'gzip, deflate, sdch',
         'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4,en-GB;q=0.2,zh-TW;q=0.2',
         'Connection': 'keep-alive',
         'DNT': '1',
         'HOST': 'movie.douban.com',
         'Cookie': '_pk_ses.100001.4cf6=*; ap_v=0,6.0; __utma=30149280.2142271506.1571898253.1571898253.1571898253.1; __utmc=30149280; __utmz=30149280.1571898253.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); __utmt=1; __utmb=30149280.2.9.1571898253; bid=zWyZz_nJmBI; dbcl2="57525233:2ZYlFd6yfXE"; __utma=223695111.2140366512.1571898264.1571898264.1571898264.1; __utmb=223695111.0.10.1571898264; __utmc=223695111; __utmz=223695111.1571898264.1.1.utmcsr=accounts.douban.com|utmccn=(referral)|utmcmd=referral|utmcct=/passport/login; push_doumail_num=0; push_noty_num=0; _pk_id.100001.4cf6=98bd0164fbf3431a.1571898253.1.1571898283.1571898253.; ck=3ZaW; ps=y'
    }
    '''
    headers = {
        'User - Agent': 'Mozilla / 5.0(Windows NT 10.0;WOW64) AppleWebKit / 537.36(KHTML, likeGecko) Chrome / 66.0.3359.170Safari / 537.36'
    }
    '''
    '''
    BIDS = gen_bids()
    headers = {
        'User-Agent': 'Baiduspider',
        'Accept-Language': 'zh-CN,zh;en-US,en',
        'Referer': 'https://www.douban.com/'
    }
    #cookie = http.cookiejar.Cookie(None, 'bid', random.choice(BIDS), '80', '80', '.douban.com', None, None, '/', None, False, False, None, None, None, None)
    #cookies.set_cookie(cookie)
    #load_cookies = requests.utils.dict_from_cookiejar(cookies)
    '''
    params = {
        'start': str(num),
        'limit': '20',
        #'sort': 'new_score',
        'sort': 'time',
        'status': 'P',
        'percent_type': ''
    }
    #base_url = 'https://movie.douban.com/subject/27113517/comments?'
    base_url = 'https://movie.douban.com/subject/30200427/comments?'
    url = base_url + urlencode(params)
    print("正在采集：" + url)
    try:
        #requests.session.cookies=requests.utils.cookiejar_from_dict(load_cookies)
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.text
    except EOFError as e:
        print(e)
        return None

# 解析网页结构
def parse_page(html):
    info = []
    #patten1 = re.compile(r'<div class="comment">.*?<span class="votes">(.*?)</span>.*?<a href=.*?class="">(.*?)</a>.*?<span class="all(.*?)0 rating" title=".*?<span class="comment-time " title="(.*?)">.*?</span>.*?<p class="">.*?<span class="short">(.*?)</span>.*?</p>.*?</div>', re.S)
    patten1 = re.compile(r'<div class="comment">.*?<span class="votes vote-count">(.*?)</span>.*?<a href=.*?class="">(.*?)</a>.*?<span class="all(.*?)0 rating" title=".*?<span class="comment-time " title="(.*?)">.*?</span>.*?<span class="short">(.*?)</span>.*?</p>.*?</div>', re.S)
    datas = re.findall(patten1, str(html))
    for data in datas:
        comic = {}
        comic['Vote_num'] = int(data[0].strip())
        comic['User'] = data[1].strip()
        comic['Star'] = data[2].strip()
        comic['Time'] = data[3].strip()
        comic['Comment'] = data[4].strip().split()
        print (data[4].strip())
        info.append(comic)
    return info

# 保存数据
def write_to_file(info):
    with open('comments.csv', 'a', newline='', encoding='utf-8-sig') as f:
        fieldnames = ['Vote_num', 'User', 'Star', 'Time', 'Comment']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        try:
            writer.writerows(info)
        except:
            pass

# 执行函数
def main():
    #for i in range(480):
    for i in range(5):
        html = get_one(i*20)
        datas = parse_page(html)
        datas.sort(key=lambda k: (k.get('Vote_num', 0)), reverse=True)
        write_to_file(datas)
        print('本页采集完毕。')  # 采集完一页后的标识
        random_sleep()  # 采集完一页休息若干秒

if __name__ == '__main__':
    main()
