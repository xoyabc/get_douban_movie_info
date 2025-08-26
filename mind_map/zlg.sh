#!/bin/bash

FILE=${1:-movie-zlg.csv}
OUT_FILE=$(echo ${FILE} |sed 's#.csv##g' |awk '{print $1".md"}')
dos2unix ${FILE}
> ${OUT_FILE}

if [ $# -lt 1 ]
then
	echo -e "Usage: \nbash zlg.sh movie-zlg.csv\nbash zlg.sh movie-jnfg.csv"
	exit 2
fi

# title
if [ $1 = "movie-jnfg.csv" ]
then
echo "# 2025.05 江南分馆日常放映片单  
## 基本信息
 - 数据来源：特工队头目 所建豆列
 - 制作：vow" >> ${OUT_FILE}
else
echo "# 2025.05 资料馆日常放映片单  
## 基本信息
 - 数据来源：葡萄冰 所建豆列
 - 制作：vow" >> ${OUT_FILE}
fi

total_num=$(awk 'END{print NR-1}' ${FILE})
not_play_num=$(cat ${FILE} |awk -F "," 'NR>1 && $2=="否"{count++} END {print count}')
no_and_copyright_num=$(cat ${FILE} |awk -F "," 'NR>1 && $2=="否" && $3!=""{count++} END {print count}')
no_and_not_copyright_num=$(cat ${FILE} |awk -F "," 'NR>1 && $2=="否" && $3==""{count++} END {print count}')
no_and_director_num=$(cat ${FILE} |awk -F "," 'NR>1 && $2=="否" && $3==""{num[$8]++}END{for(i in num) print num[i],i}' |sort -nr |awk '$1>1{sum+=$1}END{print sum+0}')
yes_play_num=$(cat ${FILE} |awk -F "," 'NR>1 && $2!="否"{count++} END {print count}')
yes_and_copyright_num=$(cat ${FILE} |awk -F "," 'NR>1 && $2!="否" && $3!=""{count++} END {print count}')
yes_and_not_copyright_num=$(cat ${FILE} |awk -F "," 'NR>1 && $2!="否" && $3==""{count++} END {print count}')
yes_and_director_num=$(cat ${FILE} |awk -F "," 'NR>1 && $2!="否" && $3==""{num[$8]++}END{for(i in num) print num[i],i}' |sort -nr |awk '$1>1{sum+=$1}END{print sum+0}')

dup_percent=$(echo ${yes_play_num} ${total_num} |awk '{printf"%d%",$1/$2*100}')

# dup statistic
echo " - 影片总数：${total_num}部，其中 ${yes_play_num} 部 22-24 年放过，重复率：${dup_percent}" >> ${OUT_FILE}

# 未放过
echo -e "\n## 一、22-24年未放过影片（${not_play_num}部）" >> ${OUT_FILE}
# 未放过，有版代
echo "### （一）有版代影片（${no_and_copyright_num}部）" >> ${OUT_FILE}
cat ${FILE} |awk -F "," 'NR>1 && $2=="否" && $3!=""{num[$3]++}END{for(i in num) print num[i],i}' |sort -nr |while read line
do
	num=$(echo ${line} |awk '{print $1}')
	name=$(echo ${line} |awk '{print $2}')
	echo "#### **${name}（${num}部）** " >> ${OUT_FILE}
	cat ${FILE} |awk -F "," 'NR>1 && $2=="否" && $3!=""' |grep "${name}" |sort -t ',' -k5,5rn -k4,4n |grep -Ev "暂无评分|尚未上映|尚未播出" |awk -F "," '{print "   - 《"$1"》（"$4"年，"$7"，"$8"，"$5"分）"}' >> ${OUT_FILE}
	cat ${FILE} |awk -F "," 'NR>1 && $2=="否" && $3!=""' |grep "${name}" |sort -t ',' -k5,5rn -k4,4n |grep -E "暂无评分|尚未上映|尚未播出" |awk -F "," '{print "   - 《"$1"》（"$4"年，"$7"，"$8"，"$5"）"}' >> ${OUT_FILE}
done

# 未放过，无版代
echo -e "\n### （二）无版代影片（${no_and_not_copyright_num}部）" >> ${OUT_FILE}
# 未放过，无版代，导演分组
# 需满足导演作品 >=2
if [ ${no_and_director_num} -ge 1 ]
then
echo "#### **导演分组（${no_and_director_num}部，≥2部）**" >> ${OUT_FILE}
cat ${FILE} |awk -F "," 'NR>1 && $2=="否" && $3==""{num[$8]++}END{for(i in num) print num[i],i}' |sort -nr |awk '$1>1' |while read line
do
	num=$(echo ${line} |awk '{print $1}')
	director=$(echo ${line} |awk '{print $2}')
	echo "   - **${director}（${num}部）** " >> ${OUT_FILE}
	cat ${FILE} |awk -F "," 'NR>1' |sort -t ',' -k5,5rn -k4,4n |awk -F "," -v dr="${director}"  '$2=="否" && $3=="" && $8==dr' |grep -Ev "暂无评分|尚未上映|尚未播出" |awk -F "," '{print "     - 《"$1"》（"$4"年，"$7"，"$5"分）"}' >> ${OUT_FILE}
	cat ${FILE} |awk -F "," 'NR>1' |sort -t ',' -k5,5rn -k4,4n |awk -F "," -v dr="${director}"  '$2=="否" && $3=="" && $8==dr' |grep -E "暂无评分|尚未上映|尚未播出" |awk -F "," '{print "     - 《"$1"》（"$4"年，"$7"，"$5"）"}' >> ${OUT_FILE}
done
fi

# 未放过，无版代，国家分组 ≥2部
no_director_name=$(cat ${FILE} |awk -F "," 'NR>1 && $2=="否" && $3==""{num[$8]++}END{for(i in num) print num[i],i}' |sort -nr |awk '$1>1{print $2}' |tr '\n' '|' |sed 's/.$//') 
no_and_ctry_num=$(cat ${FILE} |awk -F "," 'NR>1' |sort -t ',' -k5,5rn -k4,4n |awk -F "," -v dr="${no_director_name}" '($2=="否" && $3=="" && dr == "") || ($2=="否" && $3=="" && $8 !~ dr){count++} END {print count}')
echo "#### **国家/地区分组（${no_and_ctry_num}部，按数量降序）** " >> ${OUT_FILE}
cat ${FILE} |awk -F "," 'NR>1' |sort -t ',' -k5,5rn -k4,4n |awk -F "," -v dr="${no_director_name}" '($2=="否" && $3=="" && dr == "") || ($2=="否" && $3=="" && $8 !~ dr)' > no_and_ctry
cat no_and_ctry |awk -F "," '{num[$7]++}END{for(i in num) print num[i],i}' |sort -nr |awk '$1>1' |while read line
do
	num=$(echo ${line} |awk '{print $1}')
	country=$(echo ${line} |awk '{print $2}')
	echo "   - **${country}（${num}部）** " >> ${OUT_FILE}
	cat no_and_ctry |awk -F "," -v ctry="${country}"  '$7==ctry' |grep -Ev "暂无评分|尚未上映|尚未播出" |awk -F "," '{print "     - 《"$1"》（"$4"年，"$8"，"$5"分）"}' >> ${OUT_FILE}
	cat no_and_ctry |awk -F "," -v ctry="${country}"  '$7==ctry' |grep -E "暂无评分|尚未上映|尚未播出" |awk -F "," '{print "     - 《"$1"》（"$4"年，"$8"，"$5"）"}' >> ${OUT_FILE}
done

# 未放过，无版代，国家分组 <2 部
no_and_other_ctry_num=$(cat no_and_ctry |awk -F "," '{num[$7]++}END{for(i in num) print num[i],i}' |sort -nr |awk '$1==1{count++} END {print count}')
no_and_other_ctry_name=$(cat no_and_ctry |awk -F "," '{num[$7]++}END{for(i in num) print num[i],i}' |sort -nr |awk '$1==1{print $2}' |tr '\n' '|' |sed 's/.$//')
echo "   - **其他（${no_and_other_ctry_num}部）** " >> ${OUT_FILE}
cat no_and_ctry |grep -Ew "${no_and_other_ctry_name}" |awk -F "," -v ctry="${no_and_other_ctry_name}"  '$7 ~ ctry' |grep -Ev "暂无评分|尚未上映|尚未播出" |awk -F "," '{print "     - 《"$1"》（"$4"年，"$7"，"$8"，"$5"分）"}' >> ${OUT_FILE}
cat no_and_ctry |grep -Ew "${no_and_other_ctry_name}" |awk -F "," -v ctry="${no_and_other_ctry_name}"  '$7 ~ ctry' |grep -E "暂无评分|尚未上映|尚未播出" |awk -F "," '{print "     - 《"$1"》（"$4"年，"$7"，"$8"，"$5"）"}' >> ${OUT_FILE}

# ********************分割线***************************
# 放过
echo -e "\n## 二、22-24年放过影片（${yes_play_num}部）" >> ${OUT_FILE}
# 放过，有版代
echo "### （一）有版代影片（${yes_and_copyright_num}部）" >> ${OUT_FILE}
cat ${FILE} |awk -F "," 'NR>1 && $2!="否" && $3!=""{num[$3]++}END{for(i in num) print num[i],i}' |sort -nr |while read line
do
	num=$(echo ${line} |awk '{print $1}')
	name=$(echo ${line} |awk '{print $2}')
	echo "#### **${name}（${num}部）** " >> ${OUT_FILE}
	cat ${FILE} |awk -F "," 'NR>1 && $2!="否" && $3!=""' |grep "${name}" |sort -t ',' -k5,5rn -k4,4n |grep -Ev "暂无评分|尚未上映|尚未播出" |awk -F "," '{print "   - 《"$1"》（"$4"年，"$7"，"$8"，"$5"分）"}' >> ${OUT_FILE}
	cat ${FILE} |awk -F "," 'NR>1 && $2!="否" && $3!=""' |grep "${name}" |sort -t ',' -k5,5rn -k4,4n |grep -E "暂无评分|尚未上映|尚未播出" |awk -F "," '{print "   - 《"$1"》（"$4"年，"$7"，"$8"，"$5"）"}' >> ${OUT_FILE}
done

# 放过，无版代
echo -e "\n### （二）无版代影片（${yes_and_not_copyright_num}部）" >> ${OUT_FILE}
# 放过，无版代，导演分组
# 需满足导演作品 >=2
if [ ${yes_and_director_num} -ge 1 ]
then
echo "#### **导演分组（${yes_and_director_num}部，≥2部）**" >> ${OUT_FILE}
cat ${FILE} |awk -F "," 'NR>1 && $2!="否" && $3==""{num[$8]++}END{for(i in num) print num[i],i}' |sort -nr |awk '$1>1' |while read line
do
	num=$(echo ${line} |awk '{print $1}')
	director=$(echo ${line} |awk '{print $2}')
	echo "   - **${director}（${num}部）** " >> ${OUT_FILE}
	cat ${FILE} |awk -F "," 'NR>1' |sort -t ',' -k5,5rn -k4,4n |awk -F "," -v dr="${director}"  '$2!="否" && $3=="" && $8==dr' |grep -Ev "暂无评分|尚未上映|尚未播出" |awk -F "," '{print "     - 《"$1"》（"$4"年，"$7"，"$5"分）"}' >> ${OUT_FILE}
	cat ${FILE} |awk -F "," 'NR>1' |sort -t ',' -k5,5rn -k4,4n |awk -F "," -v dr="${director}"  '$2!="否" && $3=="" && $8==dr' |grep -E "暂无评分|尚未上映|尚未播出" |awk -F "," '{print "     - 《"$1"》（"$4"年，"$7"，"$5"）"}' >> ${OUT_FILE}
done
fi

# 放过，无版代，国家分组 ≥2部
yes_director_name=$(cat ${FILE} |awk -F "," 'NR>1 && $2!="否" && $3==""{num[$8]++}END{for(i in num) print num[i],i}' |sort -nr |awk '$1>1{print $2}' |tr '\n' '|' |sed 's/.$//') 
yes_and_ctry_num=$(cat ${FILE} |awk -F "," 'NR>1' |sort -t ',' -k5,5rn -k4,4n |awk -F "," -v dr="${yes_director_name}" '($2!="否" && $3=="" && dr == "") || ($2!="否" && $3=="" && $8 !~ dr){count++} END {print count}')

echo "#### **国家/地区分组（${yes_and_ctry_num}部，按数量降序）** " >> ${OUT_FILE}
cat ${FILE} |awk -F "," 'NR>1' |sort -t ',' -k5,5rn -k4,4n |awk -F "," -v dr="${yes_director_name}" '($2!="否" && $3=="" && dr == "") || ($2!="否" && $3=="" && $8 !~ dr)' > yes_and_ctry
cat yes_and_ctry |awk -F "," '{num[$7]++}END{for(i in num) print num[i],i}' |sort -nr |awk '$1>1' |while read line
do
	num=$(echo ${line} |awk '{print $1}')
	country=$(echo ${line} |awk '{print $2}')
	echo "   - **${country}（${num}部）** " >> ${OUT_FILE}
	cat yes_and_ctry |awk -F "," -v ctry="${country}"  '$7==ctry' |grep -Ev "暂无评分|尚未上映|尚未播出" |awk -F "," '{print "     - 《"$1"》（"$4"年，"$8"，"$5"分）"}' >> ${OUT_FILE}
	cat yes_and_ctry |awk -F "," -v ctry="${country}"  '$7==ctry' |grep -E "暂无评分|尚未上映|尚未播出" |awk -F "," '{print "     - 《"$1"》（"$4"年，"$8"，"$5"）"}' >> ${OUT_FILE}
done

# 放过，无版代，国家分组 <2 部
yes_and_other_ctry_num=$(cat yes_and_ctry |awk -F "," '{num[$7]++}END{for(i in num) print num[i],i}' |sort -nr |awk '$1==1{count++} END {print count}')
yes_and_other_ctry_name=$(cat yes_and_ctry |awk -F "," '{num[$7]++}END{for(i in num) print num[i],i}' |sort -nr |awk '$1==1{print $2}' |tr '\n' '|' |sed 's/.$//')
echo "   - **其他（${yes_and_other_ctry_num}部）** " >> ${OUT_FILE}
cat yes_and_ctry |awk -F "," -v ctry="${yes_and_other_ctry_name}"  '$7 ~ ctry' |grep -Ev "暂无评分|尚未上映|尚未播出" |awk -F "," '{print "     - 《"$1"》（"$4"年，"$7"，"$8"，"$5"分）"}' >> ${OUT_FILE}
cat yes_and_ctry |awk -F "," -v ctry="${yes_and_other_ctry_name}"  '$7 ~ ctry' |grep -E "暂无评分|尚未上映|尚未播出" |awk -F "," '{print "     - 《"$1"》（"$4"年，"$7"，"$8"，"$5"）"}' >> ${OUT_FILE}

# delete tmp file
rm -f no_and_ctry
rm -f yes_and_ctry
