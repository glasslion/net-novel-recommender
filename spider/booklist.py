#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2019-06-10 11:55:49
# Project: booklist

from pyspider.libs.base_handler import *
from datetime import datetime
import re
import urllib.parse


START_URL = 'http://www.yousuu.com/booklist?s=digest'
MAX_BOOKLIST_PAGES = 100


def dump_page(resp):
    with open('/tmp/pyspider_debug.html', 'wb') as f:
        f.write(resp.content)

def extract_num(s):
    """
    Extract number from a string
    """
    ptn = re.compile(r'(\d+)')
    m = ptn.search(s)
    if m:
        return m.groups()[0]
    return None

def replace_querystring(url, qs):
    url_parts = list(urllib.parse.urlparse(url))
    query = dict(urllib.parse.parse_qsl(url_parts[4]))
    query.update(qs)
    url_parts[4] = urllib.parse.urlencode(query)
    return urllib.parse.urlunparse(url_parts)


class Handler(BaseHandler):
    crawl_config = dict(
        user_agent='Sogou web spider/4.0(+http://www.sogou.com/docs/help/webmasters.htm#07)',
    )

    def on_start(self):
        self.crawl(START_URL, callback=self.index_page, save={'depth': 1})

    @config(priority=3, age=60*20)
    def index_page(self, response):
        sel = '.shudanlist tr.list-item td h4 a[href^="http://www.yousuu.com/booklist"]'
        for each in response.doc(sel).items():
            self.crawl(each.attr.href, callback=self.booklist_page, save={'page': 1})

        if response.save['depth'] < MAX_BOOKLIST_PAGES:
            next_js = response.doc('.pagination a:contains("下一页")').attr('onclick')
            # next_js demo: ys.common.jumpurl('t','1560087064')
            tid = extract_num(next_js)
            next_url = f'http://www.yousuu.com/booklist?s=digest&t={tid}'
            self.crawl(
                next_url, callback=self.index_page,
                save={'depth': response.save['depth'] + 1})



    @config(priority=3)
    def booklist_page(self, response):
        pages = response.doc('.pagination li a')
        # e.g. ys.common.jumpurl('page',2)
        if len(pages) > 0:
            page_nums = [extract_num(p.attr.onclick) for p in pages.items()]
            page_nums = [int(p) for p in page_nums if p]
            max_page = max(page_nums)
            print(max_page)
            if response.save['page'] < max_page:
                next_page = response.save['page'] + 1
                next_url = replace_querystring(response.url, {'page': next_page})
                print(next_url)
                self.crawl(
                    next_url, callback=self.booklist_page, save={'page': next_page})

        for each in response.doc('.booklist-item .booklist-subject .title a').items():
            self.crawl(each.attr.href, callback=self.book_page, save={'page': 1})

        return {
            "url": response.url,
            "title": response.doc('title').text(),
        }

    @config(priority=2)
    def book_page(self, response):
        name = response.doc('.container > div:nth-child(3) > div:nth-child(1) > div:nth-child(1) > div.col-sm-7 > div:nth-child(1) > span').text()

        author = response.doc('.container > div:nth-child(3) > div:nth-child(1) > div:nth-child(1) > div.col-sm-7 > div.media > div > ul > li:nth-child(1)').text()
        author = author.replace('作者:', '')

        length = response.doc('.container > div:nth-child(3) > div:nth-child(1) > div:nth-child(1) > div.col-sm-7 > div.media > div > ul > li:nth-child(2)').text()
        length = int(extract_num(length) or '-1')

        category = response.doc('#booktag a.category').text()

        rating_count = response.doc('.ys-book-averrate small').text()
        rating_count = int(extract_num(rating_count) or '-1')

        rating_avg = response.doc('.ys-book-averrate').remove('small').text()
        rating_avg = float(rating_avg)

        update_date = response.doc('.container > div:nth-child(3) > div:nth-child(1) > div:nth-child(1) > div.col-sm-7 > div.media > div > ul > li:nth-child(5)').text()
        update_date = update_date.replace('更新时间: ', '')
        # e.g. 19/05/2 22:10
        update_date = '20' + update_date
        update_date = datetime.strptime(update_date, '%Y/%m/%d %H:%M').isoformat()
        ret = {
            "url": response.url,
            "name": name,
            "author": author,
            "length": length,
            "category": category,
            "rating_count": rating_count,
            "rating_avg": rating_avg,
            "update_date": update_date,
        }
        return ret
