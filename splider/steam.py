# -*- coding: utf-8 -*-
import json
import urllib
import datetime
import re
from math import ceil

from bs4 import BeautifulSoup

from tool import DecimalUtil
from tool.DBUtil import get_spider_conf, update_last_execute, save_web_product, save_trade_stop_log, save_steam_product, \
    get_steam_product, update_total_count
from tool.Code import ResultCode
from tool.PoolDB import pool
from tool.CommonUtils import Time_dict, thread_error_stop, send_request, WebSite


def collection_steam_product(app_id):
    """
    :param app_id:
    :return:
    """
    func_name = collection_steam_product.__name__
    headers = {"Accept-Language": "zh-CN,zh;q=0.8,en;q=0.6"}
    result = get_spider_conf(func_name)
    page = result.get("page")
    start_page = result.get("start_page")
    total_page = result.get("total_page")
    page_size = result.get("page_size")
    total_count = result.get("total_count")
    # 修改最后执行时间
    if start_page == page:
        update_last_execute(func_name)
    try:
        while True:
            print "steam:product:page:%s" % page
            start = page * page_size
            url = "https://steamcommunity.com/market/search/render/?query=&start=%s&count=%s&search_descriptions=0&" \
                  "sort_column=popular&sort_dir=desc&appid=%s" % (start, page_size, app_id)
            response = send_request(url, headers)
            resp_data = json.loads(response.read())
            if not resp_data:
                break
            if resp_data.get("success"):
                # 总数
                if total_count != resp_data.get("total_count"):
                    total_count = resp_data.get("total_count")
                    total_page = ceil(DecimalUtil.decimal_div(total_count, page_size))
                    update_total_count(func_name, total_count, total_page)
                # 其他数据
                html = resp_data.get("results_html")
                soup = BeautifulSoup(html, "html.parser")
                all_a = soup.find_all("a", attrs={"class", "market_listing_row_link"})
                for a_item in all_a:
                    try:
                        icon_url =a_item.find_all("img")[0].get("src").split("/62fx62f")[0]
                        span = a_item.find_all("span", attrs={"class", "market_listing_item_name"})[0]
                        market_name = unicode(span.string)
                        color = span.get("style").split("color:")[1][1:8]
                        market_hash_name = a_item.find("div", attrs={"class": "market_listing_row market_recent_listing_row market_listing_searchresult"}).get("data-hash-name")
                        save_result = save_steam_product(market_name, icon_url, app_id, color,
                                                         market_hash_name=market_hash_name)
                        if save_result.get("code") == ResultCode.Success:
                            save_web_product(WebSite.steam, save_result.get("data").get("id"), save_result.get("data").get("id"),
                                             app_id)
                    except BaseException as e:
                        print "steam:product:error:%s" % e
                        continue
                if page > total_page:
                    break
                page += 1
            else:
                print "steam:连接失败"
                break
        thread_error_stop(page, func_name)
    except BaseException as e2:
        save_trade_stop_log(function_name=func_name, page=page)
        thread_error_stop(page, func_name)


def collection_steam_sale_history(app_id):
    try:
        func_name = collection_steam_sale_history.__name__
        rows = 10
        sql = """select count(id) from web_site_product where web_site=%s""" % WEB_SITE.get("steam")
        total_count = pool.find_one(sql).get("count(id)") / rows + 1
        sql = """update spider_conf set total_page=%s, updated="%s" where function_name="%s" """ %\
              (total_count, datetime.datetime.now(), func_name)
        pool.commit(sql)
        sql = """select page, is_first, last_execute, start_page from spider_conf where function_name="%s" """ % func_name
        spider_result = pool.find_one(sql)
        db_page = spider_result.get("page")
        is_first = spider_result.get("is_first")
        last_execute = spider_result.get("last_execute")
        start_page = spider_result.get("start_page")
        hearders = {"Accept-Language": "zh-CN,zh;q=0.8,en;q=0.6"}
        if start_page == db_page and is_first == 1:
            set_last_execute_time(func_name)
        while True:
            start = db_page * rows
            sql = """select market_hash_name, product.market_name, product.id from product, web_site_product where
                        product.id=web_site_product.product_id and web_site=%s limit %s, %s""" % \
                  (WEB_SITE.get("steam"), start, rows)
            product_list = pool.find(sql)
            print "steam:sale_history:db_page:%s" % db_page
            for product in product_list:
                print "steam:sale_history:product:%s" % product.get("product.id")
                market_hash_name = str(product.get("market_hash_name").encode("utf-8"))
                time.sleep(1)
                url = "https://steamcommunity.com/market/listings/%s/%s" % (app_id, urllib.quote(market_hash_name))
                response = send_request(url, hearders)
                if response.code == 200:
                    soup = BeautifulSoup(response.read(), "html.parser")
                    pattern = re.compile(r"line1")
                    script = soup.find("script", text=pattern)
                    if not script:
                        continue
                    history_list = json.loads(script.text.split("line1=")[1].split("];")[0]+"]")
                    for history in history_list:
                        sell_time = history[0].split(" ")
                        pay_time = datetime.datetime(year=int(sell_time[2]), month=Time_dict.get(sell_time[0]), day=int(sell_time[1]),
                                                     hour=int(sell_time[3].split(":")[0]))
                        if last_execute and is_first == 1 and is_before_time(pay_time, last_execute):
                            continue
                        price = history[1]
                        qty = history[2]
                        feature_id = get_feature_id("steam", app_id, product.get("product.id"),
                                                    pay_time.strftime("%Y-%m-%d %H:%M:%S"))
                        if not get_sale_history(feature_id):
                            try:
                                sql = """insert into sale_history(web_site, qty, price, pay_time, market_name, product_id,
                                                                  web_site_product_id, created, app_id, description, wear, feature_id) VALUES
                                                                  (%s, %s, %s, "%s", "%s", %s, %s, "%s", %s, "%s", "%s", "%s")""" % \
                                      (WEB_SITE.get("steam"), qty, price, pay_time, product.get("product.market_name"),
                                       product.get("product.id"), product.get("product.id"), datetime.datetime.now(),
                                       app_id, "", "", feature_id)
                                pool.commit(sql)
                            except BaseException as e2:
                                print "steam:sale_history:error:%s" % e2
                                continue
                else:
                    break
            db_page = db_page + 1
            if db_page >= total_count:
                break
        thread_error_stop(db_page, func_name)
    except BaseException as e:
        print "steam:sale_history:error:%s" % e
        thread_error_stop(db_page, func_name)


def set_last_execute_time(func_name):
    now = datetime.datetime.now()
    last_exeucte_time = datetime.datetime(year=now.year, month=now.month, day=now.day, hour=0, minute=0, second=0)
    sql = """update spider_conf set last_execute=%s, updated=%s where function_name=%s"""
    param = [last_exeucte_time, datetime.datetime.now(), func_name]
    pool.commit(sql, param)

