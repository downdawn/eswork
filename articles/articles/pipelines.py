# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import logging
# import MySQLdb
# import MySQLdb.cursors
import copy
import pymysql
from twisted.enterprise import adbapi


# class ArticlesPipeline(object):
#     def process_item(self, item, spider):
#         return item


class MysqlTwistedPipeline(object):
    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):  # 函数名固定，会被scrapy调用，直接可用settings的值
        """
        数据库建立连接
        :param settings: 配置参数
        :return: 实例化参数
        """
        adbparams = dict(
            host=settings['MYSQL_HOST'],
            db=settings['MYSQL_DBNAME'],
            user=settings['MYSQL_USER'],
            password=settings['MYSQL_PASSWORD'],
            cursorclass=pymysql.cursors.DictCursor  # 指定cursor类型
        )

        # 连接数据池ConnectionPool，使用pymysql或者Mysqldb连接
        dbpool = adbapi.ConnectionPool('pymysql', **adbparams)
        # 返回实例化参数
        return cls(dbpool)

    def process_item(self, item, spider):
        """
        使用twisted将MySQL插入变成异步执行。通过连接池执行具体的sql操作，返回一个对象
        """
        # 防止入库速度过慢导致数据重复
        item = copy.deepcopy(item)
        query = self.dbpool.runInteraction(self.do_insert, item)  # 指定操作方法和操作数据
        # 添加异常处理
        query.addCallback(self.handle_error)  # 处理异常

    def do_insert(self, cursor, item):
        # 对数据库进行插入操作，并不需要commit，twisted会自动commit
        insert_sql = """
      insert into pm_article(title, create_date, url, content, view, tag, url_id) VALUES (%s, %s, %s, %s, %s, %s, %s)
      """
        cursor.execute(insert_sql, (item['title'], item['create_date'], item['url'],
                                    item['content'], item['view'], item['tag'], item['url_id']))

    def handle_error(self, failure):
        if failure:
            # 打印错误信息
            print(failure)


class ElasticsearchPipeline(object):
    # 将数据写入到es中
    def process_item(self, item, spider):
        # 将item转换为es的数据
        item.save_to_es()

        return item
