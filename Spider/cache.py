import queue
import random

from Spider.config import *
from Spider.Redis import Redis_client
from queue import Queue


class Cache(object):
    _instance = None
    _queueName = "queue"
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Cache, cls).__new__(cls, *args, **kwargs)
            cls._instance._buildCache()
        return cls._instance


    def _buildCache(self):
        self.websiteDelay_dict = use_redis_cache and Redis_client(websiteDelay_db) or {}
        self.workingWebsite_list = use_redis_cache and Redis_client(workingWebsite_db) or []
        self.websiteUrl_queue = use_redis_cache and Redis_client(websiteUrl_db) or Queue()
        self.oldContent_list = use_redis_cache and Redis_client(oldContentUrl_db) or []
        self.freshContentUrl_queue = use_redis_cache and Redis_client(freshContentUrl_db) or Queue()
        self.unrecognized_contentUrl_dict = use_redis_cache and Redis_client(unrecognized_contentUrl_db) or {}
        self.unrecognized_websiteUrl_dict = use_redis_cache and Redis_client(unrecognized_websiteUrl_db) or {}
        self.log_queue = use_redis_cache and Redis_client(log_db) or Queue()
        self.globalArgs_dict = use_redis_cache and Redis_client(globalArgs_db) or {}


    @staticmethod
    def setDict(obj, name, val):
        """
        @summary: 设置字典key, val
        """
        if type(obj) is dict:
            obj[name] = val
        elif type(obj) is Redis_client:
            obj.set(name, val)
        else:
            raise TypeError


    @staticmethod
    def _outputFormat(data):
        """
        @summary: 格式化输出
        """
        try:
            data = eval(data)
            return data
        except:
            try:
                data = data.decode("utf-8")
                return data
            except:
                try:
                    data = data.decode("ascii")
                    return data
                except:
                    return data


    @staticmethod
    def getDict(obj, name):
        """
        @summary: 根据name从目标对象中获取对应的值
        """
        if type(obj) is dict:
            return obj[name]
        elif type(obj) is Redis_client:
            return Cache._outputFormat(obj.get(name))
        else:
            raise TypeError


    @staticmethod
    def dempty(obj):
        """
        @summary: 判断对象是否为空
        """
        return len(Cache.keys(obj)) == 0


    @staticmethod
    def keyExist(obj, name):
        """
        @summary: 从目标对象中判断name是否存在
        """
        if type(obj) is dict or type(obj) is Redis_client:
            return name in obj.keys()
        else:
            raise TypeError


    @staticmethod
    def keys(obj):
        """
        @summary: 获取目标对象的所有key
        """
        if type(obj) is dict or type(obj) is Redis_client:
            return obj.keys()
        else:
            raise TypeError


    @staticmethod
    def appendList(obj, name):
        """
        @summary: 追加name到目标对象中
        """
        if type(obj) is list:
            obj.append(name)
        elif type(obj) is Redis_client:
            Cache.setDict(obj, name, "")
        else:
            raise TypeError


    @staticmethod
    def removeList(obj, name):
        """
        @summary: 删除目标对象中的name
        """
        if type(obj) is list:
            obj.remove(name)
        elif type(obj) is Redis_client:
            obj.delete(name)
        else:
            raise TypeError


    @staticmethod
    def listItemExist(obj, name):
        """
        @summary: 判断目标对象中是否存在name
        """
        if type(obj) is list:
            return name in obj
        elif type(obj) is Redis_client:
            return Cache.keyExist(obj, name)
        else:
            raise TypeError


    @staticmethod
    def listLength(obj):
        """
        @summary: 获取目标对象的长度
        """
        if type(obj) is list:
            return len(obj)
        elif type(obj) is Redis_client:
            return len(Cache.keys(obj))
        else:
            raise TypeError


    @staticmethod
    def putQueue(obj, val):
        """
        @summary: 把val放入目标对象中
        """
        if type(obj) is Queue:
            obj.put(val)
        elif type(obj) is Redis_client:
            obj.lpush(Cache._queueName, val)
        else:
            raise TypeError


    @staticmethod
    def getQueue(obj, block):
        """
        @summary: 从目标对象中获取一个元素
        """
        if type(obj) is Queue:
            return obj.get(block)
        elif type(obj) is Redis_client:
            val = obj.brpop(Cache._queueName, 0 if block else 1)
            if val:
                return Cache._outputFormat(val)
            else:
                if not block:
                    raise queue.Empty
        else:
            raise TypeError


    @staticmethod
    def qempty(obj):
        """
        @summary: 判断目标对象长度为否为0
        """
        if type(obj) is Queue:
            return obj.empty()
        elif type(obj) is Redis_client:
            return obj.llen(Cache._queueName)==0
        else:
            raise TypeError


    @staticmethod
    def flushdb(obj):
        """
        @summary: 清空redis数据库
        """
        if type(obj) is Redis_client:
            obj.flushdb()


    @staticmethod
    def randomKey(obj):
        """
        @summary: 从目标对象中随机获取一个值
        """
        if type(obj) is dict:
            return random.choice(obj.keys())
        if type(obj) is list:
            return random.choice(obj)
        elif type(obj) is Redis_client:
            return Cache._outputFormat(obj.randomkey())


    @staticmethod
    def removeDict(obj, name):
        """
        @summary: 移除目标对象中的键name的项
        """
        try:
            if type(obj) is dict:
                del obj[name]
            elif type(obj) is Redis_client:
                obj.delete(name)
        except:
            pass