# -*- coding: utf-8 -*-

from elasticsearch_dsl import DocType, Date, Completion, Keyword, Text, Integer

from elasticsearch_dsl.analysis import CustomAnalyzer as _CustomAnalyzer

from elasticsearch_dsl.connections import connections
connections.create_connection(hosts=["localhost"])


class CustomAnalyzer(_CustomAnalyzer):
    # 版本问题，需要重新继承CustomAnalyzer，重写get_analysis_definition方法
    def get_analysis_definition(self):
        return {}


ik_analyzer = CustomAnalyzer("ik_max_word", filter=["lowercase"])


class ArticleType(DocType):
    """
    # elasticsearch_dsl安装5.4版本
    """
    # 文章类型
    suggest = Completion(analyzer=ik_analyzer)
    title = Text(analyzer="ik_max_word")
    create_date = Date()
    url = Keyword()
    view = Integer()
    tag = Text(analyzer="ik_max_word")
    content = Text(analyzer="ik_max_word")
    url_id = Keyword()

    class Meta:
        index = "pm"  # 数据库名
        doc_type = "article"  # 表名


if __name__ == "__main__":
    data = ArticleType.init()
    print(data)

