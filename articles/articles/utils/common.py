
import hashlib
import datetime


def date_convert(value):
    # 日期转化
    try:
        create_date = datetime.datetime.strptime(value, "%Y/%m/%d").date()
    except Exception as e:
        print(e)
        create_date = datetime.datetime.now().date()

    return create_date


def get_md5(url):
    # url md5加密
    if isinstance(url, str):
        url = url.encode("utf-8")
    m = hashlib.md5()
    m.update(url)
    return m.hexdigest()


if __name__ == '__main__':
    print(date_convert('2020/02/28'))
    print(get_md5('http://www.woshipm.com/it/3443027.html'))
