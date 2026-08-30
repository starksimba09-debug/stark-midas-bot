import logging
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# جلب التوكن من متغيرات البيئة في Railway لضمان الأمان
TOKEN = os.getenv("BOT_TOKEN", "8950696232:AAFYW8wPylbYIRkRyV-2wkrP042UGbzH7lE")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    await update.message.reply_text(
        f"أهلاً بك يا {user_name}! 🚀\n"
        "أرسل رابط مساعدة Midasbuy وسأقوم باستقباله وتجهيزه للتنفيذ."
    )

async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if "midasbuy.com" in text or "pagedooapi" in text:
        await update.message.reply_text(
            "✅ تم استلام رابط المساعدة بنجاح!\n"
            f"🔗 الرابط: {text}\n\n"
            "⏳ جاري التمرير للتنفيذ..."
        )
    else:
        await update.message.reply_text("⚠️ يرجى إرسال رابط Midasbuy صحيح.")

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_link))
    
    print("Bot is running on Railway...")
    app.run_polling()

if __name__ == "__main__":
    main()
