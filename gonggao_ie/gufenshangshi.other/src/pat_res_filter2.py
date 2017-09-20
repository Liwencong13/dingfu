#!/bin/python
#coding=utf8

import json
import sys
import copy
from collections import defaultdict
reload(sys)
sys.setdefaultencoding('utf8')

def filter(one_dic):
    mark_dic = {}
    res_dic = copy.deepcopy(one_dic)
    for pattern in one_dic.get('pattern_res', []):
        flag = False
        dic_tmp = pattern[0][0][0][0]
        for (k, v) in dic_tmp.items():
            if not mark_dic.has_key(k):
                mark_dic[k] = 1
            else: flag = True
            break
        if flag:
            res_dic['pattern_res'].remove(pattern)
    return res_dic, mark_dic

def bin_search(lls, key):
    lo, hi = 0, len(lls)-1
    while lo < hi:
        mi = lo + hi >> 1
        if key < lls[mi][0]:
            hi = mi
        elif lls[mi][0] < key:
            lo = mi
        else:
            return mi
    return -1

if __name__ == '__main__':
    fin_pt = sys.argv[1]
    fin_bk = sys.argv[2]
    fout = open(sys.argv[2], 'w')
    # _mark_dic = defaultdict(int)
    bk = []
    for line in open(fin_bk, 'r'):
        bk.append(json.loads(line.strip()))
    for line in open(fin_pt, 'r'):
        try:
            one_dic = json.loads(line.strip())
        except:
            continue
        res_dic, mark_dic = filter(one_dic)
        # for (k, v) in mark_dic.items():
        #     _mark_dic[k] += 1
        pat_nums = len(res_dic['pattern_res'])
        if pat_nums == 3:
            fout.write(json.dumps(res_dic, ensure_ascii=False) + '\n')
        else:
            hb_key = res_dic.get('hbase_key', '')
            ls = []
            for pat in res_dic['pattern_res']:
                idx = bin_search(bk, hb_key)
                if idx != -1:
                    ls = bk[idx]
            for cont in ls:
                pass
    # for (k, v) in _mark_dic.items():
    #     print (k, v)
    fout.close()