import os
import json
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Appwrite Variables ውስጥ የጨመርከውን BOT_TOKEN ያነባል
TOKEN = os.environ.get('BOT_TOKEN')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ለ /start ትዕዛዝ 'Hello' ብሎ ይመልሳል"""
    await update.message.reply_text("Hello! እኔ የ Smart-X ቦት ነኝ። እንዴት ልርዳህ?")

async def run_bot(body):
    """ቦቱን የማስነሻ ክፍል"""
    app = Application.builder().token(TOKEN).build()
    
    # የ /start ትዕዛዝን መመዝገብ
    app.add_handler(CommandHandler("start", start))

    await app.initialize()
    update = Update.de_json(json.loads(body), app.bot)
    await app.process_update(update)
    await app.shutdown()

# --- ይህ ክፍል ለ Appwrite ወሳኝ ነው (Entrypoint) ---
def handler(request, response):
    if request.method == "POST":
        # ቴሌግራም የላከውን ዳታ ማሰናዳት
        asyncio.run(run_bot(request.body))
        return response.json({"status": "success"})
    return response.json({"status": "Only POST is allowed"})
    
