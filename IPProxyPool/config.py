import platform

system = platform.system()

redis_host = "192.168.121.196"
redis_port = 6379
original_db = 1
availale_db = 0
trash_db = 2

queue_name = "queue"
available_minexpire = 120
available_maxexpire = 300
available_minimum = 80


chromedriver = r"E:\Code\PythonCode\chromedriver.exe"