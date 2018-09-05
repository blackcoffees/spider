# -*- coding: utf-8 -*-
import threading
from splider.steam import collection_steam_product,collection_steam_sale_history
from splider.xxskins import collection_xxskins_product, collection_xx_sale_history
from splider.c5game import collection_c5_product
from splider.stmbuy import collection_stmbuy_product, collection_stmbuy_sale_history
from splider.opskins import collection_opskins_product


class CollectionThread(threading.Thread):

    def __init__(self, name, function_name, app_id):
        threading.Thread.__init__(self)
        self.name = name
        self.function_name = function_name
        self.stop = False,
        self.app_id = app_id
        self.event = threading.Event()

    def run(self):
        exec(str(self.function_name) + "(" + str(self.app_id) + ")")

    def get_stop(self):
        return self.stop