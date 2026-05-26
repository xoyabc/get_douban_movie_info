#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import json
import re
import time
import random
import csv
from datetime import datetime
import sys

# ============ 独立 COOKIE 变量配置 ============
# 默认空，需要时填写：例如 "bid=xxx; douban-fav-remind=1; __utma=xxx;"
#COOKIE = ''
COOKIE = 'bid=HsJsjNjAMW8; ll="108288"; _vwo_uuid_v2=D159B0FEAE98E92504C9D5EE1B1FDE8D4|4c028c5dfa7f8d72bb8f8741ccabc525; _pk_id.100001.8cb4=0ab8050b5417ea3b.1767544622.; __utmc=30149280; __utmv=30149280.5752; push_doumail_num=0; ct=y; _pk_ref.100001.8cb4=%5B%22%22%2C%22%22%2C1774977252%2C%22https%3A%2F%2Fmovie.douban.com%2Fsubject%2F38396228%2F%22%5D; dbcl2="57525233:673b+5fFP+Y"; ck=AU78; frodotk_db="753392586051f06b5f9ab70920f5d141"; ap_v=0,6.0; push_noty_num=0; __utma=30149280.1614386525.1769827582.1775142095.1775147146.23; __utmb=30149280.0.10.1775147146; __utmz=30149280.1775147146.23.17.utmcsr=search.douban.com|utmccn=(referral)|utmcmd=referral|utmcct=/movie/subject_search'
# =============================================
# 分页参数模板
PAGE_PARAMS = "?start={}&sort=seq&playable=0&sub_type="

# 请求头
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://www.douban.com/",
    "Accept-Language": "zh-CN,zh;q=0.9"
}

# 若 COOKIE 不为空，则添加到请求头
cookie_enabled = False
if COOKIE.strip():
    HEADERS["Cookie"] = COOKIE.strip()
    cookie_enabled = True
    print(f"✅ 已加载自定义 Cookie: {COOKIE[:20]}...")  # 仅打印前20字符，避免泄露
else:
    print("ℹ️  未配置 Cookie，使用匿名请求")

def get_total_items():
    """
    获取豆列总条目数，计算总页数
    优先级：1. a.active 标签 → 2. 页面全文兜底
    :return: total_items, total_pages
    """
    try:
        response = requests.get(DOUBAN_LIST_BASE_URL, headers=HEADERS, timeout=10)
        response.raise_for_status()
        response.encoding = response.apparent_encoding
        soup = BeautifulSoup(response.text, "html.parser")
        
        # 优先级1：严格匹配 a.active 标签
        total_tag = soup.find("a", class_="active")
        if total_tag:
            total_text = total_tag.get_text(strip=True)
            total_match = re.search(r'\((\d+)\)', total_text)
            if total_match:
                total_items = int(total_match.group(1))
                total_pages = (total_items + 24) // 25  # 向上取整
                print(f"📊 [标签匹配成功] 豆列总条目数：{total_items} | 总页数：{total_pages}")
                return total_items, total_pages
        
        # 优先级2：兜底 - 搜索页面全文
        page_text = soup.get_text(strip=True)
        total_match = re.search(r'全部\((\d+)\)', page_text)
        if total_match:
            total_items = int(total_match.group(1))
            total_pages = (total_items + 24) // 25
            print(f"📊 [全文兜底成功] 豆列总条目数：{total_items} | 总页数：{total_pages}")
            return total_items, total_pages

    except Exception as e:
        print(f"⚠️  获取总条目数失败，默认按10页以内处理 | 错误：{e}")
    return 0, 10  # 失败时默认总页数10

def crawl_single_page(start, total_pages, is_last_page=False):
    """
    爬取单页数据，根据总页数动态设置延迟，休眠后置
    :param start: 分页起始值
    :param total_pages: 总页数
    :param is_last_page: 是否为最后一页，最后一页无需休眠
    :return: 该页电影列表
    """
    page_url = DOUBAN_LIST_BASE_URL + PAGE_PARAMS.format(start)
    movie_list = []
    try:

        response = requests.get(page_url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        response.encoding = response.apparent_encoding
        soup = BeautifulSoup(response.text, "html.parser")
        items = soup.find_all("div", class_="doulist-item")

        if not items:
            print(f"⚠️  第 {start//25 + 1} 页无数据，停止爬取")
            return movie_list

        print(f"\n📄 开始爬取第 {start//25 + 1} 页（start={start}）")
        for idx, item in enumerate(items, 1):
            movie_info = {}

            # 1. 条目ID
            link_tag = item.find("a", class_="doulist-link") or item.find("a", href=lambda x: x and "movie.douban.com" in x)
            if link_tag:
                link_href = link_tag.get("href", "")
                id_match = re.search(r'subject/(\d+)', link_href)
                movie_info["条目ID"] = id_match.group(1) if id_match else "未知"
            else:
                movie_info["条目ID"] = "未知"

            # 2. 中文片名/原始片名
            title_tag = item.find("div", class_="title")
            if title_tag:
                full_title = title_tag.get_text(strip=True).replace("\n", "").replace("  ", " ")
                if " " in full_title:
                    chinese_title, original_title = full_title.split(" ", 1)
                    movie_info["中文片名"] = chinese_title
                    movie_info["原始片名"] = original_title
                else:
                    movie_info["中文片名"] = full_title
                    movie_info["原始片名"] = ""
            else:
                movie_info["中文片名"] = "未知"
                movie_info["原始片名"] = ""

            # 3. 导演/制片国家/地区/年份
            abstract_tag = item.find("div", class_="abstract")
            if abstract_tag:
                field_lines = [line.strip() for line in abstract_tag.stripped_strings]
                for line in field_lines:
                    if line.startswith(("导演:", "导演：")):
                        movie_info["导演"] = line.split("：")[-1].strip() if "：" in line else line.split(":")[-1].strip()
                    elif line.startswith(("制片国家/地区:", "制片国家/地区：")):
                        movie_info["制片国家/地区"] = line.split("：")[-1].strip() if "：" in line else line.split(":")[-1].strip().split('/', 1)[0]
                    elif line.startswith(("年份:", "年份：")):
                        movie_info["年份"] = line.split("：")[-1].strip() if "：" in line else line.split(":")[-1].strip()
            movie_info.setdefault("导演", "未知")
            movie_info.setdefault("制片国家/地区", "未知")
            movie_info.setdefault("年份", "未知")

            # 4. 评语
            comment_item_tag = item.find("div", class_="comment-item content")
            if comment_item_tag:
                blockquote_tag = comment_item_tag.find("blockquote", class_="comment")
                if blockquote_tag:
                    comment_text = blockquote_tag.get_text(strip=True).replace("评语：", "").replace("评语:", "")
                    movie_info["评语"] = comment_text if comment_text else "无评语"
                else:
                    movie_info["评语"] = "无评语"
            else:
                movie_info["评语"] = "无评语"

            # 5. 添加日期
            actions_tag = item.find("div", class_="actions")
            if actions_tag:
                time_tag = actions_tag.find("time", class_="time")
                if time_tag:
                    full_time = time_tag.get_text(strip=True)
                    #add_date = full_time.split(" ")[0]
                    add_date = full_time
                    movie_info["添加日期"] = add_date
                else:
                    movie_info["添加日期"] = "未知"
            else:
                movie_info["添加日期"] = "未知"

            # 6. 评分/评价人数
            rating_tag = item.find("div", class_="rating")
            if rating_tag:
                rating_nums_tag = rating_tag.find("span", class_="rating_nums")
                movie_info["评分"] = rating_nums_tag.get_text(strip=True) if rating_nums_tag else "暂无评分"
                people_text = rating_tag.get_text(strip=True)
                people_match = re.search(r'\((\d+)人评价\)', people_text)
                movie_info["评价人数"] = people_match.group(1) if people_match else "暂无评分"
            else:
                movie_info["评分"] = "暂无评分"
                movie_info["评价人数"] = "暂无评分"

            movie_list.append(movie_info)
            print(f"✅ 第{idx}部 | 条目ID：{movie_info['条目ID']} | 中文名：{movie_info['中文片名']} | 评分：{movie_info['评分']} | 评价人数：{movie_info['评价人数']} | 添加日期：{movie_info['添加日期']} | 评语：{movie_info['评语']}")

        # 动态延迟逻辑
        if not is_last_page:
            if not cookie_enabled:
                sleep_time = 1
                print(f"⏳ Cookie 为空，固定休眠 {sleep_time} 秒")
            else:
                if total_pages <= 10:
                    sleep_time = random.uniform(3, 5)
                    print(f"⏳ Cookie 已配置+总页数≤10，随机休眠 {sleep_time:.2f} 秒")
                else:
                    sleep_time = random.uniform(5, 10)
                    print(f"⏳ Cookie 已配置+总页数>10，随机休眠 {sleep_time:.2f} 秒")
            time.sleep(sleep_time)
        else:
            print(f"⏳ 最后一页爬取完成，无需休眠")

        return movie_list

    except requests.exceptions.RequestException as e:
        print(f"❌ 第 {start//25 + 1} 页网络请求错误：{e}")
        return movie_list
    except Exception as e:
        print(f"❌ 第 {start//25 + 1} 页解析错误：{e}")
        return movie_list

def crawl_all_pages():
    """爬取所有分页数据，传递最后一页标记"""
    all_movies = []
    total_items, total_pages = get_total_items()
    start = 0
    while True:
        current_page = start // 25 + 1
        is_last_page = (current_page == total_pages)
        page_movies = crawl_single_page(start, total_pages, is_last_page)
        if not page_movies:
            break
        all_movies.extend(page_movies)
        start += 25

    print(f"\n🎉 爬取完成！累计获取 {len(all_movies)} 部电影信息")
    return all_movies

def save_to_csv(movie_list):
    """
    保存为CSV文件，表头改为「国家/地区」，字段顺序不变
    """
    # 生成时间戳文件名：douban_doulist_YYYYMMDD_HHMMSS.csv
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"douban_doulist_{current_time}.csv"
    
    # 最终CSV表头（制片国家/地区 → 国家/地区），顺序不变
    csv_headers = [
        "条目ID", "中文片名", "原始片名", "年份", "评分",
        "评价人数", "国家/地区", "导演", "添加日期", "评语"
    ]
    # 数据字典键名 与 CSV表头的映射关系
    header_map = {
        "条目ID": "条目ID",
        "中文片名": "中文片名",
        "原始片名": "原始片名",
        "年份": "年份",
        "评分": "评分",
        "评价人数": "评价人数",
        "国家/地区": "制片国家/地区",  # 关键映射
        "导演": "导演",
        "添加日期": "添加日期",
        "评语": "评语"
    }

    try:
        with open(filename, "w", encoding="utf-8-sig", newline='') as f:
            writer = csv.writer(f)
            writer.writerow(csv_headers)  # 写入表头
            
            # 遍历数据，按表头映射提取对应值
            for movie in movie_list:
                row = [movie.get(header_map[col], "") for col in csv_headers]
                writer.writerow(row)
                
        print(f"\n💾 数据已保存到CSV文件：{filename}")
    except Exception as e:
        print(f"❌ 保存CSV失败：{e}")

if __name__ == "__main__":
    # ============ 核心：命令行传参 + 兼容处理 ============
    if len(sys.argv) < 2:
        print("❌ 请传入豆瓣豆列ID/豆列完整URL作为参数！")
        print("✅ 运行格式1（推荐）：python3 本脚本名.py 豆列ID")
        print("✅ 运行格式2：python3 本脚本名.py https://www.douban.com/doulist/豆列ID")
        print("🔍 示例：python3 get_douban_doulist_info.py 160587626")
        sys.exit(1)
    
    # 获取传入的参数
    input_param = sys.argv[1].strip()
    # 正则提取豆列ID，兼容【纯数字】和【完整URL】两种传参方式
    id_match = re.search(r'(\d{6,})', input_param)
    if not id_match:
        print(f"❌ 传入的参数【{input_param}】格式错误！请传入纯数字豆列ID 或 豆瓣豆列完整URL")
        sys.exit(1)
    
    doulist_id = id_match.group(1)
    # 豆列基础URL（不含分页参数）
    DOUBAN_LIST_BASE_URL = f"https://www.douban.com/doulist/{doulist_id}/"
    print(f"\n🚀 开始爬取豆瓣豆列：{DOUBAN_LIST_BASE_URL}")
    
    # 执行爬取+保存
    all_movies = crawl_all_pages()
    if all_movies:
        save_to_csv(all_movies)
