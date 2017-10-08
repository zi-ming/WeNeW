"""
采集代理IP
"""


import os
import time
from scrapy.selector import Selector
from selenium import webdriver
import threading
from IPProxyPool.IPProxyRedis.Redis import Redis_Client
from IPProxyPool.config import *
import requests
import re
from IPProxyPool.useragent import user_agent


original_redis_client = Redis_Client(db=original_db)
avaliable_redis_client = Redis_Client(db=availale_db)


proxy_EXIT = False


def getAvailableIP():
    try:
        ip = avaliable_redis_client.randomIP()
        port = avaliable_redis_client.get(ip)
        return ip, port
    except Exception as e:
        return None, None


def selector_with_chromeDriver(url, timeout = 40):
    """
    @summary: 使用chromeDriver爬取页面代理
    """
    # chrome_options = Options()
    # chrome_options.add_argument('--headless')
    # chrome_options.add_argument('--disable-gpu')
    # driver = webdriver.Chrome(chrome_options=chrome_options)

    os.environ["webdriver.chrome.driver"] = chromedriver
    ip, port = getAvailableIP()
    if ip and port:
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--proxy-server=http://%s:%s" % (ip, port))
        driver = webdriver.Chrome(chromedriver, chrome_options=chrome_options)
    else:
        driver = webdriver.Chrome(chromedriver)

    if driver:
        driver.get(url=url)
        time.sleep(timeout)
        html = driver.page_source
        driver.close()
        driver.quit()
        return Selector(text=html), ip
    return None, ""


def selector_with_requests(url):
    """
    @summary: 使用requests爬取页面代理
    """
    try:
        ip, port = getAvailableIP()
        if not ip or not port:
            html = requests.get(url, headers = {"User-Agent": user_agent.user_agent()}).text
        else:
            proxies = {'http': 'http://%s:%s' % (ip, port)}
            html = requests.get(url, headers = {"User-Agent": user_agent.user_agent()},proxies=proxies).text
        selector = Selector(text=html)
        return selector, ip
    except:
        return None, ""


# 代理地址以及对应的筛选规则
proxies = [
    # {"url": "http://www.kuaidaili.com/free/inha/%s/", "page_range": (1, 3),
    #  "get_selector_method": selector_with_chromeDriver,
    #  "xpaths": ["//tbody/tr", "./td[1]/text()", "./td[2]/text()", "./td[4]/text()"], "trs_limit": 0, "timeout": 10,
    #  "proto_mark": 'http'},
    {"url": "http://www.xicidaili.com/nn/%s", "page_range": (1, 3),
     "get_selector_method": selector_with_requests,
     "xpaths": ["//tbody/tr", "./td[2]/text()", "./td[3]/text()", "./td[6]/text()"], "trs_limit": 1, "timeout": 10,
     "proto_mark": 'http'},
    {"url": "https://www.us-proxy.org/", "page_range": (1, 2),
     "get_selector_method": selector_with_requests,
     "xpaths": ["//tbody/tr", "./td[1]/text()", "./td[2]/text()", "./td[7]/text()"], "trs_limit": 0, "timeout": 10,
     "proto_mark": 'no'},
    {"url": "http://www.ip3366.net/?stype=1&page=%s", "page_range": (1, 3),
     "get_selector_method": selector_with_requests,
     "xpaths": ["//tbody/tr", "./td[1]/text()", "./td[2]/text()", "./td[4]/text()"], "trs_limit": 0, "timeout": 10,
     "proto_mark": 'http'},
]


def proxy(url, page_range, get_selector_method, xpaths, trs_limit, timeout, proto_mark):
    while not proxy_EXIT:
        if avaliable_redis_client.keysCount() < available_minimum:
            for i in range(*page_range):
                if proxy_EXIT: break
                proxy_url = (page_range[1]-page_range[0])>1 and url%(i) or url
                selector, ip = get_selector_method(proxy_url)
                if selector is None: continue
                trs = selector.xpath(xpaths[0])
                if len(trs) <= trs_limit:
                    avaliable_redis_client.delete(ip)
                    continue
                print("* %s"%(len(trs)))
                for tr in trs:
                    try:
                        ip = tr.xpath(xpaths[1]).extract()[0]
                        port = tr.xpath(xpaths[2]).extract()[0]
                        proto = tr.xpath(xpaths[3]).extract()[0].lower()
                        if re.match("\d+\.\d+\.\d+\.\d+", ip) and re.match("\d+", port):
                            if original_redis_client and proto == proto_mark:
                                original_redis_client.lpush(queue_name, (ip,port))
                    except:pass
                time.sleep(timeout)


def main():
    threads = []
    for p in proxies:
        t = threading.Thread(target=proxy, kwargs=(p))
        t.setDaemon(True)
        t.start()
        threads.append(t)

    for thread in threads:
        thread.join()



if __name__ == '__main__':
    main_thread = threading.Thread(target=main)
    main_thread.setDaemon(True)
    main_thread.start()
    print("* Started IPProxy-program ...")
    while True:
        cmd = input(">>").lower()
        if cmd == "stop":
            print("* Waiting for the IPProxy-program to end ...")
            proxy_EXIT = True
            main_thread.join()
            print("* IPProxy-programe closed successfully!")
            break