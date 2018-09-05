# -*- coding: utf-8 -*-
from base.ThreadList import ThreadList
from base.thread import CollectionThread
from tool.PoolDB import pool
from tool.CommonUtils import thread_list

if __name__ == "__main__":
    sql = """select function_name, page, total_page from spider_conf where status=1 limit 1"""
    web_list = pool.find(sql)
    tread_list = ThreadList()
    for web in web_list:
        thread = CollectionThread(web.get("function_name"), web.get("function_name"), 730)
        thread_list.append(thread)
        thread.start()
    while True:
        if len(thread_list.get_all()) == 0:
            break
        for thread in thread_list.get_all():
            # 线程已经停止
            if thread.get_stop():
                thread.event.clear()
                thread.event.wait(100)
                thread.event.set()




    # print "process start:%s" % datetime.datetime.now()
    # web_name_list = ["xxskins"]
    # app_id = 730
    # type = "sale_history"
    # for web_name in web_name_list:
    #     if type == "sale_history":
    #         thread_name = WEB_FUNCTION.get(web_name)[0]
    #     elif type == "product":
    #         thread_name = product_function.get(web_name)[0]
    #     else:
    #         print "paramter type error"
    #         print "process stop:%s" % datetime.datetime.now()
    #         sys.exit(0)
    #     fuc_name = "%s(%s)" % (thread_name, app_id)
    #     singal = threading.Event()
    #     thread1 = collection_thread(thread_name, fuc_name, singal, web_name)
    #     thread_list.append(thread1)
    #     thread1.start()
    # while True:
    #     if len(thread_list.get_all()) == 0:
    #         break
    #     for thread in thread_list.get_all():
    #         if thread.stop:
    #             sql = """select page, total_page, start_page from spider_conf where function_name="%s" """ % thread.name
    #             result = pool.find_one(sql)
    #             page = result.get("page")
    #             total_page = result.get("total_page")
    #             start_page = result.get("start_page")
    #             if page >= total_page:
    #                 update_sql = """update spider_conf set page = %s, updated="%s" where function_name="%s" """ % \
    #                              (start_page, datetime.datetime.now(), thread.name)
    #                 pool.commit(update_sql)
    #                 thread_list.remove(thread)
    #                 break
    #             else:
    #                 print "thread :%s, sleep" % thread.name
    #                 thread.singal.wait(300)
    #                 thread_list.remove(thread)
    #                 new_thread = collection_thread(thread.name, thread.function_name, singal, thread.web_name)
    #                 thread_list.append(new_thread)
    #                 new_thread.start()
    #                 print "thread :%s, start" % thread.name
    # print "process stop:%s" % datetime.datetime.now()
    # sys.exit(0)
    # collection_steam_product(730)
    # collection_xxskins_product(730)