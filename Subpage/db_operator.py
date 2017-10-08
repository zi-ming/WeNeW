from Subpage.models import *


def saveWebsiteXpath(user_id, url, detail, xpath):
    """
    @summary: 保存网站xpath
    :param user_id:         用户id
    :param url:             网站url
    :param detail:          网站备注
    :param xpath:           网站xpath
    :return:                boolean
    """
    try:
        web = Website.objects.filter(url=url)
        web = len(web) == 0 and Website.objects.create(url=url, detail=detail) or web[0]
        web_xpath = web.websitexpath_fk.filter(xpath = xpath)
        if len(web_xpath) == 0:
            web.websitexpath_fk.create(xpath=xpath)

        sub = User_sub.objects.filter(user_id=user_id, website_id=web.id)
        if len(sub) == 0:
            User_sub.objects.create(user_id=user_id, website_id=web.id)
        return True
    except Exception as e:
        print(e)
        return False


def saveContentXpath(website_url, title_xpath, author_xpath, time_xpath, content_xpath):
    """
    @summary: 保存内容xpath=
    :param website_url:     网站url
    :param title_xpath:     标题xpath
    :param author_xpath:    作者xpath
    :param time_xpath:      时间xpath
    :param content_xpath:   内容xpath
    :return:                {'res': boolean-obj, 'exist': boolean-obj, 'errors': list-obj}
    """
    try:
        web = Website.objects.filter(url = website_url)
        if len(web) == 0:
            return {'res': False,'exist':False, 'errors': ['数据库中不存在该菜单地址！',]}

        web = web[0]
        res = Xpath.objects.filter(website_id=web.id,
                             title_xpath=title_xpath,
                             author_xpath=author_xpath,
                             time_xpath=time_xpath,
                             content_xpath=content_xpath)
        if len(res) == 0:
            Xpath.objects.create(website_id=web.id,
                                 title_xpath=title_xpath,
                                 author_xpath=author_xpath,
                                 time_xpath=time_xpath,
                                 content_xpath=content_xpath)
            return {'res': True, 'exist': False, 'errors': []}
        else:
            return {'res': True, 'exist': True, 'errors': []}

    except Exception as e:
        return {'res': False, 'exist': False, 'errors': [repr(e),]}


def webSiteExist(website_url):
    """
    @summary: 检查网站是否已存在
    :param website_url:     网站地址
    :return:
    """
    count = Website.objects.filter(url=website_url).count()
    return count > 0


def delUserSub(user_id, website_ids):
    """
    @summary: 删除用户订阅
    :param user_id:     用户id
    :param website_ids: 网站id
    :return:
    """
    for id in website_ids:
        User_sub.objects.filter(user_id=user_id, website_id=id).delete()


def userSub(website_url, user_id):
    """
    @summary: 判断用户有没有订阅该网站，没有的话就订阅
    :param website_url:     网站地址
    :param user_id:         用户id
    :return:
    """
    website_id = Website.objects.filter(url=website_url).values("id")
    if website_id.count() > 0:
        website_id = website_id[0]["id"]
    rc = User_sub.objects.filter(website_id=website_id, user_id=user_id).count()
    if rc == 0:
        User_sub.objects.create(website_id=website_id, user_id=user_id)

