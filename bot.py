"""
Telegram 频道转发机器人
作者: 笨哥哥 (@bengege)
GitHub: https://github.com/mugegea/telegram-forward-bot
"""

import os
import asyncio
import logging
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup,
    InputMediaPhoto, InputMediaVideo
)
from telegram.ext import (
    ApplicationBuilder, ContextTypes,
    CommandHandler, CallbackQueryHandler,
    ConversationHandler, MessageHandler,
    filters, PicklePersistence
)

# 配置日志
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", 
    level=getattr(logging, log_level, logging.INFO)
)
logger = logging.getLogger(__name__)

SELECT_SRC, MANAGE_TGT, ADD_TGT, DEL_TGT, DEL_SRC = range(5)
persistence_file = os.getenv("PERSISTENCE_FILE", "bot_data.pkl")
persistence = PicklePersistence(filepath=persistence_file)

media_group_cache = {}
media_group_events = {}

async def on_startup(application):
    bd = application.bot_data
    bd.setdefault("sources", set())
    bd.setdefault("dst_map", {})

def make_src_menu(bot_data):
    buttons = []
    for src in sorted(bot_data.get("sources", [])):
        buttons.append([InlineKeyboardButton(f"📡 源频道 {src}", callback_data=f"src_{src}")])
    buttons.append([
        InlineKeyboardButton("➕ 添加源", callback_data="add_src"),
        InlineKeyboardButton("🗑️ 删除源", callback_data="del_src"),
        InlineKeyboardButton("❓ 帮助", callback_data="help")
    ])
    return InlineKeyboardMarkup(buttons)

def make_tgt_menu(src_id, bot_data):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ 添加目标", callback_data="add_tgt"),
         InlineKeyboardButton("➖ 删除目标", callback_data="del_tgt")],
        [InlineKeyboardButton("🧹 清空目标", callback_data="clear_tgt")],
        [InlineKeyboardButton("📋 查看映射", callback_data="show_map")],
        [InlineKeyboardButton("🔙 返回源列表", callback_data="back")]
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_message.reply_text(
        "请选择一个源频道进行管理：", reply_markup=make_src_menu(context.bot_data)
    )
    return SELECT_SRC

async def src_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    bd = context.bot_data

    if data.startswith("src_"):
        src = int(data[4:])
        context.user_data["current_src"] = src
        tgts = bd.get("dst_map", {}).get(src, set())
        msg = f"🎯 当前源频道：{src}\n目标频道：{', '.join(map(str, tgts)) or '无'}"
        await query.edit_message_text(msg, reply_markup=make_tgt_menu(src, bd))
        return MANAGE_TGT

    if data == "add_src":
        context.user_data["action"] = "add_src"
        await query.edit_message_text("请输入要添加的源频道 ID：")
        return ADD_TGT

    if data == "del_src":
        context.user_data["action"] = "del_src"
        await query.edit_message_text("请输入要删除的源频道 ID：")
        return DEL_SRC

    if data == "help":
        text = (
            "📖 帮助信息：\n"
            "/start - 打开频道管理菜单\n"
            "/listsources - 查看已添加源频道\n"
            "/listtargets <源ID> - 查看该源的目标频道\n\n"
            "📡 源频道是监听对象，🎯 目标频道是接收对象\n"
            "每个源频道可设置多个目标频道，操作互不影响"
        )
        await query.edit_message_text(text, reply_markup=make_src_menu(bd))
        return SELECT_SRC

async def tgt_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    action = query.data
    bd = context.bot_data
    src = context.user_data.get("current_src")

    if action == "add_tgt":
        context.user_data["action"] = "add_tgt"
        await query.edit_message_text(f"请输入目标频道 ID（添加到源 {src}）：")
        return ADD_TGT

    if action == "del_tgt":
        context.user_data["action"] = "del_tgt"
        await query.edit_message_text(f"请输入要删除的目标频道 ID（源 {src}）：")
        return DEL_TGT

    if action == "clear_tgt":
        bd["dst_map"].get(src, set()).clear()
        await query.edit_message_text(f"✅ 已清空源频道 {src} 的所有目标频道", reply_markup=make_tgt_menu(src, bd))
        return MANAGE_TGT

    if action == "show_map":
        tgts = bd["dst_map"].get(src, set())
        text = f"📡 源频道 {src} → {', '.join(map(str, tgts)) or '无'}"
        await query.edit_message_text(text, reply_markup=make_tgt_menu(src, bd))
        return MANAGE_TGT

    if action == "back":
        await query.edit_message_text("请选择一个源频道进行管理：", reply_markup=make_src_menu(bd))
        return SELECT_SRC

async def text_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    bd = context.bot_data
    action = context.user_data.get("action")
    src = context.user_data.get("current_src")

    try:
        if action == "add_src":
            cid = int(text)
            bd["sources"].add(cid)
            bd.setdefault("dst_map", {}).setdefault(cid, set())
            resp = f"✅ 已添加源频道 {cid}"
            await update.message.reply_text(resp, reply_markup=make_src_menu(bd))
            return SELECT_SRC

        if action == "del_src":
            cid = int(text)
            bd["sources"].discard(cid)
            bd["dst_map"].pop(cid, None)
            resp = f"✅ 已删除源频道 {cid}"
            await update.message.reply_text(resp, reply_markup=make_src_menu(bd))
            return SELECT_SRC

        cid = int(text)
        tgts = bd["dst_map"].setdefault(src, set())
        if action == "add_tgt":
            tgts.add(cid)
            resp = f"✅ 已添加目标频道 {cid} 到源 {src}"
        else:
            tgts.discard(cid)
            resp = f"✅ 已从源频道 {src} 删除目标频道 {cid}"
        await update.message.reply_text(resp, reply_markup=make_tgt_menu(src, bd))
        return MANAGE_TGT

    except Exception as e:
        logger.error(e)
        await update.message.reply_text("❌ 输入格式错误，请输入有效的频道 ID")
        return MANAGE_TGT

async def forward_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.channel_post or update.message
    cid = msg.chat.id
    bd = context.bot_data

    if cid not in bd["sources"]:
        return

    if not msg.media_group_id:
        for tgt in bd["dst_map"].get(cid, []):
            try:
                await context.bot.copy_message(chat_id=tgt, from_chat_id=cid, message_id=msg.message_id)
            except Exception as e:
                logger.warning(f"普通转发失败 {cid}->{tgt}: {e}")
        return

    gid = (cid, msg.media_group_id)
    if gid not in media_group_cache:
        media_group_cache[gid] = []
        media_group_events[gid] = asyncio.Event()
        asyncio.create_task(handle_album_group(gid, context))

    media_group_cache[gid].append(msg)
    media_group_events[gid].set()

async def handle_album_group(gid, context):
    event = media_group_events[gid]
    try:
        timeout_rounds = 10
        wait_interval = 1.2
        unchanged_count = 0
        last_len = -1

        for _ in range(timeout_rounds):
            event.clear()
            try:
                await asyncio.wait_for(event.wait(), timeout=wait_interval)
            except asyncio.TimeoutError:
                current_len = len(media_group_cache.get(gid, []))
                if current_len == last_len:
                    unchanged_count += 1
                else:
                    unchanged_count = 0
                    last_len = current_len
                if unchanged_count >= 3:
                    break
        
        # 相册处理结束后继续执行：
        msgs = media_group_cache.pop(gid, [])
        media_group_events.pop(gid, None)
        msgs.sort(key=lambda m: m.message_id)

        media = []
        for m in msgs:
            if m.photo:
                media.append(InputMediaPhoto(m.photo[-1].file_id, caption=m.caption or None))
            elif m.video:
                media.append(InputMediaVideo(m.video.file_id, caption=m.caption or None))

        if not media:
            return

        src = gid[0]
        for tgt in context.bot_data["dst_map"].get(src, []):
            try:
                await context.bot.send_media_group(chat_id=tgt, media=media)
                logger.info(f"📦 整组转发完成：{len(media)} 项 from {src} → {tgt}")
            except Exception as e:
                logger.warning(f"⚠️ 相册转发失败 {src}->{tgt}: {e}")
    except Exception as e:
        logger.exception(f"📛 相册处理异常：{e}")

# 辅助命令
async def listsources(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bd = context.bot_data
    text = "📡 已注册源频道：\n" + ("\n".join(map(str, bd["sources"])) or "无")
    await update.message.reply_text(text)

async def listtargets(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bd = context.bot_data
    try:
        src = int(context.args[0])
        tgts = bd["dst_map"].get(src, set())
        text = f"🎯 源频道 {src} 的目标频道：\n" + ("\n".join(map(str, tgts)) or "无")
    except:
        text = "❌ 用法：/listtargets <源频道ID>"
    await update.message.reply_text(text)

# 启动入口
def main():
    token = os.getenv("BOT_TOKEN")
    if not token:
        logger.error("❌ 未找到 BOT_TOKEN 环境变量，请检查配置文件")
        return
    
    logger.info("🚀 启动 Telegram 转发机器人...")
    app = ApplicationBuilder()\
        .token(token)\
        .persistence(persistence)\
        .post_init(on_startup)\
        .build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            SELECT_SRC: [CallbackQueryHandler(src_menu_handler)],
            MANAGE_TGT: [CallbackQueryHandler(tgt_menu_handler)],
            ADD_TGT: [MessageHandler(filters.TEXT & ~filters.COMMAND, text_input)],
            DEL_TGT: [MessageHandler(filters.TEXT & ~filters.COMMAND, text_input)],
            DEL_SRC: [MessageHandler(filters.TEXT & ~filters.COMMAND, text_input)],
        },
        fallbacks=[CommandHandler("start", start)],
        name="conv",
        persistent=True
    )

    app.add_handler(conv)
    app.add_handler(CommandHandler("listsources", listsources))
    app.add_handler(CommandHandler("listtargets", listtargets))
    app.add_handler(MessageHandler(filters.ALL, forward_handler))
    
    try:
        logger.info("✅ 机器人启动成功，开始轮询...")
        app.run_polling()
    except KeyboardInterrupt:
        logger.info("🛑 收到停止信号，正在关闭机器人...")
    except Exception as e:
        logger.error(f"❌ 机器人运行出错: {e}")
        raise

if __name__ == "__main__":
    main()


