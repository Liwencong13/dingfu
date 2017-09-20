#!/bin/python
#coding=utf8

import json
import sys
reload(sys)
sys.setdefaultencoding('utf8')

if __name__ == '__main__':
    fin = sys.argv[1]
    fout = open(sys.argv[2], 'w')
    res_ls = []
    for line in open(fin, 'r'):
        try:
            one_dic = json.loads(line.strip())
        except:
            continue
        ls = []
        ls.append(one_dic.get('hbase_key', ''))
        for cont in one_dic['content']:
            ls.append(cont.get('content', ''))
        res_ls.append(ls)
        res_ls = sorted(res_ls)
    for ls in res_ls:
        fout.write(json.dumps(ls, ensure_ascii=False) + '\n')