from peewee import *
import datetime

import os


db = SqliteDatabase('my_database.db')

class BaseModel(Model):
    class Meta:
        database = db


class Book(BaseModel):
    url = CharField(index=True)
    name = CharField()
    author = CharField()
    category = CharField()
    length = IntegerField()
    rating_count = IntegerField()
    rating_avg = FloatField()
    update_date = CharField()



class Rating(BaseModel):
    comment_id = CharField(index=True)
    username = CharField()
    user_id = IntegerField(index=True)
    book_id = IntegerField(index=True)
    rate = IntegerField()
    message = TextField()
    starnum = IntegerField()


if __name__ == '__main__':
    db.connect()
    db.create_tables([Book, Rating], safe=True)
