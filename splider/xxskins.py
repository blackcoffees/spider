# -*- coding: utf-8 -*-
import json
import urllib2
import datetime
from splider.steam import get_steam_product, save_steam_product, set_last_execute_time, save_web_product, send_request
from tool.PoolDB import pool
from tool.CommonUtils import thread_error_stop, is_before_time


def collection_xxskins_product(app_id):
    func_name = collection_xxskins_product.__name__
    sql = """select page, start_page, total_page from spider_conf where function_name="%s" """ % func_name
    result = pool.find_one(sql)
    page = result.get("page")
    start_page = result.get("start_page")
    total_page = result.get("total_page")
    try:
        while True:
            url = "https://apis.xxskins.com/goods/%s/0?_=1522230191000&page=%s" % (app_id, page)
            response = send_request(url)
            resp_data = json.loads(response.read())
            print "xxskins:product:page:%s" % page
            if resp_data and int(resp_data.get("code")) == 99999:
                # 总页数
                if page == start_page:
                    total_page = resp_data.get("data").get("totalPage")
                    sql = """update spider_conf set total_page=%s where function_name="%s" """ % (total_page, func_name)
                    pool.commit(sql)
                product_list = resp_data.get("data").get("list")
                for product in product_list:
                    try:
                        icon_url = "https://steamcommunity-a.akamaihd.net/economy/image/class/%s/%s" % \
                                   (product.get("app_id"), product.get("class_id"))
                        market_name = product.get("market_name")
                        color = product.get("category_rarity_color")
                        market_hash_name = product.get("market_hash_name")
                        steam_product = save_steam_product(market_name, icon_url, app_id, color,
                                                           market_hash_name=market_hash_name)
                        if steam_product == 200:
                            steam_product = get_steam_product(app_id, market_hash_name=market_hash_name)
                        if not steam_product == -100:
                            save_web_product(WEB_SITE.get("xxskins"), steam_product.get("id"), product.get("goods_item_id"),
                                             app_id)
                    except BaseException as e:
                        print "xxskins:product:error:%s" % e
                        continue
                page = page + 1
                if page > total_page:
                    break
        thread_error_stop(page, func_name)
    except BaseException as e:
        print "xxskins:product:error:%s" % e
        thread_error_stop(page, func_name)


def collection_xx_sale_history(app_id):
    func_name = collection_xx_sale_history.__name__
    try:
        sql = """select count(id) from web_site_product where web_site=%s""" % WEB_SITE.get("xxskins")
        total_page = pool.find_one(sql).get("count(id)") / 100 + 1
        sql = """update spider_conf set total_page=%s, updated="%s" where function_name="%s" """ % \
              (total_page, datetime.datetime.now(), func_name)
        pool.commit(sql)
        web_id = WEB_SITE.get("xxskins")
        sql = """select page, last_execute, is_first, start_page from spider_conf where function_name="%s" limit 1""" % func_name
        result = pool.find_one(sql)
        db_page = result.get("page")
        last_execute = result.get("last_execute")
        is_first = result.get("is_first")
        start_page = result.get("start_page")
        if is_first == 0:
            collenction_all_reset(app_id)
        if db_page == start_page and is_first == 1:
            set_last_execute_time(func_name)
        db_rows = 100
        while True:
            db_start = db_page * db_rows
            sql = """select product_id, web_site_product_id, market_name,is_merge from web_site_product, product 
                      where web_site_product.app_id=%s and web_site=%s and web_site_product.product_id=product.id 
                      and is_merge = 1
                      limit %s, %s """ % (app_id, web_id, db_start, db_rows)
            web_p_list = pool.find(sql)
            print "xxskins:sale_history:db_page:%s" % db_page
            for site_product in web_p_list:
                web_page = 1
                is_before = False
                print "xxskins:sale_history:product:%s" % site_product.get("product_id")
                while True:
                    url = "https://apis.xxskins.com/goods/saleRecord?_=1522660905000&goodsItemId=%s&page=%s&limit=100" % \
                          (site_product.get("web_site_product_id"), web_page)
                    response = send_request(url)
                    resp_data = json.loads(response.read())
                    print url
                    print "%s" % web_page
                    if web_page == 279:
                        print "asdfsadfsadfsadd"
                        print "asdfsadfsadfsadd"
                        print "asdfsadfsadfsadd"
                    if resp_data and int(resp_data.get("code")) == 99999:
                        history_list = resp_data.get("data").get("list")
                        if history_list:
                            for history in history_list:
                                try:
                                    if last_execute and is_before_time(history.get("sell_time"), last_execute) and is_first == 1:
                                        is_before = True
                                        break
                                    feature_id = get_feature_id("xxshinks", app_id, site_product.get("product_id"),
                                                                history.get("sell_time"))
                                    sql = """select id, qty from sale_history where feature_id="%s" """ % feature_id
                                    result = pool.find_one(sql)
                                    if not result:
                                        sticker_json = history.get("sticker_json")
                                        if not sticker_json:
                                            sticker_json = ""
                                        else:
                                            sticker_json = json.dumps(sticker_json)
                                        wear = history.get("worn")
                                        if not wear:
                                            wear = ""
                                        sql = """insert into sale_history(web_site, qty, price, pay_time, market_name,
                                                  product_id, web_site_product_id, created, app_id, description, wear,
                                                  feature_id) VALUES (%s, %s, %s, "%s", "%s", %s, %s, "%s", %s, '%s',
                                                   "%s", "%s")""" % \
                                              (web_id, history.get("count"), history.get("sell_price"),
                                               history.get("sell_time"), site_product.get("market_name"),
                                               site_product.get("product_id"), site_product.get("web_site_product_id"),
                                               datetime.datetime.now(), app_id, sticker_json, wear,
                                               feature_id)
                                        pool.commit(sql)
                                    elif result and site_product.get("is_merge") == 1:
                                        total_qty = result.get("qty") + history.get("count")
                                        sql = """update sale_history set qty=%s, updated="%s" where id=%s""" % \
                                              (total_qty, datetime.datetime.now(), result.get("id"))
                                        pool.commit(sql)
                                except BaseException as e:
                                    print "xxskins:sale_history:error:%s" % e
                                    continue
                        else:
                            break
                    else:
                        break
                    if is_before:
                        break
                    web_page = web_page + 1
            db_page = db_page + 1
            if db_page >= total_page:
                break
        thread_error_stop(db_page, func_name)
    except BaseException as e:
        print "xxskins:sale_history:error:%s" % e
        thread_error_stop(db_page, func_name)


def collenction_all_reset(app_id):
    """收集所有数据时，对is_merge进行初始化"""
    sql = """select id from product where app_id=%s and is_merge=1 """ % app_id
    result = pool.find(sql)
    ids = [int(item.get("id")) for item in result]
    ids = tuple(ids)
    sql = """update sale_history set qty=0, updated="%s" WHERE product_id in %s""" % (datetime.datetime.now(), ids)
    pool.commit(sql)

