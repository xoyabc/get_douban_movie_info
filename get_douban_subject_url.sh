#!/bin/bash

> douban_subjects
doulist_id="111299960"

total_num=$(curl -s "https://www.douban.com/doulist/${doulist_id}/" |pup '[class="doulist-filter"] a:first-child span text{}' |sed -r 's#\((.*)\)#\1#g')

for i in $(seq 0 25 ${total_num})
do
    # douban tag
    # curl -s "https://movie.douban.com/tag/2018?start=${i}&type=T" -A  'Mozilla/5.0 (Windows NT 6.1; Win64; x64)' |pup '.nbg attr{href}' >> douban_subjects
    # https://movie.douban.com/j/new_search_subjects?sort=T&range=0,10&tags=2019&start=0
    # dou list
    curl -s "https://www.douban.com/doulist/${doulist_id}/?start=${i}&sort=seq&playable=0&sub_type=" -A 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)' |pup '[class="post"] a attr{href}' |awk -F "/" '{print $(NF-1)}' >> douban_subjects
    sleep 1
done
