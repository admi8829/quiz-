import os
import json
import asyncio
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# 1. Logging ማዋቀር (ስህተቶች ካሉ በ Appwrite Log ላይ ለማየት ይረዳል)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# 2. የቦት Token (ለሙከራ በቀጥታ እዚህ ተቀምጧል)
TOKEN = "7893868461:AAFocP1khzN_CFgBbzFQdYxjOVDfRydz0to"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ተጠቃሚው /start ሲል የሚሰጠው ምላሽ"""
    try:
        await update.message.reply_text("እንኳን ደስ አለህ! 🎉 ቦቱ በሚገባ ሰርቷል።\nይህ የተሻሻለው የሙከራ ስሪት ነው።")
    except Exception as e:
        logger.error(f"Error sending message: {e}")

async def run_bot(body):
    """ቦቱን የማስነሳትና መልእክቱን የማስተናገድ ሂደት"""
    # Application መገንባት
    app = Application.builder().token(TOKEN).build()
    
    # ትዕዛዞችን መጨመር
    app.add_handler(CommandHandler("start", start))
    
    try:
        # ቦቱን ለጊዜው ማስነሳት (Initialize)
        await app.initialize()
        
        # ከ Webhook የመጣውን መረጃ ወደ Telegram Update መቀየር
        update_data = json.loads(body)
        update = Update.de_json(update_data, app.bot)
        
        # መልእክቱን አስተናግዶ መጨረስ
        await app.process_update(update)
    except Exception as e:
        logger.error(f"Error processing update: {e}")
    finally:
        # ሀብት እንዳይባክን ቦቱን መዝጋት
        await app.shutdown()

def handler(request, response):
    """የ Appwrite ዋናው መግቢያ (Entry point)"""
    
    # 1. ዘዴው POST መሆኑን ማረጋገጥ (ቴሌግራም ሁልጊዜ POST ነው የሚጠቀመው)
    if request.method == "POST":
        if not request.body:
            return response.json({"error": "Empty body"}, 400)
            
        try:
            # ቦቱን በ async መንገድ ማስኬድ
            asyncio.run(run_bot(request.body))
            return response.json({"status": "success", "message": "Update processed"})
        except Exception as e:
            return response.json({"status": "error", "message": str(e)}, 500)
    
    # 2. በስህተት በ Browser (GET) ለመክፈት ሲሞከር
    return response.json({
        "status": "denied", 
        "message": "ይህ endpoint ለቴሌግራም Webhook ብቻ የተዘጋጀ ነው።"
    }, 405)
    
