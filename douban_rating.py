#!/usr/bin/env python2
# -*- coding:utf-8 -*-
import math
import sys

# ref: 
# https://github.com/luozhaohui/python/blob/master/douban/exportTopMoviesFromDouban.py
# https://www.douban.com/group/topic/1117650/


minNum = 5
maxNum = 500000
#k = 0.25
k = 0.20
k1 = 0.17
k2 = 0.17
k3 = 0.17
k4 = 0.17
k5 = 0.17
k6 = 0.17


def get_weight(people, k, num, index_weight=0.0005):
    peopleWeight = 0
    while peopleWeight < num:
        peopleWeight = math.pow(people, k)
        k += index_weight
    return peopleWeight


def get_w_r(num, people, C=7):
    # (WR) = (v ÷ (v+m)) × R + (m ÷ (v+m)) × C
    # R = 该电影的平均分 
    # v = 该电影的总投票数 
    # m = 列入前250所需要的最少票数(目前是 25000 票) 
    # C = 数据库中所有电影的总平均分(目前是 7.0) 
    R = num
    v = people
    m = 25000
    if num > 9:
        C -= 0.1
    elif num > 8:
        C -= 0.1
    elif num > 7:
        C -= 0.1
    elif num > 6:
        C -= 0.1
    else:
        C -= 0.1
    #print v,m,num,C
    return round((float(v) / (v+m)) * num + (float(m) / (v+m)) * C, 2)


def computeCompositeRating(minNum, maxNum, k, num, people):
    minNum = max(10, min(200, minNum))
    maxNum = max(1000, min(maxNum, 500000))
    people = max(1, min(maxNum, people))
    peopleWeight = 0
    if people <= 5000:
        peopleWeight = get_weight(people, k1, num, 0.0001)
    elif people <= 10000:
        peopleWeight = get_weight(people, k2, num, 0.0001)
    elif people <= 20000:
        peopleWeight = get_weight(people, k2, num, 0.0001)
    elif people <= 40000:
        peopleWeight = get_weight(people, k3, num, 0.0001)
    elif people <= 80000:
        peopleWeight = get_weight(people, k4, num, 0.0001)
    elif people <= 200000:
        peopleWeight = get_weight(people, k5, num, 0.002)
    else:
        #peopleWeight = math.pow(people, k)
        peopleWeight = get_weight(people, k6, num, 0.007)

    print peopleWeight,people

    return get_w_r(num, people, peopleWeight)


with open('movie_info', 'rU') as f:
    for line in f:
        name = line.split()[0]
        ratingNum = float(line.split()[1])
        ratingPeople = int(line.split()[2])
        weight_num = computeCompositeRating(minNum, maxNum, k, ratingNum, ratingPeople)
        print name, ratingNum, ratingPeople, weight_num
