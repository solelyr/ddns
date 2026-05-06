FROM python:3.11-slim

WORKDIR /app

# 先升级pip
RUN pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple

COPY requirements.txt .

# 安装依赖
RUN pip install \
    -i https://pypi.tuna.tsinghua.edu.cn/simple \
    --no-cache-dir \
    -r requirements.txt

COPY . .

#CMD ["python", "ddns_updater.py"]
CMD sh -c "while true; do python ddns_updater.py; sleep 600; done"