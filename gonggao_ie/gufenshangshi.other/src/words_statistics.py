#!/bin/python
#coding=utf8

import mongo_op
import sys
import json

reload(sys)
sys.setdefaultencoding('utf8')

filepath = "/Users/macbook/Desktop/dingfu/output/qa_out.json.match"
file = open(filepath)
docs = []
for line in file:
    doc = []
    dic = json.loads(line.strip())
    doc.append(dic)
    if doc:
        docs.append(doc)

res = []
b = 0
for doc in docs:
    print "doc: " + doc[0]['hbase_key']
    info = mongo_op.get_info_by_docid("abiao_gonggao_doc", doc[0]['hbase_key'])
    para_position = []
    text_position = []
    for tab_word in info['tab']:
        para_position.append(tab_word['para_position'])
        text_position.append(tab_word['text_position'])
    print para_position
    print text_position
    for ii, para in enumerate(para_position):
        for line in doc[0]['content'][1:]:
            if line.get('__index', -1) == int(para):
                _offset = line.get('__content_offset', 0)
                ss = ''
                _count = 0
                if line.has_key('seg_list'):
                    for seg in line['seg_list']:
                        _len = len(ss.decode('utf8')) - _count + _offset
                        if _len == text_position[ii]:
                            continue
                        ss += seg['value_ori']
                        ss += "_"
                        _count += 1
                if 2 == b:
                    res.append(ss)
    b += 1
    if 3 <= b: break
for e in res:
    print json.dumps(e, ensure_ascii=False)