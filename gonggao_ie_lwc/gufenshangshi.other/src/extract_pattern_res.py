#!/bin/python
#coding=utf8

import json
import sys
reload(sys)
sys.setdefaultencoding('utf8')

def extract_pattern_res(one_dic):
    ls = []
    ls.append(one_dic.get('hbase_key', ''))
    for pattern in one_dic.get('pattern_res', []):
        ls.append(pattern[1]['content'])
    return ls

if __name__ == '__main__':
    fin = sys.argv[1]
    fout = open(sys.argv[2], 'w')
    res_ls = []
    for line in open(fin, 'r'):
        try:
            one_dic = json.loads(line.strip())
        except:
            continue
        ls = extract_pattern_res(one_dic)
        res_ls.append(ls)

    for ls in res_ls:
        fout.write(json.dumps(ls, ensure_ascii=False) + '\n')