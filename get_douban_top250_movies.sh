#!/bin/bash
# **********************************************************
# * Author        : xoyabc
# * Email         : lxh1031138448@gmail.com
# * Last modified : 2019-10-02 20:58
# * Filename      : get_douban_top250_movies.sh
# * Description   : 
# **********************************************************

TEMP_DIR="temp"
TEMP_MV_INFO="douban_mv_info"
URL="${TEMP_DIR}/url"
NAME="${TEMP_DIR}/name"
YEAR="${TEMP_DIR}/year"
REGION="${TEMP_DIR}/region"
GENRE="${TEMP_DIR}/genre"
DIRECTOR="${TEMP_DIR}/director"
RATING_SCORE="${TEMP_DIR}/rating_score"
RATING_NUM="${TEMP_DIR}/rating_num"

RESULT_FILE="top250_movies.csv"

[ ! -d ${TEMP_DIR} ] && mkdir ${TEMP_DIR}
>${URL} && >${NAME} && >${YEAR} && >${REGION} && >${GENRE} && >${DIRECTOR} && >${RATING_SCORE} && >${RATING_NUM}

for i in $(seq 0 25 225)
do
	link="https://movie.douban.com/top250?start=${i}&filter="
	curl -s "${link}" > ${TEMP_MV_INFO}
	# URL
	cat ${TEMP_MV_INFO} |pup 'div[class="hd"] a attr{href}' >> ${URL}
	# other ways
	#cat douban_mv_info |pup 'div[class="hd"] json{}' |jq -r '.[]|.children|.[]|select(.href != null) |.href'
	#cat douban_mv_info |pup 'div[class="hd"] json{}' |jq -r '.[]|.children[0]|.href'
	
	# movie name
	cat ${TEMP_MV_INFO} |pup 'div[class="hd"] json{}' |jq -r '.[]|.children|.[]|select(.children != null)|.children[0]|.text' >> ${NAME}
	
	# year
	cat ${TEMP_MV_INFO} |sed 's#&nbsp;##g' |pup 'div[class="bd"] p[class=""] text{}' |awk --posix -F "/" '!/^[[:space:]]+$/ && !/^$/ && /[0-9]{4}/ { sub(/^[[:blank:]]*/,"",$1);sub(/\(.*\)/,"",$1);print $1 }' >> ${YEAR}
	
	# region
	cat ${TEMP_MV_INFO} |sed 's#&nbsp;##g' |pup 'div[class="bd"] p[class=""] text{}' |awk --posix -F "/" '!/^[[:space:]]+$/ && !/^$/ && /[0-9]{4}/ { print $(NF-1)}' >> ${REGION}
	
	# genre
	cat ${TEMP_MV_INFO} |sed 's#&nbsp;##g' |pup 'div[class="bd"] p[class=""] text{}' |awk --posix -F "/" '!/^[[:space:]]+$/ && !/^$/ && /[0-9]{4}/ { print $NF}' >> ${GENRE}
	
	# director
	cat ${TEMP_MV_INFO} |pup 'div[class="bd"] p[class=""] text{}' |awk --posix -F "[/ ]+" '!/^[[:space:]]+$/ && !/^$/ && !/[0-9]{4}/{print $3}'  >> ${DIRECTOR}
	
	# rating_score
	cat ${TEMP_MV_INFO} |pup 'div[class="star"] span[property="v:average"] text{}' >> ${RATING_SCORE}
	
	# rating_num
	cat ${TEMP_MV_INFO} |pup 'div[class="star"] span:last-child text{}' |grep -Eo '[0-9]{1,}' >> ${RATING_NUM}
done

paste -d ',' ${NAME} ${YEAR} ${REGION} ${GENRE} ${DIRECTOR} ${RATING_SCORE} ${RATING_NUM} ${URL} > ${RESULT_FILE}
# 添加表头
sed -i '1i 片名,年份,制片国家/地区,类型,导演,评分,评价人数,链接' ${RESULT_FILE}
iconv -f utf8 -t gb18030 ${RESULT_FILE} -o ${RESULT_FILE}