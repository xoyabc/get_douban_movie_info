#!/usr/bin/env python
# -*- coding: utf-8 -*-
#!/usr/bin/python
# -*- coding=utf-8 -*-

import os, sys
from pyquery import PyQuery as pqy

def movie_links_range(year, index):
    base_url="https://movie.douban.com/tag";
    resource_url = "%s/%d?start=%d&type=T" %(base_url, year, index);
    rtree = pqy(url=resource_url);
    items = rtree('.nbg');
    rst_list = [];
    for idx in range(len(items)):
        link = items.eq(idx).attr('href');
        title = items.eq(idx).attr('title').encode("UTF-8");
        rst_list.append((link, title))

    return rst_list

if __name__ == "__main__":

    rst_list = movie_links_range(2018, 10);
    for item in rst_list:
        print "url: %s\ttitle: %s" % (item[0], item[1]);
    sys.exit(0);
