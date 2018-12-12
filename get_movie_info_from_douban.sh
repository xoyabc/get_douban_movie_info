#!/bin/bash
>movie_info
cat movie.list |while read movie
do
    movie_name_urlencode=$(echo "${movie}" |tr -d '\n' | xxd -plain | sed 's/\(..\)/%\1/g')
    query_url="https://api.douban.com/v2/movie/search?q=${movie_name_urlencode}"
    curl -s ${query_url} > douban_api_info
    total=$(cat douban_api_info |jq -r '.total')
    if [ ${total} -gt 0 ]
    then
        movie_genre=$(cat douban_api_info |jq -r '.subjects|.[]|.genres[0]' |head -n 1)
        movie_year=$(cat douban_api_info |jq -r '.subjects' |jq -r '.[]|.year' |head -n 1)
        movie_starring_actor=$(cat douban_api_info |jq -r '.subjects|.[]|.casts[0]|.name' |head -n 1)
        movie_director=$(cat douban_api_info |jq -r '.subjects|.[]|.directors[0]|.name' |head -n 1  )
        movie_subject_id=$(cat douban_api_info |jq -r '.subjects' |jq -r '.[]|.id' |head -n 1)
        echo "${movie};${movie_year};${movie_genre};${movie_starring_actor};${movie_director};${movie_subject_id}" >> movie_info
    else
        echo "${movie};N/A;N/A;N/A;N/A;N/A" >> movie_info
    fi
    sleep 4
done
