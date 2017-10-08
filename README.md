# **wenew** 
--订阅你想订阅

## 目录
* [运行环境](#运行环境)
* [背景介绍](#背景介绍)
* [项目介绍](#项目介绍)
* [技术说明](#技术说明)
* [使用说明](#使用说明)
* [bug](#bug)
* [项目感言](#项目感言)

<a name="运行环境"></a>
## 开发环境
windows7 or Ubuntu0.16 均可<br>
Django==1.11.2<br>
Python==3.6<br>
Mysql==<br>

<a name="背景介绍"></a>
## 背景介绍
<p>因为平时有逛IT博客、论坛以及一些个人网站的习惯，从中可以获取到各种资讯，但是每次都要切换到各个网站才能看到相应的资讯，感觉比较繁琐，所以在大三暑假开始的时候就有要做一个能够订阅各种网站的项目，但是因为各种原因，一直拖到暑假结束时才开始动手。</p>

<a name="项目介绍"></a>
## 项目介绍
<p>
该项目名称为：WeNeW<br>
　　除了用户注册登陆这些基本功能外，该项目的主要功能是实现对网站的订阅，用户在订阅页面输入要订阅的网站地址，然后设置网站的订阅策略，即可实现该网站的订阅，当然也可以对网站取消订阅。<br>　　系统会定时根据用户设置的订阅策略，爬取网站的信息，如果用户设置的订阅策略不能爬取网站资讯或者网站的爬取策略不完整，系统也会反馈给用户，好让用户完善策略，从而尽可能地实现对网站资讯的100%抓取。<br>
　　所有爬取到的资讯都会显示在网站的主页面上，用户登陆后即可看到订阅网站的最新资讯。
</p>

<a name="技术说明"></a>
## 技术说明
<p>
　　该网站是用Django实现的，其中也涉及到 HTML + CSS + JS，爬虫、Mysql、Redis等技术，其中 JS 和爬虫相对比较重要，因为前端的订阅策略设置主要是通过JS实现的，而网站资讯的爬取主要通过Python爬虫来实现。<br>
　　爬虫端没有使用Scrapy框架，也没有使用Scrapy-Redis分布式框架，而是通过多线程配合chromedriver，urllib和代理进行页面爬取，之所以没有使用Scrapy框架，因为要爬取的网站是“动态”的，用户随时可能进行订阅或取消订阅，爬虫端要经常从数据库中读取订阅的网站，而Scrapy不能动态地从数据库中获取起始URL（至少我找不到相关的教程，Scrapy-Redis好像可以动态设置起始URL），所以才选用了“多线程 + chromedriver + urllib + 代理”的爬取方式。<br>
　　因为爬取网站过程中可能会出现重复爬取的情况，所以Redis主要用来做缓存，已爬取的页面链接会存到Redis数据库中，异常的页面链接也会存到Redis对应的数据库中，每次爬取前都会对页面地址进行判断，看链接是否在这两个数据库中，若不存在，才进行爬取。因为爬虫端使用的是多线程技术，所以Redis还用来暂存日志信息，各线程把日志信息放到Redis数据库中，日志线程会不断地读取数据库的日志信息，写到本地文件里。除此之外，Redis还缓存全局信号，当管理员在爬虫命令界面输入stop来停止爬虫程序时，系统会设置全局信号，来安全正确地退出所有线程，当所有线程执行完当前正在执行的任务后，即可退出爬虫程序，退出所花时间可能很快可能很慢，如果有一个线程正在通过chromedriver爬取一个网站，而网站的加载速度比较慢，那么退出时间可能要相对久一点。<br>
</p>

![image](https://github.com/zi-ming/README_PIC/raw/master/wenew/2017-10-07_200438.png)

<a name="使用说明"></a>
## 使用说明
* 所有操作需要在用户登陆的前提下进行。
* 如果用户要订阅网站，需要知道网站资讯首页的地址，比如我要订阅“虎嗅”网，虎嗅网的资讯首页地址为：https://www.huxiu.com/
那么用户登陆WeNeW后，点击左上方的`订阅网站`，出现以下界面：
![](https://github.com/zi-ming/README_PIC/raw/master/wenew/2017-10-08_113025.png)
* 输入虎嗅首页地址后，会跳转到虎嗅首页：
![](https://github.com/zi-ming/README_PIC/raw/master/wenew/2017-10-08_151340.png)
* 点击资讯内容链接，然后点击左边工具栏的提交，即内容链接的订阅策略设置：
![](https://github.com/zi-ming/README_PIC/raw/master/wenew/2017-10-08_151420.png)
* 点击提交后，前端会自动跳转到刚刚的资讯链接，选择内容标题区域，然后点击左边工具栏中的标题，即实现内容标题的策略设置：
![](https://github.com/zi-ming/README_PIC/raw/master/wenew/2017-10-08_151626.png)
* 作者和时间的订阅策略设置同上，都是先选择对应的内容区域，然后点击工具栏对应的属性进行确认：
![](https://github.com/zi-ming/README_PIC/raw/master/wenew/2017-10-08_154121.png)
* 内容的策略设置与上面的稍有区别，要先点击工具栏的内容按钮，然后选择对应的区域，前端会根据用户选择的区域，自动筛选出其中的内容，显示在右边的页面上，当用户设置好以后，点击`锁定`即可完成内容策略的设置，最终点击`完成`提交到服务器，服务器会根据用户的订阅以及相应的订阅策略进行信息爬取，最新的资讯会及时显示反馈给用户：
![](https://github.com/zi-ming/README_PIC/raw/master/wenew/2017-10-08_151815.png)
![](https://github.com/zi-ming/README_PIC/raw/master/wenew/2017-10-08_151843.png)
![](https://github.com/zi-ming/README_PIC/raw/master/wenew/2017-10-08_151919.png)
![](https://github.com/zi-ming/README_PIC/raw/master/wenew/2017-10-08_152031.png)
![](https://github.com/zi-ming/README_PIC/raw/master/wenew/2017-10-08_152110.png)
![](https://github.com/zi-ming/README_PIC/raw/master/wenew/2017-10-08_153218.png)
![](https://github.com/zi-ming/README_PIC/raw/master/wenew/2017-10-08_153242.png)
