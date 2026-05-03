import random
import asyncio
import os
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

TOKEN = os.getenv("BOT_TOKEN")

game_active = False
players = {}
task = None


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎲 Dice Battle Bot\n"
        "/startgame 开始游戏\n"
        "发送 🎲 参与"
    )


async def start_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global game_active, players, task

    game_active = True
    players = {}

    await update.message.reply_text(
        "🎲【游戏开始】\n"
        "请在15秒内发送骰子 🎲"
    )

    task = asyncio.create_task(game_flow(update, context))


async def handle_dice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global players, game_active

    if not game_active:
        return

    msg = update.message

    # 禁止转发骰子
    if msg.forward_origin is not None:
        return

    user_id = msg.from_user.id

    if user_id in players:
        return

    if msg.dice:
        players[user_id] = msg.dice.value


async def game_flow(update, context):
    global game_active, players

    await asyncio.sleep(15)

    banker = random.randint(1, 6)

    await update.message.reply_text(f"🎲 庄家骰子：{banker}")
    await update.message.reply_text("💰 开始结算")

    for user_id, player in players.items():

        if player > banker:
            result = "✅ 赢"
        elif player < banker:
            result = "❌ 输"
        else:
            result = "⚖️ 和局（庄赢）"

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"玩家 {user_id}\n你：{player} 庄：{banker}\n{result}"
        )

    game_active = False
    players = {}


app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("startgame", start_game))
app.add_handler(MessageHandler(filters.DICE, handle_dice))

print("Bot running...")
app.run_polling()
