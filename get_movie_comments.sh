#!/bin/bash


subject_id="1292270"
FILE="comments.txt"
> ${FILE}

total_num=$(curl -s -A IE  "https://frodo.douban.com/api/v2/movie/${subject_id}/interests?start=0&count=20&status=done&apiKey=054022eaeae0b00e0fc068c0c0a2102a" |jq -r '.total')
page_count=50
page_num=$((${total_num}/${page_count}))

for i in $(seq 0 1 ${page_num})
do
	sleep_time=$(tr -cd 0-2 </dev/urandom | head -c 1)
	curl -s -A IE  "https://frodo.douban.com/api/v2/movie/${subject_id}/interests?start=${i}&count=${page_count}&status=done&apiKey=054022eaeae0b00e0fc068c0c0a2102a" |jq -r '.interests|.[]| "\(.comment) \(.create_time) \(.user.name)"' >> ${FILE}
	sleep ${sleep_time}
done
