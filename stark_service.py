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
            
            # الخطوة 1: جلب صفحة الـ HTML للرابط المختصر
            response = requests.get(
                target_url,
                impersonate="chrome120",
                headers={
                    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36'
                },
                timeout=15
            )
            
            html_content = response.text
            
            # الخطوة 2: استخراج متغير jsData باستخدام Regular Expression
            js_data_match = re.search(r'var\s+jsData\s*=\s*({.*?});', html_content)
            if not js_data_match:
                bot.reply_to(message, "❌ لم يتم العثور على بيانات الحدث داخل الرابط.")
                return
                
            js_data_json = json.loads(js_data_match.group(1))
            redirect_url = js_data_json.get("redirectUrl")
            from_data = js_data_json.get("fromData")
            
            bot.reply_to(message, f"🔗 تم استخراج الرابط بنجاح!\n\n`{redirect_url}`", parse_mode="Markdown")
            
        except Exception as e:
            bot.reply_to(message, f"❌ حدث خطأ أثناء فحص الرابط:\n{str(e)}")
    else:
        bot.reply_to(message, "أهلاً بك يا السعيد! أرسل الآن رابط دعوة Midasbuy المختصر لفحصه.")

print("Bot is ready...")
bot.infinity_polling()
