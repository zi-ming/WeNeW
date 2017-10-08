# **wenew** 
--订阅你想订阅

## 目录
* [运行环境](#运行环境)
* [背景介绍](#背景介绍)
* [项目介绍](#项目介绍)
* [技术说明](#技术说明)
* [使用说明](#使用说明)
* [代码运行](#代码运行)
* [BUG](#BUG)
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
　　该网站是用Django实现的，其中也涉及到 HTML + CSS + JS，Xpath，爬虫、Mysql、Redis等技术，其中 JS和爬虫相对比较重要，因为前端的订阅策略设置主要是通过JS实现的，而网站资讯的爬取主要通过Python爬虫来实现。<br>
　　爬虫端没有使用Scrapy框架，也没有使用Scrapy-Redis分布式框架，而是通过多线程配合chromedriver，urllib和代理进行页面爬取，之所以没有使用Scrapy框架，因为要爬取的网站是“动态”的，用户随时可能进行订阅或取消订阅，爬虫端要经常从数据库中读取订阅的网站，而Scrapy不能动态地从数据库中获取起始URL（至少我找不到相关的教程，Scrapy-Redis好像可以动态设置起始URL），所以才选用了“多线程 + chromedriver + urllib + 代理”的爬取方式。<br>
　　因为爬取网站过程中可能会出现重复爬取的情况，所以Redis主要用来做缓存，已爬取的页面链接会存到Redis数据库中，异常的页面链接也会存到Redis对应的数据库中，每次爬取前都会对页面地址进行判断，看链接是否在这两个数据库中，若不存在，才进行爬取。因为爬虫端使用的是多线程技术，所以Redis还用来暂存日志信息，各线程把日志信息放到Redis数据库中，日志线程会不断地读取数据库的日志信息，写到本地文件里。除此之外，Redis还缓存全局信号，当管理员在爬虫命令界面输入stop来停止爬虫程序时，系统会设置全局信号，来安全正确地退出所有线程，当所有线程执行完当前正在执行的任务后，即可退出爬虫程序，退出所花时间可能很快可能很慢，如果有一个线程正在通过chromedriver爬取一个网站，而网站的加载速度比较慢，那么退出时间可能要相对久一点。<br>
</p>

![image](https://github.com/zi-ming/README_PIC/raw/master/wenew/2017-10-07_200438.png)

<a name="使用说明"></a>
## 使用说明
* <p>所有操作需要在用户登陆的前提下进行。</p>
* <p>如果用户要订阅网站，需要知道网站资讯首页的地址，比如我要订阅“虎嗅”网，虎嗅网的资讯首页地址为：https://www.huxiu.com/
那么用户登陆WeNeW后，点击左上方的`订阅网站`，出现以下界面：</p>
![](https://github.com/zi-ming/README_PIC/raw/master/wenew/2017-10-08_113025.png)<br><br>
* <p>输入虎嗅首页地址后，会跳转到虎嗅首页：</p>
![](https://github.com/zi-ming/README_PIC/raw/master/wenew/2017-10-08_151340.png)<br><br>
* <p>点击资讯内容链接，然后点击左边工具栏的提交，即内容链接的订阅策略设置：</p>
![](https://github.com/zi-ming/README_PIC/raw/master/wenew/2017-10-08_151420.png)<br><br>
* <p>点击提交后，前端会自动跳转到刚刚的资讯链接，选择内容标题区域，然后点击左边工具栏中的标题，即实现内容标题的策略设置：</p>
![](https://github.com/zi-ming/README_PIC/raw/master/wenew/2017-10-08_151626.png)<br><br>
* <p>作者和时间的订阅策略设置同上，都是先选择对应的内容区域，然后点击工具栏对应的属性进行确认：</p>
![](https://github.com/zi-ming/README_PIC/raw/master/wenew/2017-10-08_154121.png)<br><br>
* <p>内容的策略设置与上面的稍有区别，要先点击工具栏的内容按钮，然后选择对应的区域，前端会根据用户选择的区域，自动筛选出其中的内容，显示在右边的页面上，当用户设置好以后，点击`锁定`即可完成内容策略的设置，最终点击`完成`提交到服务器，服务器会根据用户的订阅以及相应的订阅策略进行信息爬取，最新的资讯会及时显示反馈给用户：</p>
![](https://github.com/zi-ming/README_PIC/raw/master/wenew/2017-10-08_151815.png)
![](https://github.com/zi-ming/README_PIC/raw/master/wenew/2017-10-08_151843.png)
![](https://github.com/zi-ming/README_PIC/raw/master/wenew/2017-10-08_151919.png)
![](https://github.com/zi-ming/README_PIC/raw/master/wenew/2017-10-08_152031.png)
![](https://github.com/zi-ming/README_PIC/raw/master/wenew/2017-10-08_152110.png)
![](https://github.com/zi-ming/README_PIC/raw/master/wenew/2017-10-08_153218.png)
![](https://github.com/zi-ming/README_PIC/raw/master/wenew/2017-10-08_153242.png)

<a name="代码运行"></a>
## 代码运行
1、搭建好所需运行环境。
2、创建数据库：
```Mysql
CREATE DATABASE IF NOT EXISTS wenew DEFAULT CHARSET utf8 COLLATE utf8_general_ci;
```
3、修改`WeNeW/setting`、`common/config`、`Spider/config`中的Mysql地址，修改`common/config`，`IPProxyPool/config`，`Spider/config`中的Redis地址。
4、在项目根目录下运行以下命令实现模型迁移：
```python
python manage.py makemigrations
python manage.py migrate
```
5、运行项目根目录下的sql.sql中的sql语句。
6、依次运行`IPProxyPool/Available/Available.py`，`IPProxyPool/Spider/CollectIPProxy.py`来启动代理服务。
7、运行`Spider/WeNeW_Spider.py`，启动网站信息爬取服务。
8、在项目根目录下输入以下命令开启网站服务：
```python
python manage.py runserver 0.0.0.0:8000
```

<a name="BUG"></a>
## **BUG**
1、公众号订阅模块功能不完整。<br>
2、没有实现用户密码找回等功能。<br>
3、不是所有网站都能订阅，比如：[爱微帮](https://segmentfault.com/)、[36氪](http://36kr.com/)这些网站都不能订阅，日后有可能进行完善。<br>
4、只是对基础功能进行了测试，没有对安全进行测试。<br>
5、如果抓取的内容中存在视频，视频样式可能很丑，甚至视频无法正常播放。<br>
6、如果一个网站，内容页面结构和样式比较复杂繁多，像[博客园](https://www.cnblogs.com/pick/)这种几乎每个页面结构样式都不一样的，需要用户不断地对订阅策略进行完善，所以用户初期订阅后，可能会出现资讯内容显示不完整的情况。<br>
7、不兼容所有浏览器，建议配合chrome浏览器使用。<br>
8、该项目只有django自带的后台，没有一个数据更直观，功能更齐全的后台。<br>
9、在网站订阅过程中，页面跳转可能会比较久，甚至跳转失败或者页面的样式不能正常加载，如果跳转失败，请重新刷新，如果样式不能正常加载，也不妨碍网站的订阅。<br>



<a name="项目感言"></a>
## 项目感言
该项目除了能订阅一般的网站之外，还能订阅公众号，在网站订阅页面点击WebSite Url，就可以看到有Official Accounts的选项，选择Official Accounts可以实现公众号的订阅<br>

一开始是通过爬取搜狗的公众号的方式实现公众号信息的抓取，但是抓取次数多了，就会提示输入验证码，试过用IP代理来爬取，但是该网站的反爬机制做得太好了，用IP代理打不开公众号页面，所以使用IP代理这个方案直接就没用了，也试过用PIL+Tesseract来尝试识别验证码，从未成功过！！！试了好多办法，还是不行，最终放弃了通过搜狗微信公众号的方式，后来找到一个可以看公众号信息的网站：http://www.aiweibang.com/，一开始仿佛发现了新大陆，以为这个问题终于可以解决了，然后就
