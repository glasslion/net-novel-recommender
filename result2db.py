"""
A simple script that export the PySpider result db to the model db
"""

from pyspider.database import connect_database
from models import Book

if __name__ == '__main__':
    resultdb = connect_database("sqlite+resultdb:///data/result.db")
    for result in resultdb.select('booklist'):
        fields = result['result']
        if 'author' in fields:
            print(fields['name'])
            url = fields.pop('url')
            Book.get_or_create(url=url, defaults=fields)
