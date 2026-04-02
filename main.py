import os
import json
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Appwrite Environment Variables ውስጥ ያስገባኸውን BOT_TOKEN ያነባል
TOKEN = os.environ.get('BOT_TOKEN')

# የኩዊዝ ጥያቄዎች ዝርዝር
QUIZ_QUESTIONS = [
    {
        "id": 1,
        "question": "የኢትዮጵያ ትልቁ ወንዝ ማነው?",
        "options": ["አዋሽ", "ዓባይ", "ገናሌ", "ዋቢ ሸበሌ"],
        "correct": "ዓባይ"
    },
    {
        "id": 2,
        "question": "Python ምንድነው?",
        "options": ["የምግብ አይነት", "የፕሮግራም ቋንቋ", "የመኪና ስም"],
        "correct": "የፕሮግራም ቋንቋ"
    }
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "እንኳን ወደ Smart-X Quiz Bot በሰላም መጡ! 👋\n\nለመጀመር /quiz የሚለውን ይጫኑ።"
    )

async def send_question(update: Update, context: ContextTypes.DEFAULT_TYPE, q_index=0):
    if q_index >= len(QUIZ_QUESTIONS):
        text = "ፈተናውን ጨርሰሃል! 🎉\nእንደገና ለመጀመር /quiz ይጫኑ።"
        if update.callback_query:
            await update.callback_query.message.edit_text(text)
        else:
            await update.message.reply_text(text)
        return

    q = QUIZ_QUESTIONS[q_index]
    keyboard = []
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
    
    q_index, selected_opt = query.data.split("|")
    q_index = int(q_index)
    correct_answer = QUIZ_QUESTIONS[q_index]["correct"]
    
    if selected_opt == correct_answer:
        result_text = "ትክክል ነህ! ✅"
    else:
        result_text = f"ተሳስተሃል! ❌ ትክክለኛው መልስ: {correct_answer}"
    
    await query.message.reply_text(result_text)
    await asyncio.sleep(1)
    await send_question(update, context, q_index + 1)

# --- ይህ ክፍል ለ Appwrite ወሳኝ ነው ---
async def run_bot(body):
    # አፕሊኬሽኑን መፍጠር
    app = Application.builder().token(TOKEN).build()
    
    # Handler-ዎችን መመዝገብ
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("quiz", lambda u, c: send_question(u, c, 0)))
    app.add_handler(CallbackQueryHandler(handle_answer))

    # ቦቱን ማስነሳትና መልዕክቱን ማስተናገድ
    await app.initialize()
    update = Update.de_json(json.loads(body), app.bot)
    await app.process_update(update)
    await app.shutdown()

# Appwrite የሚጠራው ዋናው Function
def handler(request, response):
    if request.method == "POST":
        # ቴሌግራም የላከውን ዳታ ለ run_bot መስጠት
        asyncio.run(run_bot(request.body))
        return response.json({"status": "success"})
    return response.json({"status": "only POST allowed"})
    
