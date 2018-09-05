# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup

from splider.steam import send_request


def collection_stmbuy_product():
    try:
        while True:
            url = "http://123.56.70.240:9000/sl/csgo-china/issues/100041/"
            response = send_request(url)
            if response.code == 200:
                soup = BeautifulSoup(response.read(), "html.parser")
                table = soup.find("table", attrs={"class": "table key-value"})
                tr = table.find_all("tr")[0]
                code = tr.find("span", attrs={"class": "val-number"})
                # for li_item in li_list:
                #     try:
                #         web_site_product_id = li_item.find("a").get("href").split("item-")[1]
                #         if li_item.find("p", attrs={"class": "special-tag"}):
                #             market_name = li_item.find("p", attrs={"class": "tit"}).string + " (" + \
                #                           li_item.find("p", attrs={"class": "special-tag"}).contents[1].string + ")"
                #         else:
                #             market_name = li_item.find("p", attrs={"class": "tit"}).string
                #         icon_url = li_item.find("img").get("src")
                #         color = li_item.find("p", attrs={"class": "tit"}).get("style").split("color:")[1]
                #         steam_product = save_steam_product(market_name, icon_url, app_id, color)
                #         if steam_product == 200:
                #             steam_product = get_steam_product(app_id, market_name=market_name)
                #         if not steam_product == -100:
                #             save_web_product(WEB_SITE.get("stmbuy"), steam_product.get("id"), web_site_product_id,
                #                              app_id)
                #     except BaseException as e:
                #         if e.code == 429:
                #             print "request too many, sleep 5 min"
                #             time.sleep(300)
                #         else:
                #             print "stmbuy:product:error:%s" % e
                #             continue
    except BaseException as e:
        print "stmbuy:product:error:%s" % e

if __name__ == "__main__":
    collection_stmbuy_product()