
import time
import uuid
import threading
import queue
from tabulate import tabulate
import traceback

from Spider import mysql
from Spider import log
from Spider.log import LogType
from Spider import thumbnail
from Spider.spider import Spider
from Spider.cache import Cache
from Spider.common import imgSrcHandler, hrefHandler,filterPureTag, incrDelay_time, brief, randomImg, spaceHandler,filterHrefs
from Spider.config import global_Chrome
from Spider.models import SpiderResType


cache = Cache()
db = mysql.Mysql()
global_EXIT = False


def filterContentUrlFunc(website_id, website_url, xpath):
    """
    @summary: 筛选出网站的内容url
    """
    try:
        spiderRes = Spider().chromedriver(website_url)
        html_selector = spiderRes.selector
        if html_selector is None:
            log.logMsg(LogType.htmlSelectorNone,
                       "[FilterContentUrlThread] %s %s" % (website_url, "html_selector is None."))
            return False

        hrefs = filterHrefs(website_url, xpath, html_selector)
        if len(hrefs) == 0:
            return False

        flag = False
        for href in hrefs:
            if not Cache.listItemExist(cache.oldContent_list, href) and \
                    not Cache.listItemExist(cache.unrecognized_contentUrl_dict, href):
                Cache.putQueue(cache.freshContentUrl_queue, (website_id, href))
                flag = True
        if not flag:
            # 如果没有新数据，则延迟15分钟的爬取时间
            incrDelay_time(website_id, 900)
        return True
    except Exception as e:
        log.logMsg(LogType.error, "[FilterContentUrlThread] %s %s" % (website_url, traceback.format_exc()))
    return False


def filterContentInfoFunc(website_id, content_url):
    """
    @summary: 筛选内容中的信息
    """
    try:
        xpaths = mysql.Mysql.queryContentXpath(website_id)  # 返回字段循序： title_xpath,author_xpath,time_xpath,content_xpath,id
        contents = ['', '', '', '']                     # 记录 title, author, time, content内容的列表

        spiderRes = global_Chrome and Spider().chromedriver(content_url) or Spider().urllib(content_url)
        html_selector = spiderRes.selector
        if not html_selector:
            log.logMsg(LogType.htmlSelectorNone, "[filterContentInfoFunc] %s的html_selector为空" % content_url)
            return SpiderResType.htmlSelctorNone


        for xpath in xpaths:    # 筛选出最完整的信息
            items = filterPureTag(html_selector, xpath)
            if items[0] and items[3]:
                if (len(items[3]) > len(contents[3])) or (len(items[3]) == len(contents[3])) and (
                                    len(items[0]) > len(contents[0]) or len(items[1]) > len(contents[1]) or len(
                            items[2]) > len(contents[2])
                ):
                    contents = [item for item in items]
                    contents.append(xpath[-1])

        if contents[0] and contents[3]:
            if db.cursorIsClose():
                log.logMsg(LogType.error, "[filterContentInfoFunc] cursor already closed")
                return SpiderResType.cursorClose

            contents[3] = imgSrcHandler(content_url, contents[3])  # 处理图片src指向
            contents[3] = hrefHandler(content_url, contents[3])     # 处理超链接指向

            imgs = randomImg(contents[3])                        # 获取前三张图片
            contents = [*contents[:4], *imgs, brief(contents[3]), content_url, contents[4]]
            contents = spaceHandler(contents, [0, 1, 2, 7])

            if db.cursorIsClose():
                log.logMsg(LogType.error, "[filterContentInfoFunc] cursor already closed")
                return SpiderResType.cursorClose

            if contents[4]:
                imgname = str(uuid.uuid1()) + ".jpg"
                if thumbnail.saveThumbnail(contents[4], imgname):
                    contents[4] = imgname
                else:
                    contents[4] = ""

            db.callproc('dataInsert_proc', contents)
            log.logMsg(LogType.success, "[filterContentInfoFunc] %s" % content_url)
        else:
            log.logMsg(LogType.partialNone, "[filterContentInfoFunc] %s's title or content is None."%content_url, website_id, content_url)
            return SpiderResType.unrecognized
    except Exception as e:
        if type(e) is not queue.Empty:
            log.logMsg(LogType.error, "[filterContentInfoFunc] %s %s" % (content_url, traceback.format_exc()))
            return SpiderResType.otherError
    return SpiderResType.success


class QueryWebsiteUrlThread(threading.Thread):
    """
    @summary: 从数据库中获取待爬虫的网站地址
    """

    def __init__(self):
        super(QueryWebsiteUrlThread, self).__init__()


    def initWebsite_delay_dict(self, record):
        """
        @summary: 初始化网站的等待更新时间
        :param record: 网站记录（id, url, xpath, delay_time）
        :return:
        """
        if not Cache.keyExist(cache.websiteDelay_dict, record[0]):
            Cache.setDict(cache.websiteDelay_dict, record[0], record[-1])


    def putRecord(self, record):
        """
        @summary: 把record添加到正在等待的网站队列中
        """
        website_id, website_url, xpath = record[:3]
        if not Cache.listItemExist(cache.workingWebsite_list, website_id) and \
                not Cache.keyExist(cache.unrecognized_websiteUrl_dict, website_id):
            Cache.appendList(cache.workingWebsite_list, website_id)
            Cache.putQueue(cache.websiteUrl_queue, (website_id, website_url, xpath))
            sleep_time = Cache.getDict(cache.websiteDelay_dict, website_id)
            for i in range(int(sleep_time)):
                if global_EXIT: return
                time.sleep(1)
            Cache.removeList(cache.workingWebsite_list, website_id)


    def run(self):
        while not global_EXIT:
            try:
                if Cache.qempty(cache.websiteUrl_queue):
                    records = mysql.Mysql.queryWebsiteUrl()
                    for record in records:  # record: id,url,xpath,detail,delay_time
                        record = [str(item) for item in record]
                        self.initWebsite_delay_dict(record)
                        t = threading.Thread(target=self.putRecord, args=(record,))
                        t.setDaemon(True)
                        t.start()

            except Exception as e:
                log.logMsg(LogType.error, "[QueryWebsiteUrlThread] %s" % (traceback.format_exc()))
            for i in range(60):
                if global_EXIT: break
                time.sleep(1)


class FilterContentUrlThread(threading.Thread):
    """
    @summary: 爬取网站首页的内容地址
    """
    def __init__(self):
        super(FilterContentUrlThread, self).__init__()


    def run(self):
        while not global_EXIT:
            website_url = ""
            try:
                website_id, website_url, xpath = Cache.getQueue(cache.websiteUrl_queue, False)
                if not filterContentUrlFunc(website_id, website_url, xpath):
                    Cache.setDict(cache.unrecognized_websiteUrl_dict, website_id, (website_url, xpath))
            except Exception as e:
                if type(e) is not queue.Empty:
                    log.logMsg(LogType.error, "[FilterContentUrlThread.freshHandler] %s %s"%(website_url, traceback.format_exc()))
                else:
                    for i in range(10):
                        if global_EXIT: break
                        time.sleep(1)


class FilterContentInfoThread(threading.Thread):
    """
    @summary: 获取内容信息
    """
    def __init__(self):
        super(FilterContentInfoThread, self).__init__()

    def run(self):
        while not global_EXIT:
            url = ""
            try:
                website_id, url = Cache.getQueue(cache.freshContentUrl_queue, False)
                res = filterContentInfoFunc(website_id, url)
                if res == SpiderResType.success or res == SpiderResType.alreadyExist:
                    Cache.appendList(cache.oldContent_list, url)
                else:
                    Cache.setDict(cache.unrecognized_contentUrl_dict, url, website_id)
            except Exception as e:
                if type(e) is not queue.Empty:
                    log.logMsg(LogType.error, "[FilterContentInfoThread] %s %s" % (url, traceback.format_exc()))


class UnrecognizedWebsiteUrl_Thread(threading.Thread):
    def __init__(self):
        super(UnrecognizedWebsiteUrl_Thread, self).__init__()


    def run(self):
        while not global_EXIT:
            website_url = ""
            if not Cache.dempty(cache.unrecognized_websiteUrl_dict):
                try:
                    website_id = Cache.randomKey(cache.unrecognized_websiteUrl_dict)
                    if not website_id:
                        for i in range(30):
                            if global_EXIT: break
                            time.sleep(1)
                            continue

                    website_url, xpath = Cache.getDict(cache.unrecognized_websiteUrl_dict, website_id)
                    if (website_id, website_url, xpath):
                        Cache.removeDict(cache.unrecognized_websiteUrl_dict, website_id)

                except Exception as e:
                    log.logMsg(LogType.error, "[FilterContentUrlThread.unrecognizedHandler] %s %s" % (website_url, traceback.format_exc()))


class UnrecognizedContentUrl_Thread(threading.Thread):
    def __init__(self):
        super(UnrecognizedContentUrl_Thread, self).__init__()

    def run(self):
        while not global_EXIT:
            url = ""
            try:
                url = Cache.randomKey(cache.unrecognized_contentUrl_dict)
                if url:
                    website_id = Cache.getDict(cache.unrecognized_contentUrl_dict, url)
                    res = filterContentInfoFunc(website_id, url)
                    if res == SpiderResType.success or res == SpiderResType.alreadyExist:
                        Cache.removeDict(cache.unrecognized_contentUrl_dict, url)
                        Cache.appendList(cache.oldContent_list, url)
                for i in range(300):
                    if global_EXIT: break
                    time.sleep(1)
            except Exception as e:
                log.logMsg(LogType.error, "[FilterContentInfoThread.freshHandler] %s %s" % (url, traceback.format_exc()))


def initdb():
    """
    @summary: 清空redis中的数据
    """
    Cache.flushdb(cache.websiteDelay_dict)
    Cache.flushdb(cache.workingWebsite_list)
    Cache.flushdb(cache.websiteUrl_queue)
    Cache.flushdb(cache.oldContent_list)
    Cache.flushdb(cache.freshContentUrl_queue)
    Cache.flushdb(cache.log_queue)
    Cache.flushdb(cache.unrecognized_websiteUrl_dict)
    Cache.flushdb(cache.unrecognized_contentUrl_dict)
    Cache.flushdb(cache.globalArgs_dict)


def initGlobalArgs():
    """
    @summary:  初始化全局变量
    """
    Cache.setDict(cache.globalArgs_dict, "LogThread_EXIT", False)
    Cache.setDict(cache.globalArgs_dict, "global_EXIT", False)


def initContentUrl_dict():
    """
    @summary: 初始化去重列表
    """
    items = mysql.Mysql.queryContentUrl()
    for item in items:
        Cache.appendList(cache.oldContent_list, item[0])


def saveWebsiteDelaytime():
    """
    @summary: 保存网站爬取延迟到数据库中
    """
    try:
        for website_id in Cache.keys(cache.websiteDelay_dict):
            delaytime = Cache.getDict(cache.websiteDelay_dict, website_id)
            db.saveDelay_time(website_id, delaytime)
    except Exception as e:
        log.logMsg(LogType.error, "[saveWebsiteDelaytime] %s" % (repr(e)))


def main():
    thread_count = 3
    pre_threads = []

    initdb()                                            # 初始化redis数据库
    initGlobalArgs()
    initContentUrl_dict()                               # 初始化去重表

    log_thread = log.LogThread()                        # 启动日志记录线程
    log_thread.start()

    QueryWebsiteUrl_thread = QueryWebsiteUrlThread()    # 启动读取网站地址线程
    QueryWebsiteUrl_thread.start()
    pre_threads.append(QueryWebsiteUrl_thread)

    filterContentUrl_thread = FilterContentUrlThread()  # 启动爬取内容地址线程
    filterContentUrl_thread.start()
    pre_threads.append(filterContentUrl_thread)

    for i in range(thread_count):
        thread = FilterContentInfoThread()
        thread.start()
        pre_threads.append(thread)

    unrecognizedWebsiteUrl_thread = UnrecognizedWebsiteUrl_Thread()
    unrecognizedWebsiteUrl_thread.start()
    pre_threads.append(unrecognizedWebsiteUrl_thread)

    unrecognizedContentUrl_thread = UnrecognizedContentUrl_Thread()
    unrecognizedContentUrl_thread.start()
    pre_threads.append(unrecognizedContentUrl_thread)


    while not global_EXIT: pass

    time.sleep(5)

    saveWebsiteDelaytime()              # 保存各网站的延迟时间

    for t in pre_threads:
        t.join()

    log.logMsg(LogType.success, "--------------------bye---------------------\n")
    while not Cache.qempty(cache.log_queue): pass  # 等待把所有日志写到文件中
    Cache.setDict(cache.globalArgs_dict, "LogThread_EXIT", True)
    log_thread.join()

    if db: db.dispose()


def show_delay_time():
    """
    @summary: 显示各网站的爬取延迟
    """
    records = []
    keys = Cache.keys(cache.websiteDelay_dict) or []
    for website_id in keys:
        record = mysql.Mysql.queryWebsiteUrl(website_id)    # id,url,xpath,detail,delay_time
        records.append((record[0][0], record[0][3] or record[0][1], Cache.getDict(cache.websiteDelay_dict, website_id)))
    headers = ["id", "url", "delay-time(s)"]
    print(tabulate(records, headers=headers))


def content_count():
    """
    @summary: 显示已爬取的内容地址数量
    """
    print("content'count: %s"%(Cache.listLength(cache.oldContent_list)))


def resetDelay_time():
    """
    @summary: 重置各网站的爬取延迟
    """
    db = None
    try:
        db = mysql.Mysql()
        for website_id in Cache.keys(cache.websiteDelay_dict):
            record = Cache.getDict(cache.websiteDelay_dict, website_id)
            Cache.setDict(cache.websiteDelay_dict, website_id, (record[0], 0))
            db.saveDelay_time(website_id, 0)
    except Exception as e:
        log.logMsg(LogType.error, "[saveWebsiteDelaytime] %s" % (repr(e)))
    finally:
        if db: db.dispose()


def command(cmd):
    cmd = cmd.lower()
    if cmd == "delay-time" or cmd == "dt":
        show_delay_time()
    elif cmd == "content-count" or cmd == "cc":
        content_count()
    elif cmd == "reset-delay-time" or cmd == "rdt":
        resetDelay_time()


if __name__ == '__main__':
    print("* Started WeNeW_Spider-programe...")
    thread = threading.Thread(target=main)
    thread.setDaemon(True)
    thread.start()
    while True:
        cmd = input(">>")
        if cmd.lower() == "stop":
            global_EXIT = True
            Cache.setDict(cache.globalArgs_dict, "global_EXIT", True)
            print("* Waiting for the WeNeW_Spider-programe to end...")
            thread.join()
            print("* WeNeW_Spider-programe closed successfully!")
            break
        else:
            command(cmd)