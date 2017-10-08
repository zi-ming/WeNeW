import urllib.parse
import re
import random

from Spider.config import *
from Spider.Redis import Redis_client
from Spider.cache import Cache
from scrapy.selector import Selector

cache = Cache()


def filterPureTag(html_selector, xpaths):
    """
    @summary:               获取纯净的页面源码（去除所有没用的标签属性）
    :param html_selector:   html选择器
    :param xpath:           title、author、time、content的xpath
    :return:                过滤后的html源码
    """
    item = ['', '', '', '']
    for i in range(4):
        if xpaths[i]:
            item[i] = html_selector.xpath(xpaths[i]).extract()
            item[i] = ''.join(item[i])
            p = re.compile(r' (?!(?:href|src|hrefs|target|alt|data-src))(?:[a-zA-Z0-9\-_]+)=(["\']).*?\1', re.I)
            item[i] = p.subn('', item[i])[0]                                # 去除其他没用的属性
            item[i] = re.subn(">(\s*)", ">", item[i])[0]                    # 去除标签内容开头的空格
            item[i] = re.subn("<p>(<img.*?>)</p>", r"\1", item[i])[0]       # 删除该格式下的p便签
            item[i] = re.subn("(<img.*?>)", r"<p align='middle'>\1</p>", item[i])[0]  # 设置图片居中
            item[i] = re.subn("<script.*?>.*?</script>", "", item[i])[0]    # 剔除某些在便签內的script便签
    return item


def getUrlInfo(url):
    """
    @summary:       获取url域名
    :param url:     url地址信息
    :return:        协议+域名, 协议, 域名
    """
    proto, rest = urllib.parse.splittype(url)
    domain, rest = urllib.parse.splithost(rest)
    return "%s://%s"%(proto, domain), proto, domain


def domainEqual(parent_url, child_url):
    """
    @summary:           判断两个url地址的域名是否相同
    :param parent_url:  网站url地址
    :param child_url:   内容url地址
    :return:
    """
    urlinfo = getUrlInfo(parent_url)
    demain_p = all(urlinfo[1:]) and urlinfo[0] or None
    urlinfo = getUrlInfo(child_url)
    demain_c = all(urlinfo[1:]) and urlinfo[0] or None
    return demain_p and demain_c and (demain_c in demain_p)


def urlSupplement(parent_url, child_url):
    """
    @summary:           补全url地址（针对<img>中src和<a>中href的缺省链接）
    :param parent_url:  父地址（带有完整协议和域名的url地址）
    :param child_url:   子地址（可能会出现缺省的地址）
    :return:
    """
    if child_url and child_url[0] == "/":
        child_url = "%s%s"%(getUrlInfo(parent_url)[0], child_url)
    return child_url


def imgSrcHandler(url, html):
    """
    @summary:       处理<img>的data-src和src情况以及域名缺省的情况（这个处理是针对微信的<img>缺省）
    :param url:     内容或者网站地址
    :param html:    页面源码
    :return:        处理后的页面源码
    """
    imgs = re.findall("<img.*?>", html)
    p1 = re.compile(r'(<img.*?\s)(data-src=(["\']))'  # 1 2 3
                    r'(.*?)(\3)'  # 4 5
                    r'(.*?)'  # 6
                    r'(\ssrc=\3)'  # 7
                    r'(.*?)(\3)'  # 8 9
                    r'(.*?>)', re.I)  # 10
    p2 = re.compile(r'(<img.*?\s)(data-src)(=(["\']).*?\4.*?>)')
    for img in imgs:
        new_img = p1.subn(r"\1\7\4\3\6\10", img)[0]
        if new_img == img:
            new_img = p2.subn(r'\1src\3', img)[0]
        if new_img != img:
            html = html.replace(img, new_img)
    imgs = re.findall("<img.*?>", html)
    p = re.compile(r'(<img.*?\ssrc=(["\']))(/.*?)\2', re.I)
    url = getUrlInfo(url)[0]
    for img in imgs:
        new_img = p.subn(r"\1%s\3\2" % url, img)[0]
        if new_img != img:
            html = html.replace(img, new_img)
    return html


def hrefHandler(url, html):
    """
    @summary:           补全href|hrefs属性中的缺省域名
    :param content_url: 内容页面链接地址，作用是提取页面的域名
    :param html:        页面源码
    :return:
    @note:              遍历所有href或hrefs的值，凡是以'/'开头的，一律替换成网站url+href|hrefs，
                        可能会有例外的情况，导致不能链接到正确的地址
    """

    p = re.compile(r'(\s(?:hrefs|href)=(["\']))(/.*?)\2', re.I)
    return p.subn(r"\1%s\3\2"%getUrlInfo(url)[0], html)[0]


def getProxy():
    """
    @summary:   获取代理ip
    """
    try:
        redis_client = Redis_client(availale_db)
        ip = redis_client.randomkey()
        if ip:
            port = redis_client.get(ip)
            if port:
                return ip, port
    except:pass
    return None, None


def delProxy(ip):
    """
    @summary:   删除代理ip
    """
    redis_client = Redis_client(availale_db)
    redis_client.delete(ip)


def incrDelay_time(website_id, timeout):
    """
    @summary: 对网站增加timeout个时间延迟
    """
    record = Cache.getDict(cache.websiteDelay_dict, website_id)
    Cache.setDict(cache.websiteDelay_dict, website_id, int(record) + timeout)


def brief(html):
    """
    @summary: 获取内容简介
    """
    selector = Selector(text=html)
    brief = selector.xpath("string(.)").extract()
    return len(brief) and brief[0][:150] or ""


def randomImg(html):
    """
    @summary: 随机获取内容的图片
    """
    selector = Selector(text=html)
    imgs = selector.xpath("//img/@src").extract()
    count = len(imgs)
    if count == 0:
        return ["", "", ""]
    else:
        index = random.randint(0, count - 1)
        # random.sample(arr, count)     # 随机从arr中获取count个元素
        return [imgs[index], "", ""]


def spaceHandler(content_list, index_list):
    """
    @summary: 处理内容的空格
    """
    for i in index_list:
        content_list[i] = content_list[i].strip()
    return content_list


def legalLink(href):
    """
    @summary: 判断链接是否合法
    """
    if href:
        if len(href) > 3 and 'http' in href[:4].lower() or href[0] == "/":
                return True
    return False


def filterHrefs(url, xpath, html_selector):
    """
    @summary: 筛选内容链接地址
    """
    xpath = xpath + '/@href'
    xpath = "%s|%ss"%(xpath,xpath)
    tmp_hrefs = html_selector.xpath(xpath).extract()
    hrefs = []
    for href in tmp_hrefs:
        if legalLink(href):
            hrefs.append(href)
    hrefs = [urlSupplement(url, href) for href in hrefs]
    return hrefs