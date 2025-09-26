#!/bin/bash

# 快速启动脚本
# 用于开发环境快速启动机器人

set -e

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🚀 启动 Telegram 转发机器人...${NC}"

# 检查配置文件
if [ ! -f .env ]; then
    echo "❌ 未找到 .env 配置文件"
    echo "请先复制 config.env.example 为 .env 并配置 BOT_TOKEN"
    echo "cp config.env.example .env"
    echo "nano .env"
    exit 1
fi

# 检查 BOT_TOKEN
if grep -q "BOT_TOKEN=your_bot_token_here" .env || grep -q "BOT_TOKEN=$" .env; then
    echo "❌ 请先在 .env 文件中配置 BOT_TOKEN"
    exit 1
fi

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "🔧 激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo "📥 安装依赖..."
pip install -r requirements.txt

# 启动机器人
echo -e "${GREEN}✅ 启动机器人...${NC}"
python bot.py
