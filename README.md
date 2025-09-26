# Telegram 频道转发机器人

一个功能强大的 Telegram 频道消息转发机器人，支持文本、图片、视频、相册等多种消息类型的自动转发。

## ✨ 功能特性

- 🎯 **多源多目标转发**：支持一个源频道转发到多个目标频道
- 📱 **智能消息处理**：自动处理文本、图片、视频、相册等消息类型
- 🖼️ **相册批量转发**：智能识别并批量转发相册消息，保持原始顺序
- 🎛️ **交互式管理**：通过按钮菜单轻松管理源频道和目标频道
- 💾 **数据持久化**：使用 PicklePersistence 保存配置，重启后数据不丢失
- 🔧 **灵活配置**：支持环境变量配置，便于部署和管理
- 📊 **详细日志**：完整的日志记录，便于调试和监控

## 🚀 快速开始

### 1. 创建 Telegram 机器人

1. 在 Telegram 中找到 [@BotFather](https://t.me/botfather)
2. 发送 `/newbot` 命令创建新机器人
3. 按提示设置机器人名称和用户名
4. 获取 Bot Token（格式类似：`123456789:ABCdefGHIjklMNOpqrsTUVwxyz`）

### 2. 配置机器人权限

将机器人添加到需要转发的频道中，并给予以下权限：
- 读取消息权限
- 发送消息权限（目标频道）

### 3. 获取频道 ID

- 将机器人添加到频道
- 发送一条消息到频道
- 访问 `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
- 在返回的 JSON 中找到 `chat.id` 字段

## 📦 安装部署

### 🚀 一键部署（推荐）

在 VPS 上运行以下命令即可完成部署：

```bash
curl -fsSL https://raw.githubusercontent.com/mugegea/telegram-forward-bot/main/install.sh | bash
```

**部署步骤**：
1. 脚本会自动安装系统依赖
2. 克隆代码到 `/opt/telegram-forward-bot`
3. 创建 Python 虚拟环境并安装依赖
4. 提示你配置 BOT_TOKEN
5. 创建 systemd 服务并启动
6. 设置开机自启动

**配置 BOT_TOKEN**：
脚本会提示你编辑配置文件，执行：
```bash
sudo nano /opt/telegram-forward-bot/.env
```
将 `BOT_TOKEN=your_bot_token_here` 改为你的实际 Token。

### 方法二：手动部署

1. **克隆仓库**
```bash
git clone https://github.com/mugegea/telegram-forward-bot.git
cd telegram-forward-bot
```

2. **安装依赖**
```bash
# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt
```

3. **配置环境变量**
```bash
# 复制配置文件模板
cp config.env.example .env

# 编辑配置文件
nano .env
```

在 `.env` 文件中填入你的 Bot Token：
```env
BOT_TOKEN=your_bot_token_here
LOG_LEVEL=INFO
PERSISTENCE_FILE=bot_data.pkl
```

4. **运行机器人**
```bash
python bot.py
```

### 方法三：Docker 部署

```bash
# 构建镜像
docker build -t telegram-forward-bot .

# 运行容器
docker run -d \
  --name telegram-forward-bot \
  --env-file .env \
  -v $(pwd)/bot_data.pkl:/app/bot_data.pkl \
  telegram-forward-bot
```

## 🎮 使用说明

### 基本命令

- `/start` - 打开频道管理菜单
- `/listsources` - 查看已添加的源频道
- `/listtargets <源ID>` - 查看指定源频道的目标频道

### 管理界面

1. **添加源频道**：点击 "➕ 添加源"，输入源频道 ID
2. **添加目标频道**：选择源频道后，点击 "➕ 添加目标"，输入目标频道 ID
3. **删除频道**：使用相应的删除按钮移除不需要的频道
4. **查看映射**：点击 "📋 查看映射" 查看当前转发配置

### 消息转发

机器人会自动监听已添加的源频道，当有新消息时：
- 普通消息：直接转发到所有目标频道
- 相册消息：等待所有图片/视频接收完成后，批量转发

## ⚙️ 配置选项

| 环境变量 | 默认值 | 说明 |
|---------|--------|------|
| `BOT_TOKEN` | 无 | Telegram Bot Token（必需） |
| `LOG_LEVEL` | `INFO` | 日志级别（DEBUG/INFO/WARNING/ERROR） |
| `PERSISTENCE_FILE` | `bot_data.pkl` | 数据持久化文件路径 |

## 🔧 系统服务

使用一键部署脚本会自动创建 systemd 服务，支持以下操作：

```bash
# 查看服务状态
sudo systemctl status telegram-forward-bot

# 启动服务
sudo systemctl start telegram-forward-bot

# 停止服务
sudo systemctl stop telegram-forward-bot

# 重启服务
sudo systemctl restart telegram-forward-bot

# 查看日志
sudo journalctl -u telegram-forward-bot -f

# 开机自启
sudo systemctl enable telegram-forward-bot
```

## 🐛 故障排除

### 常见问题

1. **机器人无响应**
   - 检查 Bot Token 是否正确
   - 确认机器人已添加到频道并有相应权限
   - 查看日志文件排查错误

2. **消息转发失败**
   - 确认目标频道 ID 正确
   - 检查机器人是否在目标频道中
   - 验证机器人是否有发送消息权限

3. **相册消息不完整**
   - 这是正常现象，机器人会等待所有媒体文件接收完成
   - 如果长时间不完整，可能是网络问题

### 日志查看

```bash
# 实时查看日志
tail -f bot.log

# 查看系统服务日志
sudo journalctl -u telegram-forward-bot -f
```

## ⚠️ 免责声明

本工具仅供学习和研究使用，请遵守相关法律法规和 Telegram 服务条款。使用者需自行承担使用风险。

## 👨‍💻 作者

**笨哥哥** - [@bengege](https://t.me/bengege)
