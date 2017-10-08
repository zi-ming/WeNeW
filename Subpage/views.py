import json

from django.shortcuts import render
from django.shortcuts import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from Subpage import common
from Subpage import db_operator
from Subpage import models
from common.mysql import Mysql


@login_required
def parse2Website(req):
    """
    @summary: 网站和公众号输入页面
    """

    return render(req, "Subpage/parse2Website.html")


@login_required
def saveWebsiteXpath(req):
    """
    @summary: 保存网站订阅以及对应的xpath页面
    """
    if req.method == "POST":
        detail, website_url, xpath = \
            common.getArgs(req.POST,
                           ("detail", "website_url", "xpath")).values()
        res = db_operator.saveWebsiteXpath(req.user.id, website_url, detail, xpath)
        if res:
            return HttpResponse(True)
    return HttpResponse(False)


@login_required
def parse2Content(req):
    """
    @summary: 输入内容地址页面
    """
    return render(req, "Subpage/parse2Content.html")


@login_required
def websiteSub(req):
    """
    @summary: 根据订阅的地址，打开网站页面
    """
    if req.method == "GET":
        website_type, website_url, content_url = common.getArgs(req.GET,
                                                                ("website_type","website_url", "content_url")).values()
        res = common.initWebsite(website_type, website_url, content_url)
        if res['res'] == common.InitResType.inlegalUrl:
            return render(req, "Subpage/parse2Website.html", {"errors": "请输入合法地址"})
        elif res['res'] == common.InitResType.OAnotfound:
            return render(req, "Subpage/parse2Website.html", {"errors": "公众号不存在"})
        elif res['res'] == common.InitResType.success:
            return render(req, "Subpage/websiteSub.html", {'html_code': res['code']})


@login_required
def contentSub(req):
    """
    @summary: 根据内容地址，打开内容页面
    """
    if (req.method == "GET"):
        _website_url, _content_url = req.GET.get("website_url"), req.GET.get("content_url")
        website_url, content_url = common.getArgs(req.GET,
                                                  ("website_url", "content_url")).values()

        if not common.urlLegal(website_url) or not common.urlLegal(content_url):
            return render(req, "Subpage/parse2Content.html", {"errors": "网站地址或内容地址有误"})

        # 如果网站地址不存在
        if not common.websiteExist(website_url):
            return HttpResponseRedirect("/sub/websiteSub/?website_url=%s&content_url=%s"%
                                        (_website_url, _content_url))
        else:
            db_operator.userSub(website_url, req.user.id)
        return render(req, "Subpage/contentSub.html", {"website_url": _website_url, "content_url": _content_url})
    return HttpResponse("content has not POST method.")


@login_required
def iframe_contentPage(req):
    """
    @summary: 内容xpath订阅的左半部分
    """
    if req.method == "GET":
        html = common.initIframe_contentPage(**common.getArgs(req.GET, ("website_url", "content_url")))
        return render(req, "Subpage/iframe_contentPage.html", {"html_code": html})
    else:
        res = db_operator.saveContentXpath(**common.getArgs(req.POST,
                                                            ("website_url","title_xpath",
                                                             "author_xpath","time_xpath","content_xpath")))
        if res['res']:
            return HttpResponse("保存成功！")
        else:
            return HttpResponse("保存失败，%s"%res['errors'])

@login_required
def iframe_previewPage(req):
    """
    @summary: 内容xpath订阅的右半部分
    """
    return render(req, "Subpage/iframe_previewPage.html")


@login_required
def sub_manager(req):
    """
    @summary: 订阅管理页面
    """
    if req.method == "GET":
        websites = Mysql.queryWebsite(req.user.id)
        if websites:
            websites = [models.Submanager(data) for data in websites]
        return render(req, "Subpage/sub_manager.html", {"websites": websites})
    if req.method == "POST":
        website_ids = json.loads(req.POST.get('website_ids'))
        Mysql.cancleWebsiteSub(req.user.id, website_ids)
        return HttpResponse("0")


def website_msg(req):
    """
    @summary: 网站订阅消息反馈页面
    """
    if req.method == "GET":
        msgs = Mysql.queryWebsiteMsg(req.user.id)
        if msgs != None:
            msgs = [models.WebsiteMsg(msg) for msg in msgs]
        return render(req, "Subpage/website_msg.html", {"msgs": msgs})
    else:
        Mysql.clearMsg(req.user.id)
        return HttpResponse(True)


