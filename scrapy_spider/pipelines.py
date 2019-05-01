# -*- coding: utf-8 -*-

import os
import json

import MySQLdb
from MySQLdb import cursors
from scrapy.pipelines.images import ImagesPipeline
from twisted.enterprise import adbapi

from .settings import BASE_DIR


# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html


class JobboleArticleImagePipeline(ImagesPipeline):
    def item_completed(self, results, item, info):
        ok, value = results[0]
        cover_path = value['path'] if ok else ''
        item['cover_path'] = cover_path
        return item


class JobboleArticleJsonExporterPipeline(object):
    def __init__(self):
        dir_path = os.path.join(BASE_DIR, 'jsons')
        self._file = open(os.path.join(dir_path, 'jobbole_article.json'), 'w', encoding='utf-8')

    def process_item(self, item, spider):
        line = json.dumps(dict(item), ensure_ascii=False) + '\n'
        self._file.write(line)
        return item

    def spider_closed(self, spider):
        self._file.close()


class SyncMySQLExporterPipeline(object):
    def __init__(self):
        self._conn = MySQLdb.connect(
            host=os.environ['MYSQL_HOST'],
            port=int(os.environ['MYSQL_PORT']),
            user=os.environ['MYSQL_USER'],
            passwd=os.environ['MYSQL_PASSWORD'],
            db=os.environ['MYSQL_DB'],
            connect_timeout=60,
            charset='utf8mb4',
            use_unicode=True
        )
        self._cursor = self._conn.cursor()

    def process_item(self, item, spider):
        insert_sql, params = item.get_insert_sql()
        self._cursor.execute(
            insert_sql,
            params
        )
        self._conn.commit()


class AsyncMySQLExporterPipeline(object):
    """使用 Twisted 的异步机制写入数据库"""
    def __init__(self):
        db_options = dict(
            host=os.environ['MYSQL_HOST'],
            port=int(os.environ['MYSQL_PORT']),
            user=os.environ['MYSQL_USER'],
            passwd=os.environ['MYSQL_PASSWORD'],
            db=os.environ['MYSQL_DB'],
            connect_timeout=60,
            charset='utf8mb4',
            use_unicode=True,
            cursorclass=cursors.DictCursor
        )
        # 使用 Twisted 的异步 API 创建数据库连接池
        self._db_pool = adbapi.ConnectionPool('MySQLdb', **db_options)

    def process_item(self, item, spider):
        deferred = self._db_pool.runInteraction(self.do_insert, item)
        deferred.addErrback(self.handle_error)

    def handle_error(self, failure):
        """处理数据库异步操作的异常"""
        print(failure)

    def do_insert(self, cursor, item):
        insert_sql, params = item.get_insert_sql()
        cursor.execute(insert_sql, params)
