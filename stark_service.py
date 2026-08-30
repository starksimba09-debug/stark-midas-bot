import telebot
from curl_cffi import requests
import re
import json

TOKEN = "8961573070:AAFojTKU_1EBpjxAg-M_gI2V3_t9E0dZ4io"
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    text = message.text
    
    if "midasbuy.com" in text:
        bot.reply_to(message, "🔍 جاري تحليل الرابط واستخراج بيانات المساعدة...")
        
        try:
            url_match = re.search(r'(https?://[^\s]+)', text)
            if not url_match:
                bot.reply_to(message, "❌ لم يتم العثور على رابط صحيح في رسالتك.")
                return
                
            target_url = url_match.group(1)
            
            # 1. جلب صفحة الـ HTML للرابط المختصر
            response = requests.get(
                target_url,
                impersonate="chrome120",
                headers={
                    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36'
                },
                timeout=15
            )
            
            js_data_match = re.search(r'var\s+jsData\s*=\s*({.*?});', response.text)
            if not js_data_match:
                bot.reply_to(message, "❌ لم يتم العثور على بيانات الحدث داخل الرابط.")
                return
                
            js_data_json = json.loads(js_data_match.group(1))
            redirect_url = js_data_json.get("redirectUrl")
            
            if not redirect_url:
                bot.reply_to(message, "❌ لم يتم العثور على رابط التوجيه.")
                return

            bot.reply_to(message, "⚙️ جاري فحص الرابط والتأكد من حالة اللفات...")

            # 2. الدخول على رابط التوجيه الفعلي (Redirect URL) لجلب النتيجة النهائية
            final_response = requests.get(
                redirect_url,
                impersonate="chrome120",
                headers={
                    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'referer': target_url,
                    'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36'
                },
                timeout=15
            )
            
            # 3. إرسال رد مناسب بناءً على الاستجابة أو طباعة محتوى الصفحة أو الـ API المرتبط
            if "expired" in final_response.text.lower() or "over" in final_response.text.lower():
                bot.reply_to(message, "🎰 لا توجد لفات متاحة في هذا الرابط (قد تكون سحبت بالفعل أو انتهى الرابط).")
            else:
                # عرض جزء من الرد لو فيه تفاصيل تانية ترغب في رؤيتها
                bot.reply_to(message, f"📌 حالة الرابط النهائية:\nتم فحص الرابط بنجاح وجاري معالجة الطلب.")
            
        except Exception as e:
            bot.reply_to(message, f"❌ حدث خطأ أثناء فحص الرابط:\n{str(e)}")
    else:
        bot.reply_to(message, "أهلاً بك يا السعيد! أرسل الآن رابط دعوة Midasbuy المختصر لفحصه.")

print("Bot is ready...")
bot.infinity_polling(skip_pending=True)
