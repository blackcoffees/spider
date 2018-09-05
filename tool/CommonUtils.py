# -*- coding: utf-8 -*-

import datetime
import urllib2

from base.ThreadList import ThreadList
from tool.Code import ResultCode
from tool.PoolDB import pool

APP_IDS = {"CSGO": 730}

thread_list = ThreadList()

Time_dict = {"Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6, "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12, }


class WebSite(type):
    xxskins = 1
    c5game = 2
    steam = 3
    stmbuy = 4
    all_web_size = [xxskins, c5game, steam, stmbuy]


def is_before_time(pay_time, last_execute):
    pay_time = datetime.datetime.strptime(pay_time, "%Y-%m-%d %H:%M:%S")
    if pay_time < last_execute:
        return True
    return False


def thread_error_stop(page, func_name):
    page_sql = """update spider_conf set page=%s, updated='%s' where function_name='%s'""" \
               % (page, datetime.datetime.now(), func_name)
    pool.commit(page_sql)
    thread_list.sleep(func_name)


def send_request(url, headers=None):
    if headers:
        request = urllib2.Request(url, headers=headers)
    else:
        request = urllib2.Request(url)
    response = urllib2.urlopen(request)
    return response


def get_feature_id(web_site_name, app_id, product_id, pay_time):
    return "%s:%s:%s:%s" % (web_site_name, app_id, product_id, pay_time)


def base_result(message=None, data=None):
    resutl = {"code": ResultCode.Error, "message": "", "data": {}}
    if message:
        resutl["message"] = message
    if data:
        resutl["data"] = data
    return resutl