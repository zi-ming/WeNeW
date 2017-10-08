import re
import urllib.request
import urllib.parse
import json

from Subpage import db_operator
from common.spider import Spider
from common.config import global_Chrome


class InitResType(object):
    success = 0
    inlegalUrl = 1
    urlIsNone = 2
    OAnotfound = 3


def initWebsite(website_type, website_url, content_url=''):
    """
    @summary: 初始化订阅的网站页面（添加相应的js）
    :param website_type:    网站类型（0：普通网站地址；1：公众号地址）
    :param website_url:     网站地址
    :param content_url:     内容地址
    :return:
    """
    if int(website_type) == 0 and not urlLegal(website_url):
        return {"res": InitResType.inlegalUrl, "code": ""}

    oa_name = ""
    if website_type == "1":
        oa_name = website_url
        website_url = getOAUrl(website_url)
        if website_url is None:
            return {"res": InitResType.OAnotfound, "code": ""}

    script_code = """
            <script src="/static/Subpage/js/common.js"></script>
            <script src = "/static/Subpage/js/filterXpath.js"></script>
            <script src="/static/Subpage/js/websiteDiscriminate.js"></script>
            """
    html = Spider().chromedriver(website_url)

    head = re.findall("(<head.*?>)", html)
    if len(head) > 0:
        head = head[0]
        html = html.replace(head, "%s%s"%(head, '<meta name="referrer" content="never"><link rel="stylesheet" type="text/css" href="/static/Subpage/css/sub.css">'))
    html = html.replace("</body>", "%s<input id = 'sub_info' type = 'hidden' detail='%s' website_url='%s' content_url='%s'></body>"%(
    script_code, oa_name, website_url, content_url))
    return {"res": InitResType.success, "code": html}


def initIframe_contentPage(website_url, content_url):
    """
    @summary: 初始化订阅的内容页面（添加相应的js）
    :param website_url:     网站url地址
    :param content_url:     内容url地址
    :return:                页面源码
    """

    script_code = """
        <script src="/static/Subpage/js/common.js"></script>
        <script src="/static/Subpage/js/filterXpath.js"></script>
        <script src="/static/Subpage/js/contentDiscriminate.js"></script>
        """

    if global_Chrome:
        html = Spider().chromedriver(content_url)
    else:
        html = Spider().urllib(content_url)
    if not html: return "404"

    p = re.compile(r'(<head>|<head .*?>)')
    html = p.subn(r"\1%s"%('<meta name="referrer" content="never">'
                           '<link rel="stylesheet" type="text/css" href="/static/Subpage/css/sub.css">'), html)[0]

    p = re.compile(r'(</body>)')
    extract_html = "%s<input id='sub_info' type='hidden' website_url='%s' content_url='%s'>"%(
        script_code, website_url, content_url)
    html = p.subn(r"%s\1"%extract_html, html)[0]
    return html


def websiteExist(website_url):
    """
    @summary: 检查网站url是否已存在与数据库中
    :param website_url: 网站url地址
    """
    return website_url and db_operator.webSiteExist(website_url) or False


def getUrlInfo(url):
    """
    @summary: 获取url信息（完整url、协议、域名）
    :param url:     url地址信息
    :return:        协议+域名, 协议, 域名
    """
    proto, rest = urllib.parse.splittype(url)
    domain, rest = urllib.parse.splithost(rest)
    return "%s://%s"%(proto, domain), proto, domain


def domainEqual(website_url, content_url):
    """
    @summary: 判断两个url地址的域名是否相同
    :param website_url: 网站url地址
    :param content_url:     内容url地址
    :return:
    """
    urlinfo = getUrlInfo(website_url)
    domain1 = all(urlinfo[1:]) and urlinfo[0] or None
    urlinfo = getUrlInfo(content_url)
    domain2 = all(urlinfo[1:]) and urlinfo[0] or None
    return domain1 and domain2 and (domain2 in domain1)


def getArgs(obj, keys):
    """
    @summary: 解码原来的地址信息，其实就是把"(-)__(-)"替换成"&"
    :param obj:     HttpRequest object
    :param keys:    要提取的参数名（list）
    :return:        dict object
    """
    args = {}
    for key  in keys:
        args[key] = obj.get(key, "").replace("(-)__(-)", "&")
    return args


def getOAUrl(name):
    """
    @summary: 获取公众号链接地址
    :param name:    公众号名称
    :return:        公众号链接地址 or None
    """
    try:
        oa_json = Spider().requests("http://top.aiweibang.com/user/getsearch", "POST", {'Kw': name})
        oa_data = json.loads(oa_json)["data"]
        oa_id = oa_data['data'][0]['Id']
        url = "http://top.aiweibang.com/article/%s"%oa_id
        return url
    except:
        return None


def urlLegal(url):
    """
    @summary: 判断链接是否合法
    :param type:    链接类型（0：普通链接；1：公众号）
    :param url:     链接地址
    :return:        boolean
    """
    p = re.compile('^((http|https)://)?\w+\.\w+')
    return p.match(url) != None