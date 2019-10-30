#!/bin/bash

> douban_subjects
doulist_id="817584"

for i in $(seq 0 25 100)
do
    # douban tag
    # curl -s "https://movie.douban.com/tag/2018?start=${i}&type=T" -A  'Mozilla/5.0 (Windows NT 6.1; Win64; x64)' |pup '.nbg attr{href}' >> douban_subjects
    # dou list
    curl -s "https://www.douban.com/doulist/${doulist_id}/?start=${i}&sort=seq&playable=0&sub_type=" -A 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)' |pup '[class="post"] a attr{href}' |awk -F "/" '{print $(NF-1)}' >> douban_subjects
    sleep 1
done
