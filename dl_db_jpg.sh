#!/bin/bash

> download.log

[ ! -d pic_dir ] && mkdir pic_dir

#cat urls.txt | xargs -P 50 -n 1 wget --timeout=10 --tries=1 -Nq -P ./pic_dir --show-progress
#cat urls.txt | xargs -P 50 -n 1 wget --timeout=10 --tries=1 -N -P ./pic_dir -nv -a download.log

cat urls.txt | xargs -P 50 -n 1 sh -c 'echo "Downloading: $1" >> download.log && wget --timeout=5 --tries=1 --retry-on-http-error=500,502,503,504 -Nq -P ./pic_dir "$1" >> download.log 2>> download.log || echo "FAILED: $1" >> download.log' sh 
