#!/bin/bash

# 创建 logs 目录（如果不存在）
mkdir -p logs

source /root/anaconda3/etc/profile.d/conda.sh
conda activate rss
# 启动 run_rss.py 并将输出重定向到相应的日志文件
PYTHONUNBUFFERED=1 nohup python3 poker_gpt_flask.py > logs/poker.log 2>&1 &