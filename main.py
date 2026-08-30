import os
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
import requests

# قراءة البروكسيات من الملف
def load_proxies():
    if os.path.exists("proxies.txt"):
        with open("proxies.txt", "r") as f:
            return [line.strip() for line in f if line.strip()]
    return []

# دالة التعامل مع الروابط اللي بتجيلك على البوت
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    
    # التأكد إن الرسالة فيها رابط ميداسباي
    if "midasbuy.com" in user_message:
        await update.message.reply_text("⏳ جارٍ بدء إرسال الطلبات عبر البروكسيات...")
        
        proxies_list = load_proxies()
        if not proxies_list:
            await update.message.reply_text("❌ خطأ: لم يتم العثور على ملف البروكسيات!")
            return

        success_count = 0
        total_requests = 30  # عدد الطلبات المستهدف إرسالها زي فكرة فوكسي
        
        for i in range(total_requests):
            # اختيار بروكسي بالتناوب (دورة تكرارية)
            proxy_item = proxies_list[i % len(proxies_list)]
            proxy_dict = {
                "http": f"http://{proxy_item}",
                "https": f"http://{proxy_item}",
            }
            
            try:
                # إرسال الطلب لرابط المساعدة المستهدف
                response = requests.get(user_message, proxies=proxy_dict, timeout=8)
                if response.status_code == 200:
                    success_count += 1
            except Exception:
                pass

        # إرسال تقرير بالنتيجة شبه بوت فوكسي
        report = (
            f"✅ **تم الانتهاء بنجاح!**\n"
            f"📊 الطلبات الناجحة: {success_count}/{total_requests}\n"
            f"🚀 الحالة: تم التنفيذ باستخدام البروكسيات بنجاح."
        )
        await update.message.reply_text(report, parse_mode="Markdown")
    else:
        await update.message.reply_text("يرجى إرسال رابط مساعدة Midasbuy صحيح للبداء.")

if __name__ == "__main__":
    # سحب التوكن أوتوماتيك من إعدادات Railway (الـ Environment Variables)
    TOKEN = os.getenv("BOT_TOKEN")
    
    if not TOKEN:
        print("خطأ: لم يتم العثور على متغير BOT_TOKEN في البيئة!")
    else:
        app = ApplicationBuilder().token(TOKEN).build()
        app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
        
        print("البوت يعمل الآن...")
        app.run_polling()
