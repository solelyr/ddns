# DDNS脚本部署手册

# Linux环境
> ###### 1.下载源代码，
> ###### 2.修改配置文件：config.example.json，并重命名为config.json,调整域名、APIkey等，修改：requirements.txt，按实际情况判断是否需要删除 pywin32==311、pywin32-ctypes==0.2.3 两行内容
> ###### 3.安装python虚拟环境，python3 -m venv venv 如果提示没有 venv：sudo apt install python3-venv -y
> ###### 4.激活虚拟环境：source venv/bin/activate
> ###### 5.运行测试：python ddns_updater.py
> ###### 6.创建 service文件 sudo vim /etc/systemd/system/ddns.service 
```
[Unit]
Description=DDNS Updater

[Service]
Type=oneshot
ExecStart=/usr/bin/python3 /home/solelyr/ddns/ddns_updater.py
WorkingDirectory=/home/solelyr/ddns
User=root
```

> ###### 7.创建 timer文件：sudo vim /etc/systemd/system/ddns.timer
```
[Unit]
Description=Run DDNS every 10 minutes

[Timer]
OnBootSec=1min
OnUnitActiveSec=10min
Unit=ddns.service

[Install]
WantedBy=timers.target
```
> ###### 8.启动定时器 
```
sudo systemctl daemon-reload
sudo systemctl enable ddns.timer
sudo systemctl start ddns.timer
```
> ###### 9.查看运行状态：systemctl list-timers
> ###### 10.查看日志：journalctl -u ddns.service

# Win环境
> ##### 1.编译
```
pyinstaller --onefile --noconsole ddns_updater.py
```
> ##### 2.在ddns_updater.exe 修改配置文件：config.example.json，并重命名为config.json,调整域名、APIkey等，复制到ddns_updater.exe同级目录，新建log目录

# Docker
> ##### 编译推送
```
docker buildx build `
--platform linux/amd64,linux/arm64 `
-t solelyrzz/ddns-cloudflare:latest `
--push .

docker builder prune -f --缓存清除
```
> ##### 使用
> ###### 1.修改配置文件：config.example.json，并重命名为config.json,调整域名、APIkey等，新建log目录
> ###### 2.通过
> linux：
    docker run -d \
        --name ddns-cloudflare \
        --restart always \
        -e TZ=Asia/Shanghai \
        -v $(pwd)/config.json:/app/config.json \
        -v $(pwd)/logs:/app/logs \
        solelyrzz/ddns-cloudflare:latest

> Windows PowerShell
    docker run -d `
        --name ddns-cloudflare `
        --restart always `
        -e TZ=Asia/Shanghai `
        -v ${PWD}/config.json:/app/config.json `
        -v ${PWD}/logs:/app/logs `
        solelyrzz/ddns-cloudflare:latest
> 
> ###### 3.通过docker-compose运行，下载源码或复制源码中docker-compose.yml文件直接运行 docker compose up -d;