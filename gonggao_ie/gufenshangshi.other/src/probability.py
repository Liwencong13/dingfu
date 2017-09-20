#!/bin/python
#coding=utf8

import math

def mutual_infomation(one_dic, two_dic):
    res_dic = {}
    sum1, sum2 = sum(one_dic.values()), sum(two_dic.values())
    for (k, v) in two_dic.items():
        p_xy = float(v) / sum2
        p_x = float(one_dic[k[0]]) / sum1
        p_y = float(one_dic[k[1]]) / sum1
        res_dic[k] = math.log(p_xy / ((p_x * p_y) + 1e-4), 2)
    return res_dic