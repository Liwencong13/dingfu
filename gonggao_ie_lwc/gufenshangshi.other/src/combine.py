#!/bin/python
#coding=utf8

import json
import sys
reload(sys)
sys.setdefaultencoding('utf8')

ss = ''
ls = []
with open('/Users/macbook/Desktop/dingfu/data/new_word_mi_t2.txt') as fin:
    _count = 1
    for line in fin:
        line = json.loads(line.strip())
        tp = line[0]
        ss = tp[0] + tp[1]
        ls.append(ss)
        if 30 <= _count: break
        _count += 1

with open('/Users/macbook/Desktop/dingfu/data/combine.txt', 'w') as fout:
    for ss in ls:
        fout.write(json.dumps(ss, ensure_ascii=False) + '\n')