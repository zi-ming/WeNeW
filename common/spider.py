import urllib.parse
import os
import time
import urllib.request
import urllib.parse
import threading
import requests

from selenium import webdriver
from common.config import *
from common.Redis import Redis_client
from common import useragent
from scrapy.selector import Selector
from selenium.webdriver.chrome.options import Options
from queue import Queue

redis_client = Redis_client()

class SpiderResult(object):
    def __init__(self, page_source):
        self.page_source = page_source
        if page_source: self.selector = Selector(text=page_source)
        else:   self.selector = None


class Spider(object):
    @staticmethod
    def _isOA(url):
        """
        @summary: 判断是否是公众号
        """
        for domain in oa_domain:
            if domain in url:
                return True
        return False


    @staticmethod
    def _useProxy(url):
        """
        @summary: 判断是否使用代理
        """
        if use_oa_proxy and Spider._isOA(url):
            use_proxy = True
        elif use_comm_proxy and not Spider._isOA(url):
            use_proxy = True
        else:
            use_proxy = False
        return use_proxy


    @staticmethod
    def _getproxy():
        """
        @summary: 获取代理
        """
        ip, port = redis_client.getProxy()
        if ip and port:
            proxies = {'http': 'http://%s:%s' % (ip, port)}
            return proxies, ip, port
        return None, None, None


    @staticmethod
    def _pagesourceLegal(page_source):
        """
        @summary: 判断当前页面是否异常页面
        """
        if "Maximum number of open connections reached" in page_source or \
                        "Bad Request" in page_source or \
                        'placeholder="请输入验证码"' in page_source or \
                        'Internal Server Error' in page_source or \
                        'Please Authenticate' in page_source or \
                        '错误: 不能获取请求的 URL' in page_source or \
                        '无法访问此网站' in page_source:
            return False
        return True


    @staticmethod
    def _urllib_getPagesource(q, url):
        while q.empty():
            proxies, ip, port = None, None, None
            try:
                if Spider._useProxy(url):
                    proxies, ip, port = Spider._getproxy()
                if proxies:
                    proxy_handler = urllib.request.ProxyHandler(proxies)
                    opener = urllib.request.build_opener(proxy_handler)
                    opener.addheaders = [('User-agent', useragent.user_agent())]
                    res = opener.open(url, timeout=5)
                    page_source = res.read().decode("utf8")
                else:
                    req = urllib.request.Request(url, headers={"User-agent": useragent.user_agent()})
                    resp = urllib.request.urlopen(req)
                    page_source = resp.read().decode("utf8")

                if page_source and Spider._pagesourceLegal(page_source):
                    print(ip, port)
                    q.put(page_source)
            except Exception as e:
                if ip: redis_client.delProxy(ip)


    @staticmethod
    def urllib(url, args=""):
        """
        @summary: 使用urllib库获取页面源码
        """
        thread_count = 2
        page_source_q = Queue()
        threads = []
        try:
            if args:
                args = tuple([urllib.parse.quote(arg) for arg in args])
                url = url % args

            for i in range(thread_count):
                t = threading.Thread(target=Spider._urllib_getPagesource,
                                     args=(page_source_q, url))
                t.setDaemon(True)
                t.start()
                threads.append(t)

            for t in threads:
                t.join()

            return page_source_q.get(False)
        except Exception as e:
            return None


    @staticmethod
    def chromedriver(url, timeout=3):
        """
        @summary: 使用chromedriver获取页面源码
        """
        driver, ip, port = None, None, None
        for i in range(retry_times):
            try:
                if system == "Linux":
                    chrome_options = Options()
                    chrome_options.add_argument('--headless')
                    chrome_options.add_argument('--disable-gpu')
                else:
                    os.environ["webdriver.chrome.driver"] = chromedriver
                    chrome_options = webdriver.ChromeOptions()

                if use_chrome_proxy and Spider._useProxy(url):
                    proxies, ip, port = Spider._getproxy()

                if ip and port:
                    chrome_options.add_argument("--proxy-server=http://%s:%s" % (ip, port))

                if system == "Linux":
                    driver = webdriver.Chrome(chrome_options=chrome_options)
                else:
                    driver = webdriver.Chrome(chromedriver, chrome_options=chrome_options)

                driver.get(url)
                time.sleep(timeout)
                js = "document.body.scrollTop=1000"
                driver.execute_script(js)
                time.sleep(3)
                page_source = driver.page_source
                driver.close()
                driver.quit()
                if page_source and Spider._pagesourceLegal(page_source):
                    return page_source
            except Exception as e:
                if ip: redis_client.delProxy(ip)
                if driver:
                    driver.close()
                    driver.quit()
        return None


    @staticmethod
    def _requests_getPagesource(page_source_q, url, method, data, use_proxy=False):
        while page_source_q.empty():
            try:
                headers = {"User-agent": useragent.user_agent()}
                if use_oa_proxy:
                    proxies, ip, port = Spider._getproxy()

                if method == "POST":
                    res = requests.post(url, data=data, proxies=proxies, headers=headers)
                elif method == "GET":
                    res = requests.get(url, data=data, proxies=proxies, headers=headers)
                if res.status_code == 200:
                    print(ip, port)
                    page_source_q.put(res.text)
            except Exception as e:
                print(e)
                if ip:  redis_client.delProxy(ip)


    @staticmethod
    def requests(url, method, data):
        """
        @summary: 使用requests获取页面源码
        """
        try:
            thread_count = 2
            page_source_q = Queue()
            threads = []
            for i in range(thread_count):
                t = threading.Thread(target=Spider._requests_getPagesource,
                                     args=(page_source_q, url, method, data, Spider._useProxy(url)))
                t.setDaemon(True)
                t.start()
                threads.append(t)

            for t in threads:
                t.join()
            return page_source_q.get(False)
        except:
            return None