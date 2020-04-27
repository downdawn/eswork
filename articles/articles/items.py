# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import redis
import scrapy
import datetime
from scrapy.loader.processors import MapCompose
from articles.model.es_types import ArticleType

from elasticsearch_dsl.connections import connections
es = connections.create_connection(ArticleType._doc_type.using)

redis_cli = redis.StrictRedis()


def gen_suggests(index, info_tuple):
    # 根据字符串生成搜索建议数组
    used_words = set()
    suggests = []
    for text, weight in info_tuple:
        if text:
            # 调用es的analyze接口分析字符串
            words = es.indices.analyze(index=index, analyzer="ik_max_word", params={'filter': ["lowercase"]}, body=text)
            anylyzed_words = set([r["token"] for r in words["tokens"] if len(r["token"]) > 1])
            new_words = anylyzed_words - used_words
        else:
            new_words = set()

        if new_words:
            suggests.append({"input": list(new_words), "weight": weight})

    return suggests


class PmArticlesItem(scrapy.Item):
    # define the fields for your item here like:
    title = scrapy.Field()
    create_date = scrapy.Field()
    url = scrapy.Field()
    content = scrapy.Field()
    view = scrapy.Field()
    tag = scrapy.Field()
    url_id = scrapy.Field()

    def save_to_es(self):
        article = ArticleType()
        article.title = self['title']
        article.create_date = self["create_date"]
        article.content = self["content"]
        article.url = self["url"]
        article.view = self["view"]
        article.tag = self["tag"]
        article.meta.id = self["url_id"]

        article.suggest = gen_suggests(ArticleType._doc_type.index, ((article.title, 10), (article.tag, 7)))

        article.save()

        redis_cli.incr("pm_count")  # redis存储爬虫数量

        return

