import os
import re
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
import httpx

def load_proxies():
    if os.path.exists("proxies.txt"):
        with open("proxies.txt", "r") as f:
            return [line.strip() for line in f if line.strip()]
    return []

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    url_match = re.search(r'https?://[^\s]+midasbuy\.com[^\s]+', user_message)
    
    if url_match:
        target_url = url_match.group(0).rstrip('_copy')
        await update.message.reply_text("⏳ جاري إرسال طلبات المساعدة بالهيدرز الاحترافية...")
        
        proxies_list = load_proxies()
        if not proxies_list:
            await update.message.reply_text("❌ خطأ: ملف البروكسيات فارغ!")
            return

        success_count = 0
        total_requests = 30  
        
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json",
            "Accept-Language": "ar-EG,ar;q=0.9,en-US;q=0.8",
            "Sec-Ch-Ua": '"Chromium";v="127", "Not)A;Brand";v="99", "Microsoft Edge Simulate";v="127"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Linux"',
            "Sec-Fetch-Site": "same-site",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Referer": "https://www.midasbuy.com/"
        }
        
        for i in range(total_requests):
            proxy_item = proxies_list[i % len(proxies_list)]
            proxy_url = f"http://{proxy_item}"
            
            try:
                with httpx.Client(proxies=proxy_url, headers=headers, timeout=6, follow_redirects=True, http2=True) as client:
                    # زيارات محاكاة حقيقية لرابط المساعدة المدعوم بالبروكسي
                    response = client.get(target_url)
                    if response.status_code in [200, 301, 302, 303, 307]:
                        success_count += 1
            except Exception:
                pass

        report = (
            f"✅ **تم الانتهاء بنجاح!**\n"
            f"📊 الطلبات الناجحة: {success_count}/{total_requests}\n"
            f"🚀 الحالة: تم تمرير المساعدات بنجاح عبر البروكسيات."
        )
        await update.message.reply_text(report, parse_mode="Markdown")
    else:
        await update.message.reply_text("يرجى إرسال رابط مساعدة Midasbuy صحيح.")

if __name__ == "__main__":
    TOKEN = os.getenv("BOT_TOKEN")
    if TOKEN:
        app = ApplicationBuilder().token(TOKEN).build()
        app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
        print("البوت يعمل الآن بدون تضارب...")
        app.run_polling(drop_pending_updates=True)
