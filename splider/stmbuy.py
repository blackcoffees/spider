# -*- coding: utf-8 -*-
import urllib
import urllib2

import datetime, time
from bs4 import BeautifulSoup

from splider.steam import save_steam_product, get_steam_product, set_last_execute_time, \
    save_web_product, send_request
from tool.PoolDB import pool
from tool.CommonUtils import thread_error_stop, is_before_time


def collection_stmbuy_product(app_id):
    func_name = collection_stmbuy_product.__name__
    sql = """select page, total_page from spider_conf where function_name="%s" """ % func_name
    result = pool.find_one(sql)
    page = result.get("page")
    page_total = result.get("total_page")
    try:
        while True:
            url = "http://www.stmbuy.com/csgo/page/?&page=%s" % page
            response = send_request(url)
            print "stmbuy:product:db_page:%s" % page
            if response.code == 200:
                soup = BeautifulSoup(response.read(), "html.parser")
                ul = soup.find("ul", attrs={"class": "goods-list"})
                li_list = ul.find_all("li")
                for li_item in li_list:
                    try:
                        web_site_product_id = li_item.find("a").get("href").split("item-")[1]
                        if li_item.find("p", attrs={"class": "special-tag"}):
                            market_name = li_item.find("p", attrs={"class": "tit"}).string + " (" + \
                                          li_item.find("p", attrs={"class": "special-tag"}).contents[1].string + ")"
                        else:
                            market_name = li_item.find("p", attrs={"class": "tit"}).string
                        icon_url = li_item.find("img").get("src")
                        color = li_item.find("p", attrs={"class": "tit"}).get("style").split("color:")[1]
                        steam_product = save_steam_product(market_name, icon_url, app_id, color)
                        if steam_product == 200:
                            steam_product = get_steam_product(app_id, market_name=market_name)
                        if not steam_product == -100:
                            save_web_product(WEB_SITE.get("stmbuy"), steam_product.get("id"), web_site_product_id,
                                             app_id)
                    except BaseException as e:
                        if e.code == 429:
                            print "request too many, sleep 5 min"
                            time.sleep(300)
                        else:
                            print "stmbuy:product:error:%s" % e
                            continue
            page = page + 1
            if page > page_total:
                break
        thread_error_stop(page, func_name)
    except BaseException as e:
        print "stmbuy:product:error:%s" % e
        thread_error_stop(page, func_name)


def collection_stmbuy_sale_history(app_id):
    func_name = collection_stmbuy_sale_history.__name__
    sql = """select count(id) from web_site_product where web_site=%s""" % WEB_SITE.get("stmbuy")
    result = pool.find_one(sql)
    sql = """update spider_conf set total_page=%s, updated="%s" where function_name="%s" """ \
          %(result.get("count(id)")/100+1, datetime.datetime.now(), func_name)
    pool.commit(sql)
    sql = """select page, total_page, last_execute, is_first, start_page from spider_conf where function_name="%s" """ % func_name
    result = pool.find_one(sql)
    db_page = result.get("page")
    total_page = result.get("total_page")
    is_first = result.get("is_first")
    last_execute = result.get("last_execute")
    start_page = result.get("start_page")
    if start_page == db_page and is_first == 1:
        set_last_execute_time(func_name)
    try:
        while True:
            if db_page > total_page:
                break
            sql = """select web_site_product_id, product_id, id from web_site_product where web_site=%s limit %s, %s""" \
                  % (WEB_SITE.get("stmbuy"), db_page, 100)
            product_list = pool.find(sql)
            print "stmbuy:sale_history:db_page:%s" % db_page
            for product in product_list:
                print "stmbuy:sale_history:product:%s" % product.get("id")
                web_page = 1
                is_before = False
                while True:
                    url = "http://www.stmbuy.com/item/history.html?class_id=%s&game_name=csgo&sort[_id]=-1&page=%s" \
                          % (product.get("web_site_product_id"), web_page)
                    response = send_request(url)
                    if response.code == 200:
                        soup = BeautifulSoup(response.read(), "html.parser")
                        none = soup.find("div", attrs={"class": "def-none"})
                        if none:
                            break
                        ul = soup.find("ul", attrs={"class": "goods-list"})
                        li = ul.find_all("li")
                        for li_item in li:
                            try:
                                qty = li_item.find("div", attrs={"class": "amount"}).find("span").string
                                price_div = li_item.find("div", attrs={"class": "price"})
                                price = price_div.contents[1] + price_div.contents[2].string
                                pay_time = li_item.find_all("div", attrs={"class": "time fr"})[0].contents[2].strip()
                                if last_execute and is_before_time(pay_time, last_execute) and is_first == 1:
                                    is_before = False
                                    break
                                wear_p = li_item.find("div", attrs={"goods-sellinfo"}).find("p", attrs={
                                    "class": "mosundu-num"})
                                if wear_p:
                                    wear = wear_p.find("span").string
                                    market_name = li_item.find("div", attrs={"goods-sellinfo"}).find_all("p")[
                                        1].string
                                else:
                                    wear = ""
                                    market_name = li_item.find("div", attrs={"goods-sellinfo"}).find(
                                        "p").string.strip()
                                feature_id = get_feature_id("stmbuy", app_id, product.get("product_id"), pay_time)
                                if not get_sale_history(feature_id):
                                    sql = """insert into sale_history(web_site, qty, price, pay_time, market_name, product_id,
                                                                        web_site_product_id, created, app_id, description, wear, feature_id) VALUES
                                                                        (%s, %s, %s, "%s", "%s", %s, %s, "%s", %s, "%s", "%s", "%s")""" % \
                                          (WEB_SITE.get("stmbuy"), qty, price, pay_time, market_name,
                                           product.get("product_id"), product.get("id"),
                                           datetime.datetime.now(), app_id, "", wear, feature_id)
                                    pool.commit(sql)
                            except BaseException as e:
                                print "stmbuy:sale_history:error:%s" % e
                                continue
                    web_page += 1
                    if is_before:
                        break
        thread_error_stop(db_page, func_name)
    except BaseException as e:
        print "stmbuy:sale_history:error:%s" % e
        thread_error_stop(db_page, func_name)