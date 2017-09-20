#!/bin/python
#coding=utf8

import json
import sys
import copy
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
    return res_dic

if __name__ == '__main__':
    fin = sys.argv[1]
    fout = open(sys.argv[2], 'w')
    for line in open(fin, 'r'):
        try:
            one_dic = json.loads(line.strip())
        except:
            continue
        res_dic = filter(one_dic)
        fout.write(json.dumps(res_dic, ensure_ascii=False) + '\n')
    fout.close()