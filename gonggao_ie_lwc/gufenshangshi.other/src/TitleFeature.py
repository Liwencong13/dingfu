#!/bin/python
# coding=utf8

# 添加标题层级
# 添加页码判断特征

from Utils import Utils
from PatternEngine import PatternEngine
from collections import defaultdict
import re
import sys
import time
import json
import copy
import time
import codecs
import logging

reload(sys)
sys.setdefaultencoding('utf8')


class TitleFeature(object):
    def __init__(self):
        self.split_set = set([',', ':', ';', '?', '!', u'，', u'：', u'；', u'？', u'！', u'。'])
        self.pat_ls = None
        self.title_dic = {}
        #		self.punc_pat = re.compile(u'[:：;；。，,!！《》？?]')
        self.punc_pat = re.compile(u'[!！？?]')
        self.page_num_pat = re.compile('(\d{1,3}.?$)')
        self.not_num_pat = re.compile(u'[，、,。.:：]')
        self.pat_eng = PatternEngine()

    def load_hierachy_pattern(self, cfg_name='hierachy_pattern.cfg'):
        class_num = 0
        res_dic = {}
        for line in codecs.open(cfg_name, 'r', 'utf8'):
            ln = line.strip()
            if not ln:
                class_num += 1
                continue
            res_dic[ln] = class_num
        return res_dic

    def load_title_pat_ls(self):
        pat0 = {'pattern': [{'key_type': '^', 'type': '^', 'key': '^'}, \
                            {'key_type': 'tag', 'type': 'require', 'key': '<numpure>'}, \
                            {'key_type': 'text', 'type': 'require', 'key': u'、'}], \
                'rule': [{'num': [1, 2]}]}
        pat1 = {'pattern': [{'key_type': '^', 'type': '^', 'key': '^'}, \
                            {'key_type': 'text', 'type': 'require', 'key': u'第'}, \
                            {'key_type': 'tag', 'type': 'require', 'key': '<numpure>'}, \
                            {'key_type': 'text', 'type': 'require', 'key': u'节'}], \
                'rule': [{'num': [1, 2, 3]}]}
        pat2 = {'pattern': [{'key_type': '^', 'type': '^', 'key': '^'}, \
                            {'key_type': 'text', 'type': 'require', 'key': u'第'}, \
                            {'key_type': 'tag', 'type': 'require', 'key': '<numpure>'}, \
                            {'key_type': 'text', 'type': 'require', 'key': u'章'}], \
                'rule': [{'num': [1, 2, 3]}]}
        pat3 = {'pattern': [{'key_type': '^', 'type': '^', 'key': '^'}, \
                            {'key_type': 'text', 'type': 'require', 'key': u'('}, \
                            {'key_type': 'tag', 'type': 'require', 'key': '<numpure>'}, \
                            {'key_type': 'text', 'type': 'require', 'key': u')'}], \
                'rule': [{'num': [1, 2, 3]}]}
        pat4 = {'pattern': [{'key_type': '^', 'type': '^', 'key': '^'}, \
                            {'key_type': 'text', 'type': 'require', 'key': u'§'}, \
                            {'key_type': 'tag', 'type': 'require', 'key': '<numpure>'}], \
                'rule': [{'num': [1, 2]}]}
        pat9 = {'pattern': [{'key_type': '^', 'type': '^', 'key': '^'}, \
                            {'key_type': 'tag', 'type': 'require', 'key': '<numpure>'}], \
                'rule': [{'num': [1]}]}
        pat_ls = [pat0, pat1, pat2, pat3, pat4, pat9]
        # pat_ls = [pat0, pat1, pat2, pat3, pat4]
        return pat_ls

    def is_page_num(self, content_dic, y_thrd=100.0):
        page_num_pat, not_num_pat = self.page_num_pat, self.not_num_pat
        content, index = content_dic['content'], content_dic['index']
        y_axis = float(index.split('_')[-1])
        if y_axis < y_thrd and len(content) < 10 and not re.search(not_num_pat, content) and re.search(page_num_pat,
                                                                                                       content):
            return True
        else:
            return False

    def page_num_filter(self, content_dic_ls, y_thrd=100.0):
        page_num_pat, not_num_pat = self.page_num_pat, self.not_num_pat
        cur_page, pre_page = 0, 1
        res_set = set()
        for ind, content_dic in enumerate(content_dic_ls):
            index = content_dic['index']
            page, y_axis = index.split('_')
            cur_page, y_axis = int(page), float(y_axis)
            if cur_page > pre_page:
                pre_page = cur_page
                # 记录page下标
                if is_page_num(content_dic_ls[ind - 1], page_num_pat, not_num_pat):
                    res_set.add(ind - 1)
                    # logging.debug(content_dic_ls[ind-1]['content'])
        if is_page_num(content_dic_ls[-1], page_num_pat, not_num_pat):
            res_set.add(ind - 1)
        # logging.debug(content_dic_ls[ind-1]['content'])
        return res_set

    def compute_title_level(self, parsed_ls, title_dic):
        # 层级构建
        prev_class, cur_class, cur_level, class_dic, title_set = -2, -1, 0, {}, set()
        title_level = []
        for ind, cur_ls in enumerate(parsed_ls):
            try:
                content, title = cur_ls[1:3]
            except:
                continue
            cur_class = title_dic.get(title, -1)
            if title not in title_dic:
                continue
            if cur_class == prev_class:
                pass
            else:
                title_set = set([ss for ss in title_set if title_dic[ss] != prev_class])
                if cur_class not in class_dic:
                    class_dic[cur_class] = cur_level + 1
                    title_set.update([ss for ss in title_dic.keys() if title_dic[ss] == cur_class])
                else:
                    tmp_level = class_dic[cur_class]
                    if tmp_level == cur_level:
                        tmp_level += 1
                    class_dic[cur_class] = tmp_level
                    title_set.update([ss for ss in title_dic.keys() if title_dic[ss] == cur_class])
            # title_set.add(title)
            prev_class = cur_class
            cur_level = class_dic[cur_class]
            title_level.append((cur_ls[0], cur_level))
        return title_level

    def print_contents(self, one_dic):
        if not one_dic or not one_dic.get('content', None):
            return
        cur_index, prev_index, cont = '', one_dic['content'][0]['index'], one_dic['content'][0]['content']
        for content_dic in one_dic['content']:
            cur_index = content_dic['index']
            if cur_index != prev_index:
                print cont.strip()
                cont = ''
            prev_index = cur_index
            cont += content_dic['content']

    def filter_titles(self, init_title_res, content_ls, title_dic):
        # 过滤页码
        # 过滤投票
        punc_pat = self.punc_pat
        title_res = []
        # 段落必须为一句
        # punc_pat = re.compile(u'[:：;；。，,!！《》？?]')
        if init_title_res:
            for title_ls in init_title_res:
                ind, cont = title_ls[0:2]
                cont = cont.strip()
                if ind == 0 or ind == len(content_ls) - 1 or len(cont) < 3:
                    continue
                if (len(cont) > 21 and not re.search(punc_pat, cont[3:len(cont) - 7])) or \
                        (len(cont) <= 21 and (
                            not re.search(punc_pat, cont[3:len(cont) - 2]) or (not re.search(punc_pat, cont[3:])))):
                    cur_index, pre_index, next_index = content_ls[ind]['index'], content_ls[ind - 1]['index'], \
                                                       content_ls[ind + 1]['index']
                    if pre_index == cur_index or cur_index == next_index:
                        continue
                    else:
                        title_res.append(title_ls)
        if len(title_res) < 2:
            return title_res
        print 'middle_res'
        print '\n'.join([json.dumps(tup, ensure_ascii=False) for tup in title_res])
        # 去除连续为标题且为同一类型的情况
        fin_res, flag = [], [-1 for tt in title_res]
        for ind, tlt in enumerate(title_res[1:len(title_res) - 1], 1):
            if flag[ind] != -1:
                continue
            ind_1, ind0, ind1, typ_1, typ0, typ1 = title_res[ind - 1][0], title_res[ind][0], title_res[ind + 1][0], \
                                                   title_res[ind - 1][-1], title_res[ind][-1], title_res[ind + 1][-1]
            if ind0 == ind1 - 1 and title_dic.get(typ0, 0) == title_dic.get(typ1, 1):
                flag[ind] = 0
                flag[ind + 1] = 0
            elif ind_1 == ind0 - 1 and title_dic.get(typ_1, 0) == title_dic.get(typ0, 1):
                flag[ind] = 0
                flag[ind - 1] = 0
            else:
                flag[ind] = 1
        # print flag
        if flag[0] == -1 and title_res[0][0] + 1 == title_res[1][0] and title_dic.get(title_res[0][-1],
                                                                                      0) == title_dic.get(
                title_res[1][-1], 1):
            flag[0] = 0
        else:
            flag[0] = 1
        if flag[-1] == -1 and title_res[-1][0] - 1 == title_res[-2][0] and title_dic.get(title_res[-1][-1],
                                                                                         0) == title_dic.get(
                title_res[-2][-1], 1):
            flag[-1] = 0
        else:
            flag[-1] = 1
        # print json.dumps(flag)
        fin_res = [title_res[ind] for ind, ii in enumerate(flag) if ii == 1]
        return fin_res

    def title_extraction_single(self, dic, pat_ls):
        # 获取分词打标结果
        one_res = []
        pkey, content = dic.get('key', ' '), dic.get('content', '')
        for ind, tmp_dic in enumerate(content):
            # tmp_dic['is_title'] = False
            if 'seg_list' not in tmp_dic:
                continue
            # if len(tmp_dic['content']) > 50*3 or re.search(u'。|《|"|:', tmp_dic['content']):
            if len(tmp_dic['content']) > 50 * 3 or re.search(u'。|"', tmp_dic['content']):
                continue
            parse_res, tmp_set = [], set()
            for pat in pat_ls:
                tmp_res = self.pat_eng.parse_one_pattern(pat, tmp_dic)
                if tmp_res:
                    ss = json.dumps(tmp_res)
                    if ss not in tmp_set:
                        tmp_set.add(ss)
                        parse_res.extend(tmp_res)
            if parse_res:
                one_res.append([ind, tmp_dic['content'], parse_res[0]['num']])
                # tmp_dic['is_title'] = True
        return [pkey, one_res]

    def add_title_level(self, one_dic):
        split_set = self.split_set
        if not self.pat_ls:
            self.pat_ls = self.load_title_pat_ls()
        title_dic = self.load_hierachy_pattern()
        if not one_dic:
            return one_dic
        seg_list_flag = False
        for content_dic in one_dic['content']:
            if 'seg_list' in content_dic:
                seg_list_flag = True
                break
        if not seg_list_flag:
            one_dic = Utils().max_match_one_mark_res(one_dic)
        _, init_title_res = self.title_extraction_single(one_dic, self.pat_ls)
        #		print 'init title res'
        #		print '\n'.join([json.dumps(tup, ensure_ascii=False) for tup in init_title_res])
        # title_res = self.filter_titles(init_title_res, one_dic['content'], title_dic)
        title_res = init_title_res
        #		print 'title_res'
        #		print json.dumps(title_res, ensure_ascii=False)
        # 进行title层级判断
        title_level = self.compute_title_level(title_res, title_dic)
        for tup in title_level:
            ind, level = tup
            one_dic['content'][ind]['title_level'] = level
        return one_dic

    def add_title_feature(self, dic):
        dic_list = dic.get("content", [])
        if not self.pat_ls:
            self.pat_ls = self.load_title_pat_ls()
        pkey, one_res = self.title_extraction_single(dic, self.pat_ls)
        __inds = [tmp[0] for tmp in one_res]
        _indexes = set([dic_list[i]["__index"] for i in __inds if "__index" in dic_list[i]])
        for content_dic in dic_list:
            if content_dic.get('__index', '') in _indexes:
                if 'feature' not in content_dic:
                    content_dic['feature'] = {'is_title': True}
                else:
                    if isinstance(content_dic['feature'], dict):
                        content_dic['feature']['is_title'] = True
                    else:
                        content_dic['feature'] = {'is_title': True}
        return dic

def backtrack(dic, ind):
    ls = []
    for i in range(ind, -1, -1):
        _dic = dic.get('content', [])[i]
        if _dic.get('type', "") == "text":
            ss = _dic.get('content', '').strip()
            s = ""
            if ":" in ss: s = ss.split(":")[0]
            elif "：" in ss: s = ss.split("：")[0]
            if s and "提示" in s:
                ls.insert(0, _dic)
                return ls
            elif "提示" in ss:
                ls.insert(0, _dic)
                return ls
            ls.insert(0, _dic)
    return []

def forwordtrack(dic, ind, start_level):
    ls = []
    while ind < len(dic):
        _dic = dic.get('content', [])[ind]
        if 'title_level' in _dic:
            le = _dic['title_level']
            if start_level + 1 <= le:
                break
        if _dic.get('type', "") == "text":
            ls.append(_dic)
        ind += 1
    return ls


if __name__ == '__main__':
    total = 0
    c_util = Utils()
    c_tf = TitleFeature()
    res_ls = []
    total_ls = []
    for line in sys.stdin:
        total += 1
        try:
            dic = json.loads(line.strip())
        except:
            continue
        try:
            if 'seg_list' not in dic.get('content', [{}])[0]:
                dic = c_util.max_match_one_mark_res(dic)
        except:
            sys.stderr.write(line)
        dic = c_tf.add_title_level(dic)
        total_ls.append(dic)
        for ii, content_dic in enumerate(dic.get('content', [])):
            if 'title_level' in content_dic:
                # if not first_title:
                _dic = dic.get('content', [])[ii - 1]
                if _dic.get('type', "") == "text":
                    ss = _dic.get('content', '').strip()
                    if not "提示性公告" in ss:
                        if "提示" in ss or "提醒" in ss:
                            start_level = content_dic['title_level']
                            dic.update({'content' : forwordtrack(dic, ii - 1, start_level)})
                            res_ls.append(dic)
                        else:
                            ls = backtrack(dic, ii - 1)
                            if ls:
                                dic.update({'content' : ls})
                                res_ls.append(dic)
                break
    for dic in res_ls:
        print json.dumps(dic, ensure_ascii=False)

    # <pre_xianshougufen>|<xianzhixinggupiao>|<jiesuogufen>

    # res_ls_hk = [dic['hbase_key'] for dic in res_ls ]
    # for dic in total_ls:
    #     if dic.get('hbase_key', '') and dic.get('hbase_key', '') not in res_ls_hk:
    #         print json.dumps(dic.get('hbase_key', ''), ensure_ascii=False)
    # print "total unmatched articles: %d" % (len(total_ls) - len(res_ls))
    # print "ratio: %f" % (float(len(res_ls)) / float(len(total_ls)))

    # for dic in res_ls:
    #     print json.dumps(dic.get('hbase_key', ''), ensure_ascii=False)
    #     for _dic in dic.get('content', []):
    #         print json.dumps(_dic.get('content', ''), ensure_ascii=False)
    #     print
    # print "total matched articles: %d" % len(res_ls)
    # print "ratio: %f" % (float(len(res_ls)) / float(total))

    # # sorting by the length of list
    # for (key, vlist) in res_dic.items():
    #     res_dic.update({key : len(vlist)})
    # print json.dumps(sorted(res_dic.items(), lambda x, y : cmp(x[1], y[1]), reverse=True), ensure_ascii=False)

