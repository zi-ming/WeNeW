from Subpage.models import *
from News import common

class NewListItem(object):
    """
    Django模板中的新闻列表对象
    """
    def __init__(self, record):
        self.id = record[0]
        self.title = record[1]
        self.author = record[2]
        self.time = str(record[3])
        self.img = record[4]
        self.brief = record[5]

    def parseDict(self):
        dict = {}
        dict['id'] = self.id
        dict['title'] = self.title
        dict['author'] = self.author
        dict['time'] = self.time
        dict['img'] = self.img
        dict['brief'] = self.brief
        return dict

class NewContent(object):
    """
    Django模板中的新闻内容对象
    """
    def __init__(self, model):
        self.id = model.id
        self.title = model.title
        self.author = model.author
        self.time = model.time
        self.content = model.content
        __objs = Website.objects.filter(xpath__id=model.xpath_id)
        self.websiteurl =  len(__objs) and __objs[0].url or "url is None"
        self.websiteurl = common.urlEncode(self.websiteurl)
        self.contenturl = model.url
        self.contenturl = common.urlEncode(self.contenturl)
