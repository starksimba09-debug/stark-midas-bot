import os
import re
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
import requests

def load_proxies():
    if os.path.exists("proxies.txt"):
        with open("proxies.txt", "r") as f:
            return [line.strip() for line in f if line.strip()]
    return []

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    
    # استخراج رابط Midasbuy بدقة من نص الرسالة حتى لو معاها كلام عربي
    url_match = re.search(r'https?://[^\s]+midasbuy\.com[^\s]+', user_message)
    
    if url_match:
        target_url = url_match.group(0)
        await update.message.reply_text(f"⏳ جارٍ معالجة الرابط وإرسال الطلبات عبر البروكسيات...")
        
        proxies_list = load_proxies()
        if not proxies_list:
            await update.message.reply_text("❌ خطأ: لم يتم العثور على ملف البروكسيات!")
            return

        success_count = 0
        total_requests = 30  
        
        # هيدرز عشان السيرفر يقبل الطلب كأنه متصفح حقيقي
        headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://www.midasbuy.com/"
        }
        
        for i in range(total_requests):
            proxy_item = proxies_list[i % len(proxies_list)]
            proxy_dict = {
                "http": f"http://{proxy_item}",
                "https": f"http://{proxy_item}",
            }
            
            try:
                response = requests.get(target_url, headers=headers, proxies=proxy_dict, timeout=8)
                # لو السيرفر رد بـ 200 أو حتى بتحويله ناجحة نحسبها صح
                if response.status_code in [200, 301, 302]:
                    success_count += 1
            except Exception:
                pass

        report = (
            f"✅ **تم الانتهاء بنجاح!**\n"
            f"📊 الطلبات الناجحة: {success_count}/{total_requests}\n"
            f"🚀 الحالة: تم التنفيذ باستخدام البروكسيات بنجاح."
        )
        await update.message.reply_text(report, parse_mode="Markdown")
    else:
        await update.message.reply_text("يرجى إرسال رابط مساعدة Midasbuy صحيح يحتوي على الرابط.")

if __name__ == "__main__":
    TOKEN = os.getenv("BOT_TOKEN")
    
    if not TOKEN:
        print("خطأ: لم يتم العثور على متغير BOT_TOKEN في البيئة!")
    else:
        app = ApplicationBuilder().token(TOKEN).build()
        app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
        
        print("البوت يعمل الآن...")
        app.run_polling()
