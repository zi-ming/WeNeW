import pymysql
from DBUtils.PooledDB import PooledDB
from common.config import *


class Mysql(object):
    __pool = None
    def __init__(self):
        self._conn = Mysql.__getConn()
        self._cursor = self._conn.cursor()

    @staticmethod
    def __getConn():
        """
        @summary: 创建连接池
        """
        if Mysql.__pool is None:
            __pool = PooledDB(creator=pymysql, mincached=1, maxcached=20,
                              use_unicode = True, **mysqlConfig)
            return __pool.connection()


    def callproc(self, procname, args):
        """
        @summary: 调用存储过程
        """
        count = self._cursor.callproc(procname=procname, args=args)
        self.end("rollback" if count == 0 else "commit")
        return self._cursor.fetchall()


    def end(self, options='commit'):
        """
        @summary: 结束事务
        """
        if options=='commit':
            self._conn.commit()
        else:
            self._conn.rollback()


    def dispose(self, isEnd=True):
        """
        @summary: 释放连接池
        """
        if isEnd:
            self.end('commit')
        else:
            self.end('rollback')
        self._cursor.close()
        self._cursor = None
        self._conn.close()
        self._conn = None


    @staticmethod
    def queryNewList(user_id, latest_id, type, limit):
        """
        @summary: 获取新闻列表
        """
        db = Mysql()
        res = db.callproc("queryNewList_proc", (user_id, latest_id, type, limit))
        return res


    @staticmethod
    def queryWebsite(user_id):
        """
        @summary: 根据用户id查询订阅网站
        """
        db = Mysql()
        res = db.callproc("queryWebsite_proc", (user_id,))
        return res


    @staticmethod
    def cancleWebsiteSub(user_id, website_ids):
        """
        @summary: 根据用户类型，取消网站订阅
        """
        for website_id in website_ids:
            db = Mysql()
            db.callproc("cancleWebsiteSub_proc", (user_id, website_id))


    @staticmethod
    def clearMsg(user_id):
        """
        @summary: 清除用户的网站订阅反馈
        """
        db = Mysql()
        db.callproc("clearLog_proc", (user_id,))


    @staticmethod
    def queryWebsiteMsg(user_id):
        """
        @summary: 根据用户id查询用户网站订阅反馈
        """
        db = Mysql()
        res = db.callproc("queryWebsiteMsg_proc", (user_id,))
        return res