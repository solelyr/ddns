import json

import requests

# test.py运行后会真实更新 Cloudflare DNS 到 test_ip，请了解后再运行
with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

API_TOKEN = config["api_key"]
ZONE_ID = config["zone_id"]
DOMAIN = config["domain"]
SUBDOMAIN = config["subdomain"]
RECORD_NAME = f"{SUBDOMAIN}.{DOMAIN}"
NEW_IP = config.get("test_ip", "8.8.8.8")

headers = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json"
}

# 获取 record_id
def get_record_id():
    url = f"https://api.cloudflare.com/client/v4/zones/{ZONE_ID}/dns_records"
    response = requests.get(url, headers=headers).json()

    for record in response["result"]:
        if record["name"] == RECORD_NAME:
            return record["id"]
    return None

# 更新 DNS 记录
def update_dns(record_id):
    url = f"https://api.cloudflare.com/client/v4/zones/{ZONE_ID}/dns_records/{record_id}"
    data = {
        "type": "A",
        "name": RECORD_NAME,
        "content": NEW_IP,
        "ttl": 120,
        "proxied": False
    }
    response = requests.put(url, headers=headers, json=data)
    return response.json()

record_id = get_record_id()

if record_id:
    print(f"获取到 DNS 记录 ID: {record_id}")
    result = update_dns(record_id)
    print(result)
else:
    print("Error: Record not found.")
