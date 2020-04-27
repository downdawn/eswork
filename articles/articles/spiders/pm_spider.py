# -*- coding: utf-8 -*-
import re
import json
import scrapy
import copy
from articles.items import PmArticlesItem
from articles.utils.common import date_convert


class PmSpiderSpider(scrapy.Spider):
    name = 'pm_spider'
    allowed_domains = ['woshipm.com']
    # start_urls = ['http://www.woshipm.com/__api/v1/stream-list/page/1']
    base_url = 'http://www.woshipm.com/__api/v1/stream-list/page/{}'

    def start_requests(self):
        for i in range(1, 10):
            url = self.base_url.format(i)
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        item = PmArticlesItem()
        # print(response.text)
        data_set = json.loads(response.text)
        # print(datas.get('payload'))
        if data_set:
            for data in data_set.get('payload'):
                # print(data)
                item["title"] = data.get("title", '')
                item["create_date"] = date_convert(data.get("date", ''))
                item["url"] = data.get("permalink", '')
                # item["content"] = data.get("snipper", '').replace('\n', '').replace('\r', '')
                item["view"] = data.get("view", '')
                item["tag"] = re.search(r'tag">(.*?)<', data.get("category", '')).group(1)
                item["url_id"] = data.get('id', '')
                # print(item)
                yield scrapy.Request(url=item["url"], callback=self.parse_detail, meta=copy.deepcopy({'item': item}))

    def parse_detail(self, response):
        item = response.meta['item']
        content = response.xpath("//div[@class='grap']//text()").re(r'\S+')
        item["content"] = ''.join(content)
        # print(item)
        yield item

