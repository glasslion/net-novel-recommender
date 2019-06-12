#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from pyspider.libs.base_handler import *

from datetime import datetime
import re
import urllib.parse
import ast
from pyquery import PyQuery

from models import Book, Rating


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
         age=-1,
         itag='v1',
         user_agent='Sogou web spider/4.0(+http://www.sogou.com/docs/help/webmasters.htm#07)'
    )

    def on_start(self):
        books = [book for book in Book.select()][:2]
        for book in books:
            self.crawl(book.url, callback=self.rating_list_html, save={'depth': 1})

    def rating_list_html(self, response):
        ratings = response.doc('#content .thumbnail .caption .media')
        for r in ratings:
            cid = r.attrib['data-cid']
            url = f'http://www.yousuu.com/ajax/getonecomment?cid={cid}'
            self.crawl(url, callback=self.rating_detail_ajax)

        next_btn = response.doc('#content #next_comment_btn a').attr('onclick')
        # e.g. ys.book.nextcomment('22227','1528932106')
        if next_btn:
            next_btn = next_btn.replace('ys.book.nextcomment', '')
            bid, nexttime = ast.literal_eval(next_btn)
            url = f'http://www.yousuu.com/ajax/nextcomment?bid={bid}&nexttime={nexttime}'
            self.crawl(url, callback=self.rating_list_ajax)

    def rating_list_ajax(self, response):
        # ajax page is almost as same as the html page
        html = response.json['comment']
        d = PyQuery(html)
        response._doc = d.wrap('<div id="content"></div>')
        self.rating_list_html(response)


    def rating_detail_ajax(self, response):
        comment = response.json['comment']

        data = {
            'comment_id': comment['cid'],
            'username': comment['username'],
            'user_id': comment['uid'],
            'book_id': comment['bid'],
            'rate': comment.get('myrate', 0),
            'message': comment.get('message', ''),
            'starnum':  comment.get('starnum', 0),
        }
        Rating.get_or_create(**data)
