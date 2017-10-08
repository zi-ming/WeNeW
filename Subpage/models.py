from django.db import models

class Website(models.Model):
    url = models.CharField(max_length=255, null=False, unique=True)
    detail = models.CharField(max_length=100)
    ctime = models.DateTimeField(auto_now_add=True)
    is_activate = models.BooleanField(default=True)
    delay_time = models.IntegerField(default=0)


class Website_Xpath(models.Model):
    website = models.ForeignKey("Website", related_name='websitexpath_fk')
    xpath = models.CharField(max_length=100, null=False)
    ctime = models.DateTimeField(auto_now_add=True)


class Xpath(models.Model):
    website = models.ForeignKey("Website")
    title_xpath = models.CharField(max_length=500, null=False, blank=False)
    author_xpath = models.CharField(max_length=500)
    time_xpath = models.CharField(max_length=500)
    content_xpath = models.TextField(null=False, blank=False)
    ctime = models.DateTimeField(auto_now_add=True)


class User_sub(models.Model):
    website = models.ForeignKey("Website")
    user = models.ForeignKey("UserAction.User")


class Data(models.Model):
    xpath = models.ForeignKey('Xpath')
    url = models.CharField(max_length=1000)
    title = models.CharField(max_length=1000)
    author = models.CharField(max_length=100)
    time = models.CharField(max_length=100)
    content = models.TextField()
    img1 = models.CharField(max_length=100)
    img2 = models.CharField(max_length=100)
    img3 = models.CharField(max_length=100)
    brief = models.CharField(max_length=1000)
    ctime = models.DateTimeField(auto_now_add=True)


class Website_msg(models.Model):
    website = models.ForeignKey("Website")
    content_url = models.CharField(max_length=1000, null=False)
    msg = models.CharField(max_length=1000, null=True, blank=True)
    ctime = models.DateTimeField(auto_now_add=True)


class Submanager(object):
    def __init__(self, data):
        self.id = data[0]
        self.url = data[1]
        self.detail = data[2]


class WebsiteMsg(object):
    def __init__(self, msg):
        self.msg_type = msg[0]
        self.website_url = self.argEncode(msg[1])
        self.content_url = self.argEncode(msg[2])

    def argEncode(self, url):
        return url.replace("&", "(-)__(-)")


