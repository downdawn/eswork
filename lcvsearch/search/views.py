from django.shortcuts import render
import json
from django.views.generic.base import View
from search.models import ArticleType
from django.http import HttpResponse
from elasticsearch import Elasticsearch
from datetime import datetime
import redis

client = Elasticsearch(hosts=["127.0.0.1"])
redis_cli = redis.StrictRedis()


class IndexView(View):
    # 首页
    def get(self, request):
        topn_search = redis_cli.zrevrangebyscore("search_keywords_set", "+inf", "-inf", start=0, num=5)
        topn_search = [search.decode() for search in topn_search]
        return render(request, "index.html", {"topn_search": topn_search})


class SearchSuggest(View):
    def get(self, request):
        key_words = request.GET.get('s', '')
        re_datas = []
        if key_words:
            s = ArticleType.search()
            s = s.suggest('my_suggest', key_words, completion={
                "field": "suggest", "fuzzy": {
                    "fuzziness": 2
                },
                "size": 10
            })
            suggestions = s.execute_suggest()
            for match in suggestions.my_suggest[0].options:
                source = match._source
                re_datas.append(source["title"])
        return HttpResponse(json.dumps(re_datas), content_type="application/json")


class SearchView(View):
    """
    搜索视图，根据搜索词q和类型s_type返回搜索结果
    """
    def get(self, request):
        key_words = request.GET.get("q", "")
        s_type = request.GET.get("s_type", "article")
        # TODO
        # 根据类型不同，动态取对应的数据库内容

        # 热门搜索设置和排序
        redis_cli.zincrby("search_keywords_set", 1, key_words)  # redis最新版本参数坑
        topn_search = redis_cli.zrevrangebyscore("search_keywords_set", "+inf", "-inf", start=0, num=5)
        topn_search = [search.decode() for search in topn_search]

        page = request.GET.get("p", "1")
        try:
            page = int(page)
        except:
            page = 1

        pm_count = redis_cli.get("pm_count").decode()  # 获取爬虫数量

        start_time = datetime.now()
        response = client.search(
            index="pm",
            body={
                "query": {
                    "multi_match": {
                        "query": key_words,
                        "fields": ["tag", "title", "content"]
                    }
                },
                "from": (page-1)*10,
                "size": 10,
                "highlight": {
                    "pre_tags": ['<span class="keyWord">'],
                    "post_tags": ['</span>'],
                    "fields": {
                        "title": {},
                        "content": {},
                    }
                }
            }
        )

        end_time = datetime.now()
        last_seconds = (end_time-start_time).total_seconds()  # 搜索计时
        total_nums = response["hits"]["total"]
        if (page % 10) > 0:
            page_nums = int(total_nums/10) + 1
        else:
            page_nums = int(total_nums/10)
        hit_list = []
        for hit in response["hits"]["hits"]:
            hit_dict = {}
            if "title" in hit["highlight"]:
                hit_dict["title"] = "".join(hit["highlight"]["title"])
            else:
                hit_dict["title"] = hit["_source"]["title"]
            if "content" in hit["highlight"]:
                hit_dict["content"] = "".join(hit["highlight"]["content"])[:500]  # 取前五百个词
            else:
                hit_dict["content"] = hit["_source"]["content"][:500]

            hit_dict["create_date"] = hit["_source"]["create_date"]
            hit_dict["url"] = hit["_source"]["url"]
            hit_dict["score"] = hit["_score"]

            hit_list.append(hit_dict)

        return render(request, "result.html", {"page": page,
                                               "all_hits": hit_list,
                                               "key_words": key_words,
                                               "total_nums": total_nums,
                                               "page_nums": page_nums,
                                               "last_seconds": last_seconds,
                                               "pm_count": pm_count,
                                               "topn_search": topn_search})
