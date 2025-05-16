#!/bin/bash

FILE="2025-SIFF.md"
> ${FILE}

dos2unix movie.csv

# title and base info
total_num=$(awk 'END{print NR-1}' movie.csv)
echo "# **第27届上海国际电影节展映片单**
- **基本信息**
  - 制作：vow
  - 数据来源：FrankZSPD 所建豆列
  - 豆列链接：https://www.douban.com/doulist/161440092" >> ${FILE}
echo -e "  - 总影片数：${total_num}部\n" >> ${FILE}


cat movie.csv |awk -F ',' 'NR>1{print $1}' |uniq |while read unit
do
    unit_num=$(cat movie.csv |grep "${unit}" |wc -l)
    echo "- **${unit}（${unit_num}部）**" >> ${FILE}
    cat movie.csv |grep "${unit}" |sort -t ',' -k7,7rn -k5,5n |grep -Ev "暂无评分|尚未上映|尚未播出" |awk -F "," '{print "  - 《"$4"》（"$5"年，"$9"，"$14"，"$7"分）"}' >> ${FILE}
    cat movie.csv |grep "${unit}" |sort -t ',' -k7,7rn -k5,5n |grep -E "尚未上映|尚未播出|暂无评分" |awk -F "," '{print "  - 《"$4"》（"$5"年，"$9"，"$14"，"$7"）"}' >> ${FILE}
done
