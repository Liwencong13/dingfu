#/!bin/python
#coding=utf8

from collections import defaultdict
import json
from database import mongo_op
import probability
import sys
reload(sys)
sys.setdefaultencoding('utf8')

class FreqItem(object):
    def __init__(self, transactions):
        self.transactions = transactions

    def invalid_chars(self, c):
        chars = [u':', u',', u'.', u'!', u'~', u'/', u'?', u'|', u'(', u')', u'[', u']', u'{', u'}', u'-',
                 u'<', u'>', u'"', u" ", u"%",
                 u'，', u'。', u'：', u'【', u'】', u'（', u'）', u'？', u'；', u'《', u'》', u'、', "“", u"”",
                 u'1.', u'2.', u'3.', u'1、', u'2、', u'3、']
        return True if c in chars else False

    def one_order(self):
        hashmap = defaultdict(int)
        for sent in self.transactions:
            _len = len(sent)
            for ii, w in enumerate(sent):
                if self.invalid_chars(w):
                    continue
                hashmap[w] += 1
        return hashmap

    def two_order(self):
        hashmap = defaultdict(int)
        for sent in self.transactions:
            _len = len(sent)
            for ii, w in enumerate(sent):
                if ii < _len - 1:
                    if self.invalid_chars(w) or self.invalid_chars(sent[ii + 1]):
                        continue
                    _tuple = (w, sent[ii + 1])
                    hashmap[_tuple] += 1
        return hashmap

    def three_order(self):
        hashmap = defaultdict(int)
        for sent in self.transactions:
            _len = len(sent)
            for ii, w in enumerate(sent):
                if ii < _len - 2:
                    if self.invalid_chars(w) or self.invalid_chars(sent[ii + 1]) or self.invalid_chars(sent[ii + 2]):
                        continue
                    _tuple = (w, sent[ii + 1], sent[ii + 2])
                    hashmap[_tuple] += 1
        return hashmap


if __name__ == '__main__':
    filename = "/Users/macbook/Desktop/dingfu/output/qa_out.json.match"
    transactions = []
    docs = []
    for line in open(filename):
        doc = []
        dic = json.loads(line.strip())
        doc.append(dic)
        if doc:
            docs.append(doc)
    for doc in docs:
        info = mongo_op.get_info_by_docid("abiao_gonggao_doc", doc[0]['hbase_key'])
        label_paras = []
        for tab_word in info['tab']:
            if tab_word['para_position'] not in label_paras:
                label_paras.append(int(tab_word['para_position']))
        for line in doc[0]['content'][1:]:
            if line.get('__index', -1) in label_paras:
                words = []
                if line.has_key('seg_list'):
                    for seg in line['seg_list']:
                        words.append(seg['value_ori'])
                transactions.append(words)
    # for e in transactions:
    #     print json.dumps(e, ensure_ascii=False)
    fi = FreqItem(transactions)
    one_dic = fi.one_order()
    two_dic = fi.two_order()
    res_dic = probability.mutual_infomation(one_dic, two_dic)
    sorted_dic = sorted(res_dic.items(), lambda x, y: cmp(x[1], y[1]), reverse=True)
    with open('/Users/macbook/Desktop/dingfu/data/new_word_mi_t2.txt', 'w') as fout:
        for t in sorted_dic:
            fout.write(json.dumps(t, ensure_ascii=False) + '\n')