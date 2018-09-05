# -*- coding: utf-8 -*-
import datetime
import urllib
import urllib2

from bs4 import BeautifulSoup

from tool.CommonUtils import base_result
from tool.Code import ResultCode
from tool.PoolDB import pool

# ------- 新增 start -------


def save_trade_stop_log(function_name, page):
    sql = """insert into thread_stop_log(created, function_name, page) values (%s, %s, %s)"""
    param = [datetime.datetime.now(), function_name, page]
    pool.commit(sql, param)


def save_web_product(web_site, product_id, web_site_product_id, app_id):
    sql = """select id from web_site_product where web_site=%s and web_site_product_id=%s and app_id=%s 
                                and product_id=%s"""
    result = pool.find(sql, (web_site, web_site_product_id, app_id, product_id))
    if not result:
        sql = """insert into web_site_product(web_site, product_id, web_site_product_id, created, app_id) 
                                                    values("%s","%s","%s",%s, %s)"""
        pool.commit(sql, (web_site, product_id, web_site_product_id, datetime.datetime.now(), app_id))


def save_steam_product(market_name, icon_url, app_id, color, market_hash_name=None):
    """
    保存Steam饰品
    :param market_name:
    :param icon_url:
    :param app_id:
    :param color:
    :param market_hash_name:
    :return:
    """
    result = base_result()
    if market_hash_name:
        steam_product = get_steam_product(app_id, market_hash_name=market_hash_name)
    else:
        steam_product = get_steam_product(app_id, market_name=market_name)
    if steam_product:
        result["code"] = ResultCode.Success
        result["data"] = steam_product
        return result
    if not market_hash_name:
        market_hash_name, color = get_steam_market_hash_name(app_id, market_name)
    is_merge = 0
    if u"箱" in market_name and app_id == 730:
        is_merge = 1
    if not market_hash_name:
        result["code"] = ResultCode.NoneProduct
        return result
    sql = """insert into product(market_name, market_hash_name, icon_url, created, app_id, color, is_merge) 
              values("%s","%s","%s", %s, %s, "%s", "%s")"""
    param = (market_name, market_hash_name, icon_url, datetime.datetime.now(), app_id, color, is_merge)
    pool.commit(sql, param)
    steam_product = get_steam_product(app_id, market_hash_name=market_hash_name)
    result["data"] = steam_product
    result["code"] = ResultCode.Success
    return result

# ------- 新增 end -------


# ------- 删除 start -------
# ------- 删除 end -------


# ------- 修改 start -------


def update_last_execute(function_name):
    sql = """update spider_conf set last_execute=%s where function_name=%s """
    param = [datetime.datetime.now(), function_name]
    return pool.commit(sql, param)


def update_total_count(function_name, total_count, total_page):
    sql = """update spider_conf set total_count=%s, total_page=%s, updated=%s where  function_name="%s" """
    param = (total_count, total_page, datetime.datetime.now(), function_name)
    return pool.commit(sql, param)

# ------- 修改 end -------


# ------- 查询 start -------


def get_spider_conf(function_name=None):
    if function_name:
        sql = """select function_name, page, created, updated, total_page, last_execute, is_first, start_page, status,
                  page_size, total_count from spider_conf where function_name = '%s' limit 1
              """ % function_name
        return pool.find_one(sql)
    else:
        sql = """select function_name, page, created, updated, total_page, last_execute, is_first, start_page, status
                  from spider_conf """
        return pool.find(sql)


def get_steam_product(app_id, market_name=None, market_hash_name=None):
    """
    获得Steam饰品
    :param app_id:
    :param market_name:
    :param market_hash_name:
    :return:
    """
    if market_hash_name:
        sql = """select id, market_name, market_hash_name, icon_url, app_id from product where market_hash_name="%s" 
                    and app_id=%s"""
        param = (market_hash_name, app_id)
    elif market_name:
        sql = """select id, market_name, market_hash_name, icon_url, app_id from product where market_name="%s" 
                  and app_id=%s """
        param = (market_name, app_id)
    else:
        return False
    result = pool.find_one(sql, param)
    return result


def get_steam_market_hash_name(app_id, market_name):
    """
    获得饰品 market_hash_name
    :param app_id:
    :param market_name:
    :return:
    """
    url2 = "https://steamcommunity.com/market/search?q=%s" % urllib.quote(str(market_name.encode("utf-8")))
    headers = {"Accept-Language": "zh-CN,zh;q=0.8,en;q=0.6"}
    request2 = urllib2.Request(url2, headers=headers)
    response2 = urllib2.urlopen(request2)
    if response2.code == 200:
        soup2 = BeautifulSoup(response2.read(), "html.parser")
        div = soup2.find_all("div", attrs={
            "class": "market_listing_row market_recent_listing_row market_listing_searchresult"})
        if not div:
            return None, None
        market_hash_name = div[0].get("data-hash-name")
        steam_market_name = soup2.find_all("span", attrs={"class": "market_listing_item_name"})[0].string
        color = soup2.find_all("span", attrs={"class": "market_listing_item_name"})[0].get("style").split("color:")[1]
        steam_product = get_steam_product(app_id, market_hash_name=market_hash_name)
        if steam_market_name == market_name and not steam_product:
            return market_hash_name, color
    return None, None


def get_sale_history(feature_id):
    sql = """select id from sale_history where feature_id="%s" """ % feature_id
    result = pool.find_one(sql)
    if result:
        return True
    return False

# ------- 查询 end -------