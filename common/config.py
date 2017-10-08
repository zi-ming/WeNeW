import platform

# ------------------ OTHER ------------------
chromedriver = r"..\chromedriver.exe"

system = platform.system()

oa_domain = ["top.aiweibang.com","mp.weixin.qq.com",]

use_oa_proxy = True
use_comm_proxy = True
use_chrome_proxy = False
global_Chrome = False

retry_times = 5

# ------------------ REDIS ------------------
if system == "Linux":
    redis_host = mysql_host = '127.0.0.1'
else:
    redis_host = mysql_host = "192.168.121.196"

redis_port = 6379
availale_db = 0
trash_db = 2

# ------------------ MYSQL ------------------
mysql_user = 'root'
mysql_passwd = 'root'
mysql_db = 'wenew'
mysql_port = 3306
mysql_charset = 'utf8'
mysqlConfig = {'host': mysql_host, 'user': mysql_user, 'passwd': mysql_passwd,
               'db': mysql_db, 'port': mysql_port,'charset': mysql_charset}