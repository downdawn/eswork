# eswork
ElasticSearch+Django+Scrapy搜索引擎

## 项目功能

scrapy爬虫获取数据存储至es，ElasticSearch+Django实现搜索页面。

## 快速开始

```python
# 下拉项目代码
git clone https://github.com/downdawn/eswork.git
# 安装requirements.txt依赖
pip install -r requirements.txt
# 启动Elasticsearch-RTF
cd elasticsearch/bin
elasticsearch.bat
# 启动爬虫，获取部分数据
cd eswork/articles
python main.py
# 启动Django
cd eswork/lcvsearch
python manage.py runserver
```

## [原版教学视频](https://coding.imooc.com/class/92.html)
感谢老师分享知识

## 其他详情见博客

个人博客：[https://www.downdawn.com/blog/detail/25/](https://www.downdawn.com/blog/detail/25/)


或者

csdn：[https://blog.csdn.net/qq_42280510/article/details/104593599](https://blog.csdn.net/qq_42280510/article/details/104593599)
