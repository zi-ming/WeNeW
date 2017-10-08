"""
筛选出可用的ip代理
"""


import threading
import telnetlib
from IPProxyPool.config import *
from IPProxyPool.IPProxyRedis.Redis import Redis_Client

original_redis_client = Redis_Client(db=original_db)
available_redis_client = Redis_Client(db=availale_db)
trash_redis_client = Redis_Client(db=trash_db)


available_Exit = False


def isAvailable(ip, port, timeout = 2):
    """
    @summary: 验证ip代理是否可用
    :param ip:      ip代理
    :param port:    端口
    :param timeout: 验证超时时间
    :return:        boolean
    """
    try:
        telnetlib.Telnet(ip, port, timeout)
        return True
    except:
        return False


def main():
    expire = available_minexpire
    while not available_Exit:
        if original_redis_client.qsize(queue_name) > 0:
            ip, port = original_redis_client.brpop(queue_name, timeout=1)
            if not ip or not port: continue
            if isAvailable(ip, port):
                if available_redis_client:
                    available_redis_client.appendIPProxy(ip, port, expire)
                    expire += 2
                    if expire > available_maxexpire:
                        expire = available_minexpire
            else:
                if trash_redis_client:
                    trash_redis_client.appendIPProxy(ip, port, 3600)    # 保质期1小时


def command(cmd):
    if cmd == "available-count" or cmd == "ac":
        print("* Available key's count: %s" % available_redis_client.keysCount())
    elif cmd == "trash-count" or cmd == "tc":
        print("* Trash key's count: %s" % trash_redis_client.keysCount())

if __name__ == '__main__':
    thread_count = 30
    thread_list = []
    for i in range(thread_count):
        t = threading.Thread(target=main)
        t.setDaemon(True)
        t.start()
        thread_list.append(t)

    print("* Started Available-program ...")
    while True:
        cmd = input(">>").lower()
        if cmd == "stop":
            print("* Waiting for the Available-program to end ...")
            available_Exit = True
            for thread in thread_list:
                thread.join()
            print("* Available-programe closed successfully!")
            break
