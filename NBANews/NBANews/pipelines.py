# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import codecs
import json
import pymysql
from scrapy.pipelines.images import ImagesPipeline
from scrapy.exporters import JsonItemExporter
from twisted.enterprise import adbapi


class NbanewsPipeline(object):
    def process_item(self, item, spider):
        return item


class MysqlPipeline(object):
    def __init__(self):
        self.conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='12345678', db='NBANews',
                                    charset="utf8")
        self.cursor = self.conn.cursor()

    def process_item(self, item, spider):
        insert_sql = '''
        insert into news(title, url,url_object_id,create_time,comment_nums,content) 
        values (%s,%s,%s,%s,%s,%s)
        '''
        try:
            self.cursor.execute(insert_sql,
                                (
                                    item['title'],
                                    item['url'],
                                    item['url_object_id'],
                                    item['create_time'],
                                    item['comment_nums'],
                                    item['content']
                                )
                                )

            self.conn.commit()
        except:
            self.conn.rollback()


class MysqlTwistedPipeline(object):
    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        dbparms = dict(
            host=settings['MYSQL_HOST'],
            db=settings['MYSQL_DBNAME'],
            user=settings['MYSQL_USER'],
            password=settings['MYSQL_PASSWORD'],
            # charset='utf-8',
            cursorclass=pymysql.cursors.DictCursor,
            use_unicode=True
        )

        dbpool = adbapi.ConnectionPool('MySQLdb', **dbparms)

        return cls(dbpool)

    def process_item(self, item, spider):
        # 使用twisted 讲mysql 插入变成异步
        query = self.dbpool.runInteraction(self.do_insert, item)
        query.addErrback(self.handle_error)  # 处理异常

    def handle_error(self, failure):
        # 处理异常
        print(failure)

    def do_insert(self, cursor, item):
        insert_sql = '''
               insert into news(title, url,url_object_id,create_time,comment_nums,content) 
               values (%s,%s,%s,%s,%s,%s)
               '''
        cursor.execute(insert_sql,
                       (
                           item['title'],
                           item['url'],
                           item['url_object_id'],
                           item['create_time'],
                           item['comment_nums'],
                           item['content']
                       )
                       )


class JsonWithEncodingPipeline(object):
    def __init__(self):
        self.file = codecs.open('NBANews.json', 'w', encoding='utf-8')

    def process_item(self, item, spider):
        lines = json.dumps(dict(item), ensure_ascii=False) + "\n"
        self.file.write(lines)
        return item

    def spider_closed(self, spider):
        self.file.close()


class NBAImagesPipeline(ImagesPipeline):
    '''
    定制图片
    '''

    def item_completed(self, results, item, info):
        if 'front_image_path' in item:
            for ok, value in results:
                image_path = value['path']
            item['front_image_path'] = image_path
            return item
