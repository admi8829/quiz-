import os
import json
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Appwrite Environment Variable ውስጥ ያስገባኸውን BOT_TOKEN ያነባል
TOKEN = os.environ.get('BOT_TOKEN')

# የኩዊዝ ጥያቄዎች (እዚህ ጋር መጨመር ትችላለህ)
QUIZ_QUESTIONS = [
    {
        "id": 1,
        "question": "የኢትዮጵያ ትልቁ ወንዝ ማነው?",
        "options": ["አዋሽ", "ዓባይ", "ገናሌ", "ዋቢ ሸበሌ"],
        "correct": "ዓባይ"
    },
    {
        "id": 2,
        "question": "Python የፕሮግራም ቋንቋ ነው?",
        "options": ["አዎ", "አይደለም"],
        "correct": "አዎ"
    }
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "እንኳን ወደ Smart-X Quiz Bot በሰላም መጡ! 👋\n\nለመጀመር /quiz የሚለውን ይጫኑ።"
    )

async def send_question(update: Update, context: ContextTypes.DEFAULT_TYPE, q_index=0):
    if q_index >= len(QUIZ_QUESTIONS):
        # ሁሉንም ጥያቄ ጨርሶ ከሆነ
        text = "ፈተናውን ጨርሰሃል! 🎉\nእንደገና ለመጀመር /quiz ይጫኑ።"
        if update.callback_query:
            await update.callback_query.message.edit_text(text)
        else:
            await update.message.reply_text(text)
        return

    q = QUIZ_QUESTIONS[q_index]
    keyboard = []
    # ለእያንዳንዱ አማራጭ በተን (Button) መስራት
    for opt in q["options"]:
        keyboard.append([InlineKeyboardButton(opt, callback_data=f"{q_index}|{opt}")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    msg_text = f"ጥያቄ {q_index + 1}: {q['question']}"
    
    if update.callback_query:
        await update.callback_query.message.edit_text(msg_text, reply_markup=reply_markup)
    else:
        await update.message.reply_text(msg_text, reply_markup=reply_markup)

async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    # ዳታውን መለየት (index እና የተመረጠው መልስ)
    q_index, selected_opt = query.data.split("|")
    q_index = int(q_index)
    
    correct_answer = QUIZ_QUESTIONS[q_index]["correct"]
    
    if selected_opt == correct_answer:
        result_text = "ትክክል ነህ! ✅"
    else:
        result_text = f"ተሳስተሃል! ❌ ትክክለኛው መልስ: {correct_answer}"
    
    await query.message.reply_text(result_text)
    
    # ለቀጣዩ ጥያቄ 1 ሰከንድ ጠብቆ እንዲሄድ ማድረግ
    await asyncio.sleep(1)
    await send_question(update, context, q_index + 1)

# Appwrite Function "handler" (ይህ ክፍል ለ Appwrite ወሳኝ ነው)
async def run_bot(body):
    app = Application.builder().token(TOKEN).build()
    
    # Handler-ዎችን መመዝገብ
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("quiz", lambda u, c: send_question(u, c, 0)))
    app.add_handler(CallbackQueryHandler(handle_answer))

    await app.initialize()
    update = Update.de_json(json.loads(body), app.bot)
    await app.process_update(update)
    await app.shutdown()

def handler(request, response):
    if request.method == "POST":
        asyncio.run(run_bot(request.body))
        return response.json({"status": "success"})
    return response.json({"status": "only POST allowed"})
