import logging.handlers
import requests
import json
import os
import sys

# 创建 logs 目录（如果不存在）
LOG_DIR = "logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# 配置日志
logger = logging.getLogger("DDNS_Updater")
logger.setLevel(logging.DEBUG)  # 设置最低日志级别

# 创建一个按天切分的日志文件（每天新建一个日志文件）
log_file_path = os.path.join(LOG_DIR, "ddns.log")
file_handler = logging.handlers.TimedRotatingFileHandler(
    filename=log_file_path,  # 日志文件路径
    when="midnight",         # 每天午夜切换日志
    interval=1,              # 间隔 1 天
    backupCount=7,           # 保留最近 7 天的日志
    encoding="utf-8"
)
file_handler.setLevel(logging.DEBUG)  # 记录所有日志

# 创建控制台处理器（可选）
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)  # 仅在控制台显示 INFO 及以上级别日志

# 设置日志格式
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# 添加处理器到 logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# 读取 config.json
with open("config.json", "r") as f:
    config = json.load(f)

API_KEY = config["api_key"] # API key
EMAIL = config["email"]  # 邮箱
ZONE_ID = config["zone_id"] # 区域 ID
DOMAIN = config["domain"] # 主域名
SUBDOMAIN = config["subdomain"]  # 子域名
CHECK_IP_URL = config["check_ip_url"] # 域名检测地址

# 打包脚本 pyinstaller --onefile --noconsole ddns_updater.py

if os.name == "nt":
    import win32event
    import win32api
    import winerror

    mutex = win32event.CreateMutex(None, False, "Global\\DDNS_UPDATER_MUTEX")
    if win32api.GetLastError() == winerror.ERROR_ALREADY_EXISTS:
        sys.exit(0)
else:
    import fcntl

    LOCK_FILE = os.path.join(os.path.dirname(__file__), "ddns.lock")
    lock_file = open(LOCK_FILE, 'w')
    try:
        fcntl.flock(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except IOError:
        sys.exit(0)

# 获取公网IP
def get_public_ip():
    """获取当前公网 IP"""
    try:
        # url = "https://api-ipv4.ip.sb/ip"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
        }
        response = requests.get(CHECK_IP_URL, headers=headers, timeout=5)
        response.raise_for_status()  # 检查 HTTP 状态码
        return response.text.strip()
    except Exception as e:
        logger.error(f"获取公网 IP 失败: {e}")
        return None

# 获取 Cloudflare 当前解析的 IP
def get_cloudflare_dns_record():
    url = f"https://api.cloudflare.com/client/v4/zones/{ZONE_ID}/dns_records?name={SUBDOMAIN}.{DOMAIN}"
    headers = {
        "X-Auth-Email": EMAIL,
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    response = requests.get(url, headers=headers)
    data = response.json()
    if data["success"] and data["result"]:
        return data["result"][0]["id"], data["result"][0]["content"]
    return None, None

# 更新 Cloudflare 解析
def update_dns_record(ip,record_id):
    """更新 Cloudflare DDNS 记录"""
    url = f"https://api.cloudflare.com/client/v4/zones/{ZONE_ID}/dns_records/{record_id}"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "type": "A",
        "name": SUBDOMAIN+"."+DOMAIN,
        "content": ip,
        "ttl": 120,
        "proxied": False
    }
    response = requests.put(url, headers=headers, json=data)
    return response.json()

# 主程序
if __name__ == "__main__":
    public_ip = get_public_ip()
    if not public_ip:
        logger.error("无法获取公网 IP")
        exit(1)
    logger.info(f"获取到的公网 IP:{public_ip}")

    record_id, current_ip = get_cloudflare_dns_record()
    if not record_id:
        logger.error("获取 Cloudflare 解析记录失败")
        exit(1)

    if current_ip == public_ip:
        logger.info(f"IP 未变更 ({public_ip})，无需更新")
    else:
        response = update_dns_record(public_ip, record_id)
        if response.get("success"):
            logger.info(f"Cloudflare DNS 更新成功: {public_ip}")
        else:
            logger.error(f"更新失败: {response}")
