from News.models import *
from common.mysql import Mysql


def readNewList(user_id, latest_id, type, limit=10):
    """
    @summary: 获取read_count条新闻
    :param user_id:     用户id（未登录的用户ID为-1，会返回所有新闻中的最新新闻）
    :param type:        读取类型（读取未读新闻的数量、获取未读新闻，获取旧新闻）
    :param latest_id:   客户端最新新闻id
    :param limit:       每次读取的新闻条数
    :return:            NewListItem列表
    """
    res = Mysql.queryNewList(user_id, latest_id, type, limit)
    if type == "getcount":
        return res[0][0] > 10 and res[0][0] or 0
    else:
        return [ NewListItem(item) for item in res ]


def readContent(id):
    """
    @summary: 读取指定id的新闻
    :param id:  要读取的新闻id
    :return:    NewContent新闻对象
    """
    record = Data.objects.get(id=id)
    return NewContent(record)
