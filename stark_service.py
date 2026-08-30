import telebot
from curl_cffi import requests
import re

TOKEN = "8961573070:AAFojTKU_1EBpjxAg-M_gI2V3_t9E0dZ4io"
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    text = message.text
    
    # التأكد إن المستخدم ابتعث رابط ميداسباي المختصر
    if "midasbuy.com" in text:
        bot.reply_to(message, "🔍 جاري فحص وفك رابط المساعدة...")
        
        try:
            # استخراج الرابط من النص لو فيه كلام جنبه
            url_match = re.search(r'(https?://[^\s]+)', text)
            if not url_match:
                bot.reply_to(message, "❌ لم يتم العثور على رابط صحيح في رسالتك.")
                return
                
            target_url = url_match.group(1)
            
            # الطلب باستخدام curl_cffi لجلب بيانات الرابط المختصر
            response = requests.get(
                target_url,
                impersonate="chrome120",
                headers={
                    'accept': 'application/json, text/plain, */*',
                    'origin': 'https://www.midasbuy.com',
                    'referer': 'https://www.midasbuy.com/'
                },
                timeout=15
            )
            
            result = response.text
            bot.reply_to(message, f"📌 رد السيرفر:\n{result[:3500]}")
            
        except Exception as e:
            bot.reply_to(message, f"❌ حدث خطأ أثناء فحص الرابط:\n{str(e)}")
    else:
        bot.reply_to(message, " أهلاً بك يا السعيد! أرسل الآن رابط دعوة Midasbuy الخاص بك لفحصه.")

print("Bot is ready...")
bot.infinity_polling()
