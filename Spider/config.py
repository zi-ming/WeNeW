import platform

# ------------------ OTHER ------------------
system = platform.system()

LOG_DIR = "logfiles"

chromedriver_timeout = 3
retry_times = 2

use_redis_cache = True
use_oa_proxy = True
use_comm_proxy = False
global_Chrome = False

oa_domain = ["top.aiweibang.com","mp.weixin.qq.com"]

# ------------------ REDIS ------------------
if system == "Linux":
    redis_host = mysql_host = '127.0.0.1'
else:
    redis_host = mysql_host = "192.168.121.196"

redis_port = 6379

availale_db = 0
trash_db = 2

websiteDelay_db = 6
workingWebsite_db = 7
websiteUrl_db = 8
oldContentUrl_db = 9
freshContentUrl_db = 10
unrecognized_contentUrl_db = 11
unrecognized_websiteUrl_db = 12
log_db = 13
globalArgs_db = 14

# ------------------ MYSQL ------------------
mysql_user = 'root'
mysql_passwd = 'root'
mysql_db = 'wenew'
mysql_port = 3306
mysql_charset = 'utf8'
mysqlConfig = {'host': mysql_host, 'user': mysql_user, 'passwd': mysql_passwd,
               'db': mysql_db, 'port': mysql_port,'charset': mysql_charset}


# ------------------ THUMBNAIL ------------------
chromedriver = r"..\chromedriver.exe"
if system == "Linux":
    Thumbnail_DIR = r"..\statics\Thumbnail"
else:
    Thumbnail_DIR = r"..\statics\Thumbnail"

thumbnail_size =  (200, 150)
thumbnail_standard = 3/4