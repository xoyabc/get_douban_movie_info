#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os;
import requests;

def printHelloWorld():
    sys.stdout.write("Hello world\n");
    pass

def getMovieDescFromDouban(content_url):
    base_url = "http://api.douban.com"
    req_url = base_url + content_url;
    print "do request: %s" % req_url;
    rsp = requests.get(req_url);
    print "request.url : %s \t status: %d" % (rsp.url, rsp.status_code);

    if rsp.status_code != 200:
        return ; 
    movie_info = rsp.json();
    title = "unknown";
    actors = [];
    rating = 0;
    ratings_count = 0;
    country = ""; language = "";
    out_str = "";

    ##print rsp.json();
    if movie_info.has_key(u"id"):
        out_str += "id : %d\n" % int(movie_info[u"id"]);
    if movie_info.has_key(u"title"):
        title = movie_info[u"title"].encode("UTF-8");
        out_str += "title : %s\n" % title;
    if movie_info.has_key(u"rating"):
        rating = float(movie_info[u"rating"][u"average"]);
        out_str += "rating : %.2f\n" % rating;
    if movie_info.has_key(u"ratings_count"):
        ratings_count = int(movie_info[u"ratings_count"]);
        out_str += "ratings_count : %d\n" % ratings_count;
    if movie_info.has_key(u"countries") and len(movie_info[u"countries"]) > 0:
        country = movie_info[u"countries"][0].encode("UTF-8");
        out_str += "country : %s\n" % country;
    if movie_info.has_key(u"casts") and len(movie_info[u"casts"]) > 0:
        actors = movie_info[u"casts"]; 
        out_str += "actors : ";
        for idx, act in enumerate(actors):
            if idx != 0:
                out_str += ", ";
            out_str += act["name"].encode("UTF-8");

    print out_str;
    ##print "title: " + (rsp.json())["title"].encode('UTF-8');
    return ; 

if __name__ == "__main__":
    printHelloWorld();
    getMovieDescFromDouban("/v2/movie/subject/24751756");
    getMovieDescFromDouban("/v2/movie/subject/1764796");
    ##title = u"\u673a\u5668\u4eba9\u53f7";
    ##print title.encode('UTF-8');
    sys.exit(0);
