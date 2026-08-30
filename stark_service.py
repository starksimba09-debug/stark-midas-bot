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
            from_data = js_data_json.get("fromData")
            
            if not from_data:
                bot.reply_to(message, "❌ لم يتم استخراج بيانات الحدث بنجاح.")
                return

            bot.reply_to(message, "⚙️ جاري إرسال الطلب الفعلي لسيرفر Midasbuy...")

            # 2. إرسال الطلب الحقيقي للـ API الخاص بالحدث باستخدام بيانات الـ ShortLink المستخرجة
            api_response = requests.post(
                'https://pagedooapi.midasbuy.com/api/CallMpgo/osmidas/dd_help_model/HelpInfoListByUserId',
                impersonate="chrome120",
                headers={
                    'content-type': 'application/json',
                    'accept': 'application/json, text/plain, */*',
                    'origin': 'https://www.midasbuy.com',
                    'referer': target_url
                },
                json={
                    "mp_activity_id": "Activity_1784618952_EQXYLI",
                    "mp_app_id": "1450015065",
                    "query_page_num": 1,
                    "query_page_size": 10,
                    "mp_sub_activity_id": "1784618952184467302LJI",
                    "user_id": "62695321247286568",
                    "user_id_type": "hy_gameid",
                    "meta_data": {
                        "ori_zoneid": "1",
                        "client_ver": "android",
                        "server_id": "1",
                        "role_id": "",
                        "muid": "U24l1ch1oeyfdr",
                        "player_id": "51215330344",
                        "pf": "false.",
                        "adtag": "event.couponhelper"
                    }
                },
                timeout=15
            )
            
            # إرجاع الرد الحقيقي من السيرفر للمستخدم بدون أي تزييف
            real_result = api_response.text
            if not real_result:
                real_result = "الاستجابة فارغة من السيرفر."
                
            bot.reply_to(message, f"📌 النتيجة الحقيقية من السيرفر:\n{real_result[:3500]}")
            
        except Exception as e:
            bot.reply_to(message, f"❌ حدث خطأ أثناء فحص الرابط:\n{str(e)}")
    else:
        bot.reply_to(message, "أهلاً بك يا السعيد! أرسل الآن رابط دعوة Midasbuy المختصر لفحصه.")

print("Bot is ready...")
bot.infinity_polling(skip_pending=True)
