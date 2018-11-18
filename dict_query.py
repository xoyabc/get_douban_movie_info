#!/usr/bin/env python
# -*- coding:utf-8 -*-
import re  
import os
import json
import requests
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.117 Safari/537.36'
        }
##print url
#r = requests.get(url, headers=headers)
#data = r.text.encode('utf-8')
#dict_data = json.loads(data)
#word_means_list = dict_data['symbols'][0]['parts']

def request_word_url(url):
    r = requests.get(url, headers=headers)
    data = r.text.encode('utf-8')
    dict_data = json.loads(data)
    word_means_list = dict_data['symbols'][0]['parts']
    #print word_means_list
    return word_means_list
        
def get_word_means(word_means_list):
    word_list = []
    for word in word_means_list:
        word_means = word['means'][0]
        word_list.append(word_means)
    return " ".join(word_list)

def get_chs_means():
    with open('country.list','rU') as f:
        for line in f:
            word=line.strip().lower()
            url = 'http://dict-co.iciba.com/api/dictionary.php?key=2CE8F2C9798FC13008D79E5A61F8FCE8&type=json&w={0}' .format(word)
            try:
                word_means_list = request_word_url(url)
                print '{0} {1}' .format(word,get_word_means(word_means_list))
            except Exception as err:
                print "{0} error" .format(word)

if __name__ == '__main__':
    #get_word_means()
    get_chs_means()
