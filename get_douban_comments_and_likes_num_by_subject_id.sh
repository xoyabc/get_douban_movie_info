#!/bin/bash
> douban_comments
cat movie.list |while read subject_id
do
    curl -s https://movie.douban.com/subject/${subject_id}/ > douban_subject_info
    # short comments number
    num1=$(cat douban_subject_info |pup 'h2 span[class="pl"] a ' |grep -A 1 comments |tail -n 1 |sed -r 's#^.* ([0-9]{1,}) .*$#\1#g')
    # likes number
    num2=$(cat douban_subject_info |pup '[class="subject-others-interests-ft"] a[href]:last-child text{}' |sed -r 's#^([0-9]+).*$#\1#g')
    if [ ! -z ${num1} ]
    then
        comments_num=${num1}
    else
        comments_num="N/A"
    fi
    if [ ! -z ${num2} ]
    then
        likes_num=${num2}
    else
        likes_num="N/A"
    fi
    echo "${subject_id} ${comments_num} ${likes_num}" >> douban_comments
    sleep 1
done
sed -i '1i subject_id comments_num likes_num' douban_comments
