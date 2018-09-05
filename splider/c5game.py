# -*- coding: utf-8 -*-
import json
import urllib2

import datetime, time
from bs4 import BeautifulSoup
from splider.steam import save_steam_product, save_web_product, send_request, \
    get_steam_product
from tool.PoolDB import pool
from tool.CommonUtils import thread_error_stop, is_before_time


def collection_c5_product(app_id):
    func_name = collection_c5_product.__name__
    try:
        page_sql = """select page, start_page, total_page from spider_conf where function_name="%s" """ % func_name
        page_result = pool.find_one(page_sql)
        page = page_result.get("page")
        total_page = page_result.get("total_page")
        while True:
            url = "https://www.c5game.com/csgo/default/result.html?page=%s&locale=zh" % page
            response = send_request(url)
            soup = BeautifulSoup(response.read(), "html.parser")
            div = soup.find("div", id="yw0")
            li_list = div.find_all("li", attrs={"class": "selling"})
            print "c5game:product:db_page:%s" % page
            for li in li_list:
                try:
                    p_name = li.find("p", attrs={"class": "name"})
                    market_name = p_name.find("span", attrs={"class": "text-unique"}).string
                    icon_url = li.find("img").get("src").split("@250w.png")[0]
                    web_site_product_id = li.find("a", attrs={"class": "csgo-img-bg text-center img"}).get("href") \
                        .split(".html?")[1].split("&type=")[0].split("item_id=")[1]
                    steam_product = save_steam_product(market_name, icon_url, app_id, "")
                    if steam_product == 200:
                        steam_product = get_steam_product(app_id, market_name=market_name)
                    if not steam_product == -100:
                        save_web_product(WEB_SITE.get("c5game"), steam_product.get("id"), web_site_product_id, app_id)
                except BaseException as e:
                    if e.code == 429:
                        print "request too many, sleep 5 min"
                        time.sleep(300)
                    else:
                        print "c5game:product:error:%s" % e
                        continue
                    continue
            page = page + 1
            if page >= total_page:
                break
        thread_error_stop(page, func_name)
    except BaseException as e:
        print "c5game:product:error:%s" % e
        thread_error_stop(page, func_name)


def collection_c5_sale_history(app_id):
    func_name = collection_c5_sale_history.__name__
    sql = """select count(id) from product where web_site=%s""" % WEB_SITE.get("c5game")
    result = pool.find_one(sql)
    total_page = result.get("count(id)") / 100 + 1
    sql = """update spider_conf set total_page=%s, updated="%s" where function_name="%s" """ % \
          (total_page, datetime.datetime.now(), func_name)
    pool.commit(sql)
    sql = """select page, total_page, is_first, last_execute from spider_conf where function_name="%s" """ % func_name
    result = pool.find_one(sql)
    db_page = result.get("page")
    total_page = result.get("total_page")
    is_first = result.get("is_first")
    last_execute = result.get("last_execute")
    while True:
        try:
            start = db_page * 100
            sql = """select web_site_product_id, product_id from web_site_product where web_site=%s and app_id=%s limit %s, %s""" \
                  % (WEB_SITE.get("c5game"), app_id, start, 100)
            site_product_list = pool.find(sql)
            for site_product in site_product_list:
                web_site_product_id = site_product.get("web_site_product_id")
                url = "https://www.c5game.com/csgo/item/history/%s.html" % web_site_product_id
                response = send_request(url)
                if not response == 200:
                    break
                soup = BeautifulSoup(response.read(), "html.parser")
                tr_list = soup.find("div", attrs={"id": "history"}).find("table").find_all("tbody")[2].find_all("tr")
                for tr_item in tr_list:
                    try:
                        none_td = tr_item.find("td", attrs={"class": "text-center empty"})
                        if not none_td:
                           break
                        icon_url = tr_item.find("div", attrs={"class": "img csgo-img-bg ml-0"}).find("img").get("src")
                        market_name = tr_item.find("div", attrs={"class": "img csgo-img-bg ml-0"}).find("img").get("alt")
                        price = tr_item.find("span", attrs={"class": "ft-gold"}).string.split("￥")[1]
                        pay_time = "20" + tr_item.find_all("td")[4].string
                        if last_execute and is_first == 1 and is_before_time(pay_time, last_execute):
                            break
                        feature_id = get_feature_id("c5game", app_id, site_product.get("product_id"), pay_time)
                        if not get_sale_history(feature_id):
                            sql = """insert into sale_history(web_site, qty, price, pay_time, market_name, product_id,
                                                   web_site_product_id, created, app_id, description, wear, feature_id) VALUES
                                                   (%s, %s, %s, "%s", "%s", %s, %s, "%s", %s, "%s", "%s", "%s")""" % \
                                 (WEB_SITE.get("c5game"), 1, price, pay_time, market_name,
                                  site_product.get("product_id"), web_site_product_id,
                                  datetime.datetime.now(), app_id, "", "", feature_id)
                            pool.commit(sql)
                    except BaseException as e:
                        print "c5game:sale_history:error:%s" % e
                        continue
            if db_page >= total_page:
                break
        except BaseException as e:
            print "steam:sale_history:error:%s" % e
            thread_error_stop(db_page, func_name)


