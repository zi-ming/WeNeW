import redis
from IPProxyPool.config import *


class Redis_Client(object):
    def __init__(self, db, host="",port = ""):
        if not host: host = redis_host
        if not port: port = redis_port
        self.client = redis.Redis(host = host, port=port, db=db)


    def lpush(self, name, val):
        self.client.lpush(name, val)


    def brpop(self, name, timeout = 1):
        res = self.client.brpop(name, timeout)
        if res:
            try:
                res = res[1].decode("ascii")
                res = eval(res)
                return res
            except:
                return res
        return None, None


    def keysCount(self):
        return len(self.client.keys())


    def qsize(self, name):
        return self.client.llen(name)


    def randomIP(self):
        return self.client.randomkey().decode("utf8")


    def delete(self, name):
        self.client.delete(name)


    def shutdown(self):
        self.client.shutdown()


    def appendIPProxy(self, ip, port, expire=30):
        self.client.set(ip, port, ex=expire, nx=True)


    def get(self, name):
        res = self.client.get(name)
        if res:
            res = res.decode("utf8")
        return res