import os
import time
import requests
from flask import Flask
from threading import Thread
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import telebot
from telebot import types

# توكن البوت الحقيقي
TOKEN = "8961573070:AAEmTOgrp0tjG6rkeYJqeOqbHEF9uQvWBWg"
bot = telebot.TeleBot(TOKEN)

# إعداد سيرفر الويب لضمان بقاء البوت شغال 24/7 على Railway
app = Flask('')

@app.route('/')
def home():
    return "Stark Midas Bot is active and running 24/7!"

def run():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    server_thread = Thread(target=run)
    server_thread.daemon = True
    server_thread.start()

# دالة توليد الكوكيز أوتوماتيك باستخدام متصفح خفي (Headless Chrome)
def generate_fresh_cookies():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    
    driver = webdriver.Chrome(options=chrome_options)
    try:
        driver.get("https://www.midasbuy.com/midasbuy/ot/ug/buy/pubgm")
        time.sleep(5)
        selenium_cookies = driver.get_cookies()
        cookies_dict = {cookie['name']: cookie['value'] for cookie in selenium_cookies}
        return cookies_dict
    except Exception as e:
        print(f"Error generating cookies: {e}")
        return None
    finally:
        driver.quit()

# دالة فحص الرابط وتنفيذه بشكل حقيقي بناءً على حالته الفعليه
def send_3x_help(short_link_url):
    cookies = generate_fresh_cookies()
    if not cookies:
        return False, "❌ فشل توليد الكوكيز أوتوماتيك، حاول مرة أخرى."

    session = requests.Session()
    session.cookies.update(cookies)
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'https://www.midasbuy.com/',
        'Origin': 'https://www.midasbuy.com',
        'Content-Type': 'application/json',
        'X-Requested-With': 'XMLHttpRequest'
    }

    # 1. الخطوة الأولى: فحص الرابط لمعرفة هل هو خلصان ولا لسه؟
    try:
        check_response = session.get(short_link_url, headers=headers, timeout=10)
        if check_response.status_code == 200:
            check_data = check_response.json()
            if check_data.get('data', {}).get('is_completed') == True or check_data.get('msg') == 'completed':
                return True, "⚠️ عذراً، هذا الرابط **مكتمل بالفعل (خلصان)** ولا يقبل مساعدات جديدة!"
    except Exception as e:
        print(f"Check link warning: {e}")

    # 2. الخطوة التانية: لو الرابط لسه شغال، نبدا ننفذ الـ 30 مساعدة حقيقي
    success_count = 0
    failed_count = 0

    for i in range(30):
        try:
            response = session.post(short_link_url, headers=headers, json={}, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('ret') == 0 or data.get('code') == 0:
                    success_count += 1
                elif 'limit' in response.text.lower() or 'complete' in response.text.lower():
                    # لو الرابط خلص للنهاية أثناء اللفات
                    break
                else:
                    failed_count += 1
            else:
                failed_count += 1
                
            time.sleep(1.5)
        except Exception as e:
            failed_count += 1

    result_msg = f"✅ تم التنفيذ الحقيقي بنجاح: {success_count}/30\n⚠️ روابط منتهية أو مكتملة: {failed_count}"
    return True, result_msg

# --- أزرار وتفاعلات بوت التليجرام ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn1 = types.KeyboardButton('🛒 شراء Links')
    btn2 = types.KeyboardButton('🔗 إرسال رابط')
    btn3 = types.KeyboardButton('💳 رصيدي')
    btn4 = types.KeyboardButton('📞 تواصل مع الأدمن')
    btn5 = types.KeyboardButton('🌐 تغيير اللغة')
    markup.add(btn1, btn2, btn3, btn4, btn5)
    
    welcome_text = (
        "👑 Ⓢ ➂ Ⓔ Ⓔ Ⓓ 👑\n\n"
        "تم تفعيل حسابك بنجاح وأصبح جاهزًا للاستخدام.\n\n"
        "💳 الرصيد: Link 0\n"
        "🎁 Free Link: غير متاحة\n"
        "🔗 1 Link = 30 Invite\n"
        "⚡ COMPLETE 60 = 30 Invite إضافية\n\n"
        "اختر الخدمة المطلوبة من القائمة بالأسفل 👇"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    text = message.text
    chat_id = message.chat.id
    
    if text == '🛒 شراء Links':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        markup.add(
            types.KeyboardButton('🔥 15+2 = 17 Links | 250 EGP | 5 USDT'),
            types.KeyboardButton('🛒 2 Link • 40 EGP • 0.8 USDT'),
            types.KeyboardButton('🛒 5 Link • 100 EGP • 2 USDT'),
            types.KeyboardButton('🛒 10 Link • 200 EGP • 4 USDT'),
            types.KeyboardButton('🛒 50 Link • 1000 EGP • 20 USDT'),
            types.KeyboardButton('✍️ عدد مخصص'),
            types.KeyboardButton('❌ إلغاء')
        )
        bot.send_message(chat_id, "🛒 **شراء Links**\n\nاختر الباقة المطلوبة من الأسفل لتظهر لك بيانات الدفع والتحويل.", reply_markup=markup, parse_mode="Markdown")
    
    elif text == '❌ إلغاء' or text == 'الغاء':
        send_welcome(message)
        
    elif text == '💳 رصيدي':
        bot.send_message(chat_id, "💼 **رصيد حسابك**\n\n💳 الرصيد: Link 0\n🎁 Free Link: غير متاحة\n🔗 1 Link = 30 Invite\n⚡ COMPLETE 60 = 30 Invite إضافية", parse_mode="Markdown")
        
    elif text == '📞 تواصل مع الأدمن':
        admin_text = (
            "📞 **للتواصل مع الدعم والأدمن مباشرة:**\n\n"
            "يمكنك مراسلة أحد الإداريين عبر اليوزرات التالية:\n"
            "👤 @Vartolugaming\n"
            "👤 @S1_MBA1\n"
            "👤 @SImba_5\n\n"
            "ارسل مشكلتك أو إثبات الدفع وسيتم الرد عليك في أقرب وقت!"
        )
        bot.send_message(chat_id, admin_text, parse_mode="Markdown")

    elif 'Links' in text or 'Link' in text:
        payment_info = (
            f"📦 **تفاصيل طلب الشراء:**\n"
            f"الباقة المختارة: {text}\n\n"
            "💳 **بيانات الدفع (فودافون كاش / InstaPay):**\n"
            "• رقم المحفظة: `01507364191`\n"
            "• InstaPay: `01507364191`\n\n"
            "📸 **بعد التحويل:**\n"
            "ابعت Screenshot الدفع هنا مباشرة، وسيتم مراجعة الطلب وإضافة الرصيد فوراً!"
        )
        bot.send_message(chat_id, payment_info, parse_mode="Markdown")

    elif 'midasbuy.com' in text or 'short_link' in text:
        msg = bot.send_message(chat_id, "🚀 Stark Bot بيفحص الرابط وينفذ العجلات الحقيقية الآن...")
        success, res = send_3x_help(text.strip())
        bot.edit_message_text(f"⚡ **Stark Result:**\n\n{res}", chat_id=chat_id, message_id=msg.message_id, parse_mode="Markdown")
        
    else:
        bot.send_message(chat_id, "⚡ جاهز، ابعت رابط ميداسباي 🚀 وهفحصه وأنفذه أوتوماتيك!")

# تشغيل البوت مع السيرفر 24/7
def run_telegram_bot():
    while True:
        try:
            bot.polling(non_stop=True, interval=2, timeout=20)
        except Exception as e:
            print(f"Telegram Bot Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    keep_alive()
    run_telegram_bot()
