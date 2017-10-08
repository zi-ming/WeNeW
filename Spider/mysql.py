import pymysql

from DBUtils.PooledDB import PooledDB
from Spider.config import *


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
        @summary:           调用存储过程
        :param procname:    存储过程名
        :param args:        存储过程参数（list-obj）
        :return:            所有结果
        """
        count = self._cursor.callproc(procname=procname, args=args)
        self.end("rollback" if count == 0 else "commit")
        return self._cursor.fetchall()


    def execute(self, sql, num=0):
        """
        @summary:       执行sql语句
        :param sql:     sql语句
        :param num:     <1：返回所有；=1：返回一条记录；>1：返回指定条数
        :return:
        """
        count = self._cursor.execute(sql)
        if count > 0:
            if num == 1:
                records = self._cursor.fetchone()
            elif num > 1:
                records = self._cursor.fetchmany(num)
            else:
                records = self._cursor.fetchall()
        else:
            records = []
        return records


    def cursorIsClose(self):
        """
        @summary:   查询游标是否已经关闭
        """
        return self._cursor == None


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
    def query(sql, num = 0):
        """
        @summary:   同execute
        """
        db = Mysql()
        res = db.execute(sql, num)
        db.dispose()
        return res


    @staticmethod
    def queryWebsiteUrl(website_id = None):
        """
        @summary:   获取网站的id、url、xpath以及delay_time等信息
        """
        condition = ""
        if website_id:
            condition = " and sw.id=%s"%(website_id)

        return Mysql.query("select sw.id,url,xpath,detail,delay_time from Subpage_website sw inner join Subpage_website_xpath swx on sw.id=swx.website_id where is_activate=1%s"%condition)


    @staticmethod
    def queryContentXpath(website_id):
        """
        @summary:   根据网站id查询内容页面的xpath
        """
        return Mysql.query("select title_xpath,author_xpath,time_xpath,content_xpath,id from Subpage_xpath where website_id=%s"%(website_id))


    @staticmethod
    def queryContentUrl():
        """
        @summary:   获取所有内容的url
        """
        return Mysql.query("select url from Subpage_data")


    @staticmethod
    def articleExist(title, author):
        """
        @summary: 判断内容是否已经存在
        """
        sql = "select count(*) from Subpage_data where title='%s' and author='%s'"%(title, author)
        num = Mysql.query(sql, 1)[0]
        if int(num) == 0:
            return False
        return True


    @staticmethod
    def writeWebsiteMsg(website_id, content_url):
        """
        @summary:   记录网站订阅反馈信息
        """
        db = Mysql()
        db.callproc("writeWebsiteMsg_proc", (website_id, content_url))


    def saveDelay_time(self, id, delay_time):
        """
        @summary:   保存网站的延迟时间
        """
        sql = "update Subpage_website set delay_time=%s where id=%s"%(delay_time, id)
        return self.execute(sql)