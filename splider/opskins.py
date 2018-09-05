import time
from bs4 import BeautifulSoup

from splider.steam import send_request, save_steam_product, get_steam_product, save_web_product
from tool.PoolDB import pool
from tool.CommonUtils import thread_error_stop


def collection_opskins_product(app_id):
    try:
        func_name = collection_opskins_product.__name__
        sql = """select page from spider_conf where function_name="%s" """ % func_name
        result = pool.find_one(sql)
        page = result.get("page")
        headers = {
            "referer": "https://zh.opskins.com/?loc=shop_browse",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko)"
                          " Chrome/55.0.2883.87 Safari/537.36",
            "x-csrf": "2I25Z75fQ3YlYxMvdbndV5z5PYFDrmQEE",
            "x-op-userid": "0",
            "content-type": "text/html; charset=UTF-8",
            "x-requested-with": "XMLHttpRequest",
            "accept-encoding": "gzip, deflate, sdch, br",
            "accept-language": "zh-CN,zh;q=0.8,en;q=0.6",
            "cookie": "__ssid=1e1310b2-13e2-4bf1-a574-56200eff83bc; opskins_login_token=PTy54AM5urW6QvWHWLcJpBuwywiDhIkj;"
                      " Hm_lvt_f4d83c43fa7e41722d75d036cbcfcbbe=1522206377,1522229544,1524127707; eu_cookie_accepted=auto; "
                      "Hm_lvt_f4d83c43fa7e41722d75d036cbcfcbbe=1522206377,1522229544,1524127707; "
                      "opskins_csrf_token=2I25Z75fQ3YlYxMvdbndV5z5PYFDrmQEE;"
                      " referer=aHR0cHM6Ly93d3cuc28uY29tL3M%2FaWU9dXRmLTgmc3JjPTM2MGNocm9tZV90b29sYmFyX3NlYXJjaCZxPW9wc2tpbnM%3D;"
                      " incoming=landing_url%3D%252F%253Faff_id%253D2%2526marketing_source%253Dbaidu%2526trans_id%"
                      "253D102a5930f5661b3983b7688811e0e9%2526utm_campaign%253D%2526utm_content%253D%2526utm_medium%"
                      "253Dcpc%2526utm_source%253Dbaidu%2526utm_term%253D%26referer%3Dhttps%253A%252F%252Fwww.so.com%"
                      "252Fs%253Fie%253Dutf-8%2526src%253D360chrome_toolbar_search%2526q%253Dopskins%26user_agent%"
                      "3D119900%26trans_id%3D102a5930f5661b3983b7688811e0e9%26aff_id%3D2%26marketing_source%3Dbaidu%26kw%"
                      "3D%26campid%3D%26adgrp%3D%26mt%3D%26source%3Dbaidu%26medium%3Dcpc%26campaign%3D%26term%3D%26content%3D; "
                      "loggedout-marketing-link-json=%7B%22aff_id%22%3A%222%22%2C%22marketing_source%22%3A%22baidu%22%2"
                      "C%22trans_id%22%3A%22102a5930f5661b3983b7688811e0e9%22%2C%22utm_campaign%22%3A%22%22%2C%22utm_conte"
                      "nt%22%3A%22%22%2C%22utm_medium%22%3A%22cpc%22%2C%22utm_source%22%3A%22baidu%22%2C%22utm_term%22%3A%"
                      "22%22%2C%22referrer%22%3A%22www.so.com%22%2C%22referrer_path%22%3A%22%5C%2Fs%22%2C%"
                      "%22%3A%22ie%3Dutf-8%26src%3D360chrome_toolbar_search%26q%3Dopskins%22%7D; aft=eyJ0cmFuc0lkIjoiMTA"
                      "yYTU5MzBmNTY2MWIzOTgzYjc2ODg4MTFlMGU5IiwiYWZmaWxpYXRlSWQiOiIyIiwibWFya2V0aW5nU291cmNlIjoiYmFpZHUi"
                      "LCJrZXl3b3JkIjpudWxsLCJjYW1wYWlnbklkIjpudWxsLCJhZEdyb3VwIjpudWxsLCJtYXRjaFR5cGUiOm51bGwsInNvdXJjZ"
                      "SI6ImJhaWR1IiwibWVkaXVtIjoiY3BjIiwiY2FtcGFpZ24iOiIiLCJ0ZXJtIjoiIiwiY29udGVudCI6IiIsInNlc3Npb25UaW1"
                      "lc3RhbXAiOjE1MjUyNTI2NDgsInJlZmVyZXIiOiJodHRwczpcL1wvd3d3LnNvLmNvbVwvcz9pZT11dGYtOCZzcmM9MzYwY2h"
                      "yb21lX3Rvb2xiYXJfc2VhcmNoJnE9b3Bza2lucyIsImxhbmRpbmdVcmwiOiJcLz9hZmZfaWQ9MiZtYXJrZXRpbmdfc291cmNlP"
                      "WJhaWR1JnRyYW5zX2lkPTEwMmE1OTMwZjU2NjFiMzk4M2I3Njg4ODExZTBlOSZ1dG1fY2FtcGFpZ249JnV0bV9jb250ZW50P"
                      "SZ1dG1fbWVkaXVtPWNwYyZ1dG1fc291cmNlPWJhaWR1JnV0bV90ZXJtPSJ9; __cfduid=ddebe77d43e319a65b1601e33"
                      "9bcd54121525252649; _pk_ref.1.0ff0=%5B%22baidu%22%2C%22%22%2C1525252681%2C%22https%3A%2F%2Fwww"
                      ".so.com%2Fs%3Fie%3Dutf-8%26src%3D360chrome_toolbar_search%26q%3Dopskins%22%5D; cf_clearance=bbd"
                      "f22c0367ea926643a5d054adbb08d52dbb284-1525252703-14400; _ga=GA1.2.1144942300.1508463511; _gid=G"
                      "A1.2.1518183863.1525252651; _uetsid=_uet7cb5ab24; _pk_id.1.0ff0=d5d4cd07616a5428.1508463536.1"
                      "1.1525252793.1525252681.; _pk_ses.1.0ff0=*; n_lang=zh-CN; timezone_offset=8%2C0;"
                      " Hm_lvt_af7094281cbe36451577c00f5c0923a8=1525252681; "
                      "Hm_lpvt_af7094281cbe36451577c00f5c0923a8=1525252793; PHPSESSID=an968inhr4b4q8tlmvlkj9bit0"
        }
        db_page = page
        while True:
            print "opskins:product:page:%s" % page
            time.sleep(1)
            url = "https://zh.opskins.com/ajax/browse_scroll.php?page=%s&appId=%s&contextId=2" % (db_page, app_id)
            response = send_request(url, headers=headers)
            a = response.read()
            b = unicode(a, "gta")
            soup = BeautifulSoup(a, "html.parser")
            product_div_list = soup.find_all("div", attrs={"class": "featured-item"})
            if not product_div_list:
                break
            for product_div in product_div_list:
                try:
                    market_name = product_div.find("div", attrs={"class": "market-name market-link"}).string
                    web_site_product_id = product_div.attr("id").split("cartItem")[1]
                    icon_url = \
                    product_div.find("img", attrs={"class": "item-img media-async-complete"}).attr("src").split(
                        "/256fx256f")[0]
                    steam_product = save_steam_product(market_name, icon_url, app_id, "#ffffff")
                    if steam_product == 200:
                        steam_product = get_steam_product(app_id, market_name=market_name)
                    if not steam_product == -100:
                        save_web_product(WEB_SITE.get("opskins"), steam_product.get("id"), web_site_product_id,
                                         app_id)
                except BaseException as e:
                    print "opskins:product:error:%s" % e
                    continue
        thread_error_stop(db_page, func_name)
    except BaseException as e:
        print "opskins:product:error:%s" % e
        thread_error_stop(db_page, func_name)