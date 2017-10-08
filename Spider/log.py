import threading
import os
import datetime
import queue

from Spider.cache import Cache
from Spider.config import LOG_DIR
from Spider.mysql import Mysql


cache = Cache()


class LogType(object):
    error = 0
    htmlSelectorNone = 1
    partialNone = 2
    success = 3
    other = 4


def logMsg(logType, msg, website_id = "", content_url = ""):
    """
    @summary:               把日志放到redis中（partialNone要放到数据库中）
    :param logType:         日志类型
    :param msg:             日志内容
    :param website_id:      网站id
    :param content_url:     内容url
    :return:
    """
    if logType == LogType.error and msg:
        msg = "》Error《:%s"% msg
    elif logType == LogType.htmlSelectorNone or logType == LogType.partialNone:
        msg = "？Warning？:%s"%msg
    elif logType == LogType.success:
        msg = "【Success】:%s"%msg
    else:
        msg = "--Other--:%s"%msg
    if logType == LogType.partialNone:
        Mysql.writeWebsiteMsg(website_id, content_url)
    Cache.putQueue(cache.log_queue, msg)


class LogThread(threading.Thread):
    index = 1
    def __init__(self):
        super(LogThread, self).__init__()

    def getFilename(self):
        """
        @summary: 按日期生成日志文件名
        """
        filename = "%s_%s.log"%(datetime.datetime.now().strftime("%Y%m%d"), self.index)
        filename = os.path.join(os.path.join(os.getcwd(), LOG_DIR), filename)
        return filename

    def run(self):
        while not Cache.getDict(cache.globalArgs_dict, "LogThread_EXIT"):
            try:
                info = Cache.getQueue(cache.log_queue, False)
                if os.path.exists(self.getFilename()):
                    log_size = os.path.getsize(self.getFilename())/1024/1024    # 日志大小超过1M时另建新的日志文件
                    if log_size > 1:
                        self.index += 1
                with open(self.getFilename(), 'a') as f:
                    info += '<%s>\n'%(datetime.datetime.now().strftime("%H:%M:%S"))
                    f.write(info)
            except Exception as e:
                if type(e) is not queue.Empty:
                    print("Log Error: %s"%e)
