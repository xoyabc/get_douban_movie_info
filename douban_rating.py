#!/usr/bin/env python2
import math
import sys

# ref: https://github.com/luozhaohui/python/blob/master/douban/exportTopMoviesFromDouban.py


minNum = 5
maxNum = 100000
#k = 0.25
k = 0.20
k1 = 0.25
k2 = 0.24
k3 = 0.23
k4 = 0.22
k5 = 0.21


def computeCompositeRating(minNum, maxNum, k, num, people):
    minNum = max(10, min(200, minNum))
    maxNum = max(1000, min(maxNum, 100000))
    people = max(1, min(maxNum, people))
    if people <= minNum:
        people = minNum / 3
    if people <= 5000:
        peopleWeight = math.pow(people, k1)
    elif people <= 10000:
        peopleWeight = math.pow(people, k2)
    elif people <= 20000:
        peopleWeight = math.pow(people, k3)
    elif people <= 30000:
        peopleWeight = math.pow(people, k4)
    elif people <= 50000:
        peopleWeight = math.pow(people, k5)
    else:
        peopleWeight = math.pow(people, k)

 #   print peopleWeight,people

    if people < 200:
        return round((num * 90 + peopleWeight * 10) / 100.0, 2)
    elif people < 500:
        return round((num * 90 + peopleWeight * 10) / 100.0, 2)
    elif people < 1000:
        return round((num * 90 + peopleWeight * 10) / 100.0, 2)
    elif people < 5000:
        return round((num * 90 + peopleWeight * 10) / 100.0, 2)
    elif people < 10000:
        return round((num * 85 + peopleWeight * 15) / 100.0, 2)
    elif people < 20000:
        return round((num * 85 + peopleWeight * 15) / 100.0, 2)
    elif people < 50000:
        return round((num * 90 + peopleWeight * 10) / 100.0, 2)
    else:
        return round((num * 95 + peopleWeight * 5) / 100.0, 2)


#print computeCompositeRating(minNum, maxNum, k, 8, 4000)
#sys.exit(0)

with open('movie_info', 'rU') as f:
    for line in f:
        name = line.split()[0]
        ratingNum = float(line.split()[1])
        ratingPeople = int(line.split()[2])
        weight_num = computeCompositeRating(minNum, maxNum, k, ratingNum, ratingPeople)
        print name, ratingNum, ratingPeople, weight_num
