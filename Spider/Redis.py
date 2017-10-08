import redis
from Spider.config import *


class Redis_client(object):
    def __init__(self, db, host="", port=""):
        if not hasattr(Redis_client, "instance") or Redis_client.instance!=db:
            if not host: host = redis_host
            if not port: port = redis_port
            Redis_client._createbool(host, port, db)
        self._connection = redis.Redis(connection_pool=Redis_client.pool)


    @staticmethod
    def _createbool(host, port, db):
        Redis_client.instance = db
        Redis_client.pool = redis.ConnectionPool(
            host = host,
            port = port,
            db = db
        )


    def randomkey(self):
        res = self._connection.randomkey()
        return res or None


    def delete(self, name):
        self._connection.delete(name)


    def lpush(self, name, val):
        return self._connection.lpush(name, val)


    def brpop(self, name, timeout=1):
        res = self._connection.blpop(name, timeout=timeout)
        return res and res[1] or None

    def set(self, name, val):
        self._connection.set(name=name, value=val)


    def get(self, name):
        res = self._connection.get(name)
        return res


    def llen(self, name):
        return self._connection.llen(name)


    def keys(self):
        try:
            return [item.decode("utf8") for item in self._connection.keys()]
        except:
            try:
                return [item.decode("ascii") for item in self._connection.keys()]
            except:
                return [item for item in self._connection.keys()]


    def flushdb(self):
        self._connection.flushdb()