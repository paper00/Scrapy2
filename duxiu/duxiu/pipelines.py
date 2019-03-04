# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import pymysql
from twisted.enterprise import adbapi


class DuxiuPipeline(object):
    def __init__(self, dbPool):
        self.dbPool = dbPool

    @classmethod
    def from_settings(cls, settings):
        adbParams = dict(
            host=settings['MYSQL_HOST'],
            user=settings['MYSQL_USER'],
            password=settings['MYSQL_PASSWORD'],
            port=settings['MYSQL_PORT'],
            database=settings['MYSQL_DATABASE'],
            charset=settings['MYSQL_CHARSET'],
            use_unicode=True,
            cursorclass=pymysql.cursors.DictCursor
        )
        # Connect Pool
        dbPool = adbapi.ConnectionPool('pymysql', **adbParams)

        return cls(dbPool)

    def process_item(self, item, spider):
        # sql -> pool
        query = self.dbPool.runInteraction(self.insert_into, item)
        query.addErrback(self.handle_error)

        return item

    def insert_into(self, cursor, item):
        sql = """
                    insert books(title,author,category,subtype,date_of_pub,pages,url) VALUES(%s,%s,%s,%s,%s,%s,%s)
        """
        cursor.execute(sql, (item['title'],item['author'],item['category'],item['subtype'],item['date_of_pub'],item['pages'],item['url']))

    def handle_error(self, failure):
        if failure:
            print(failure)



# CREATE TABLE books(
#     NUM INT UNSIGNED PRIMARY KEY AUTO_INCREMENT NOT NULL,
#     Title VARCHAR(50) NOT NULL DEFAULT 'title',
#     Author VARCHAR(50) NOT NULL DEFAULT 'author',
#     Category VARCHAR(20) NOT NULL DEFAULT 'category',
#     SubType VARCHAR(50) NOT NULL DEFAULT 'subtype',
#     Date_of_pub VARCHAR(30),
#     Pages VARCHAR(10),
#     URL VARCHAR(100) NOT NULL UNIQUE
#     );