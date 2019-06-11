#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2019-06-10 11:55:49
# Project: demo

from pyspider.libs.base_handler import *
import re


START_URL = 'http://127.0.0.1:8000'

class Handler(BaseHandler):
    crawl_config = dict(
         age=1,
         itag='v3',
         process_time_limit=1000000,
    )

    def on_start(self):
        self.crawl(START_URL, callback=self.index_page, )

    @config(priority=3)
    def index_page(self, response):
        for each in response.doc('a').items():
            self.crawl(each.attr.href, callback=self.index_page)

