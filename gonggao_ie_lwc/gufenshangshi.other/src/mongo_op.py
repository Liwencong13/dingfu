#!/bin/python
# coding=utf-8
from pymongo import MongoClient
import sys

MONGO_CONF = dict({
    'host_master': '192.168.2.71',
    'host_slave_1': '192.168.2.22',
    'host_slave_2': '192.168.2.27',
    'port': '27305',
    'db_name': 'efunds-test',
    'user_name': 'efunds-test',
    'password': 'MI9nW0yZNjmSVWT'
})

# connect with mongoDB
def connect_mongo():
    mongo_client = MongoClient('mongodb://{0}:{1},{2}:{3},{4}:{5}'.format(
    MONGO_CONF['host_master'], MONGO_CONF['port'],
    MONGO_CONF['host_slave_1'], MONGO_CONF['port'],
    MONGO_CONF['host_slave_2'], MONGO_CONF['port']))
    mongo_db = mongo_client[MONGO_CONF['db_name']]
    mongo_db.authenticate(MONGO_CONF['user_name'], MONGO_CONF['password'])
    return mongo_db


def get_collection(table_name):
    mongo_db = connect_mongo()
    collection = mongo_db[table_name]
    return collection


def get_docs_by_regex(table_name, regex):
    collection = get_collection(table_name)
    cursor = collection.find({"_id" : {"$regex" : regex}, "pattern_machine" : True})
    return cursor


def get_info_by_docid(table_name, doc_id):
    collection = get_collection(table_name)
    cursor = collection.find({"doc_id": doc_id, "pattern_machine": True})
    doc = cursor.next() # only one doc returned
    res_dict = {}
    res_dict['doc_id'] = doc['doc_id']
    fea_list = []
    try:
        for contents in doc['schema_pattern_machine'][0]:
            tmp_dict = {}
            for content_dict in contents:
                tmp_dict['para_position'] = content_dict['para_position']
                tmp_dict['text_position'] = content_dict['text_position']
                tmp_dict['value_ori'] = content_dict['value_ori']
            if tmp_dict:  # 去除空值
                fea_list.append(tmp_dict)
    except:
        pass
    res_dict['tab'] = fea_list
    return res_dict


# get what we need from a specific table, with string regex matching with 'doc_id'
def get_info_from_mongo(table_name, regex):
    """
    return:
        [ 'doc_id', 'tab'=fea_list[{'para_position', 'text_position', 'value_ori'}, ... ];
                ...
        ]
    """
    cursor = get_docs_by_regex(table_name, regex)
    res_list = []
    for _ in range(cursor.count()):
        res_dict = {}
        post = cursor.next()
        res_dict['doc_id'] = post['doc_id']
        fea_list = []
        for contents in post['schema_pattern_machine'][0]:
            tmp_dict = {}
            for content_dict in contents:
                tmp_dict['para_position'] = content_dict['para_position']
                tmp_dict['text_position'] = content_dict['text_position']
                tmp_dict['value_ori'] = content_dict['value_ori']
            if tmp_dict: # 去除空值
                fea_list.append(tmp_dict)
        res_dict['tab'] = fea_list
        res_list.append(res_dict)
    return res_list