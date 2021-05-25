#!/bin/bash

# download newest title.ratings.tsv
wget -Nq https://datasets.imdbws.com/title.ratings.tsv.gz
gzip -f -d title.ratings.tsv.gz
IMDB_TT_RATING_FILE="title.ratings.tsv"
IMDB_TITLE_FILE="imdb_title"
IMDB_RATING_FILE="imdb_rating"

> ${IMDB_RATING_FILE}

cat ${IMDB_TITLE_FILE} |while read line
do
        if [ $(cat ${IMDB_TT_RATING_FILE} |grep ${line} |wc -l) -ge 1 ]
        then
                rating=$(cat ${IMDB_TT_RATING_FILE} |grep -w ${line} |awk '{print $2}')
                numvotes=$(cat ${IMDB_TT_RATING_FILE} |grep -w ${line} |awk '{print $3}')
        else
                rating="N/A"
                numvotes="N/A"
        fi
        echo "${rating} ${numvotes}" >> ${IMDB_RATING_FILE}
done

