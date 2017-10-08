import redis
from common.config import *


class Redis_client(object):
    def __init__(self):
        if not hasattr(Redis_client, 'pool'):
            Redis_client.createbool()
        self._connection = redis.Redis(connection_pool=Redis_client.pool)


    @staticmethod
    def createbool():
        """
        @summary: 创建连接池
        """
        Redis_client.pool = redis.ConnectionPool(
            host = redis_host,
            port = redis_port,
            db = availale_db
        )


    def getProxy(self):
        """
        @summary: 获取随机的代理ip
        """
        ip = self._connection.randomkey()
        if ip:
            port = self._connection.get(ip)
            if port:
                return ip.decode("utf8"), port.decode("utf8")
        return None, None


    def delProxy(self, ip):
        """
        @summary: 删除代理ip
        """
        self._connection.delete(ip)