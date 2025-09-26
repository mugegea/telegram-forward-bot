#!/bin/bash

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# 检查是否为 root 用户
if [[ $EUID -ne 0 ]]; then
   print_error "此脚本需要 root 权限运行"
   print_info "请使用: sudo bash install.sh"
   exit 1
fi

# 检查系统类型
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    print_error "此脚本仅支持 Linux 系统"
    exit 1
fi

print_info "开始安装 Telegram 转发机器人..."

# 检查必要的命令
for cmd in git python3 pip3; do
    if ! command -v $cmd &> /dev/null; then
        print_info "安装系统依赖..."
        apt update
        apt install -y git python3 python3-pip python3-venv curl
        break
    fi
done

# 设置默认仓库 URL
DEFAULT_REPO_URL="https://github.com/mugegea/telegram-forward-bot.git"
REPO_URL=""

if [ -z "$1" ]; then
    echo -n "请输入 GitHub 仓库 URL (直接回车使用默认: $DEFAULT_REPO_URL): "
    read REPO_URL
    if [ -z "$REPO_URL" ]; then
        REPO_URL="$DEFAULT_REPO_URL"
    fi
else
    REPO_URL="$1"
fi

print_info "克隆仓库: $REPO_URL"
cd /opt
if [ -d "telegram-forward-bot" ]; then
    print_warning "目录已存在，正在更新..."
    cd telegram-forward-bot
    git pull
else
    git clone "$REPO_URL" telegram-forward-bot
    cd telegram-forward-bot
fi

print_info "设置 Python 虚拟环境..."
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
deactivate
print_success "Python 依赖安装完成"

print_info "设置配置文件..."
if [ ! -f .env ]; then
    cp config.env.example .env
    print_warning "请编辑 /opt/telegram-forward-bot/.env 填入你的 BOT_TOKEN"
    print_info "执行：sudo nano /opt/telegram-forward-bot/.env"
    
    # 等待用户确认
    echo -n "配置完成后按 Enter 继续..."
    read
fi

# 检查 BOT_TOKEN 是否已配置
if grep -q "BOT_TOKEN=your_bot_token_here" .env || grep -q "BOT_TOKEN=$" .env; then
    print_error "请先配置 BOT_TOKEN 后再运行此脚本"
    exit 1
else
    print_success "配置文件已设置"
fi

chmod 600 .env

print_info "创建 systemd 服务..."
tee /etc/systemd/system/telegram-forward-bot.service > /dev/null << EOF
[Unit]
Description=Telegram Forward Bot
After=network.target
Wants=network.target

[Service]
Type=simple
User=root
Group=root
WorkingDirectory=/opt/telegram-forward-bot
EnvironmentFile=/opt/telegram-forward-bot/.env
ExecStart=/opt/telegram-forward-bot/venv/bin/python3 bot.py
Restart=on-failure
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=telegram-forward-bot

[Install]
WantedBy=multi-user.target
EOF

print_info "启动服务..."
systemctl daemon-reload
systemctl enable telegram-forward-bot

# 检查服务是否已运行
if systemctl is-active --quiet telegram-forward-bot; then
    print_info "重启服务..."
    systemctl restart telegram-forward-bot
else
    print_info "启动服务..."
    systemctl start telegram-forward-bot
fi

# 等待服务启动
sleep 3

# 检查服务状态
if systemctl is-active --quiet telegram-forward-bot; then
    print_success "部署成功！机器人已启动"
else
    print_error "服务启动失败，请检查配置"
    print_info "查看日志：journalctl -u telegram-forward-bot -f"
    exit 1
fi

echo ""
print_success "🎉 Telegram 转发机器人部署完成！"
echo ""
echo "📋 常用命令："
echo "  查看状态：systemctl status telegram-forward-bot"
echo "  查看日志：journalctl -u telegram-forward-bot -f"
echo "  重启服务：systemctl restart telegram-forward-bot"
echo "  停止服务：systemctl stop telegram-forward-bot"
echo ""
print_info "💡 提示：机器人已设置为开机自启动"
