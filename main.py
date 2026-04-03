import os
import json
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Appwrite Variables ውስጥ የጨመርከውን BOT_TOKEN ያነባል
TOKEN = os.environ.get('BOT_TOKEN')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("እንኳን ደስ አለህ! 🎉 ቦቱ በሚገባ ሰርቷል።")

async def run_bot(body):
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))

    await app.initialize()
    update = Update.de_json(json.loads(body), app.bot)
    await app.process_update(update)
    await app.shutdown()

# --- ይህ ክፍል ለ Appwrite በጣም ወሳኝ ነው ---
def handler(request, response):
    if request.method == "POST":
        asyncio.run(run_bot(request.body))
        return response.json({"status": "success"})
    return response.json({"status": "Only POST is allowed"})
    
