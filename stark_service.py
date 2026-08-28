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

# قائمة يوزرات الأدمن والدعم (رصيد دائم ومجاني غير محدود للمنشئ والدعم فقط)
ADMIN_USERNAMES = ["Vartolugaming", "S1_MBA1", "SImba_5", "YAMAC_GAMING"]

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

# دالة ذكية لفحص الرابط ومعرفة عدد اللفات المتبقية وتنفذيها بدقة
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

    success_count = 0
    failed_count = 0
    remaining_slots = 30  # الافتراضي الحد الأقصى

    # محاولة معرفة الحالة الأولى للرابط أو إرسال طلبات تدريجية لقياس الاستجابة
    for i in range(30):
        try:
            response = session.post(short_link_url, headers=headers, json={}, timeout=10)
            if response.status_code == 200:
                data = response.json()
                ret_code = data.get('ret', data.get('code', -1))
                
                # لو الطلب نجح واتقبلت المساعدة
                if ret_code == 0 or 'success' in response.text.lower():
                    success_count += 1
                # لو السيرفر رد إن الرابط اكتمل بالكامل (خلصان)
                elif 'limit' in response.text.lower() or 'complete' in response.text.lower() or ret_code == 1001 or ret_code == 2001:
                    if success_count == 0 and i == 0:
                        return True, "⚠️ عذراً، هذا الرابط **دعواته منتهية بالكامل (خلصان 30/30)** ولا يقبل أي لفات جديدة!"
                    break
                else:
                    failed_count += 1
            else:
                failed_count += 1
                
            time.sleep(1.2)
        except Exception as e:
            failed_count += 1

    if success_count == 0:
        return True, "⚠️ عذراً، هذا الرابط **مكتمل بالفعل (خلصان)** أو غير صالح!"

    result_msg = (
        f"🎯 **تقرير حالة الرابط:**\n\n"
        f"✅ عدد اللفات التي تم تنفيذها بنجاح: **{success_count} لفة**\n"
        f"⚠️ محاولات فاشلة أو روابط متوقفة: {failed_count}\n"
        f"📊 الحالة النهائية: الرابط استنفد محاولاته أو تم اكتماله بنجاح!"
    )
    return True, result_msg

# فحص هل المستخدم أدمن أو منشئ أم لا
def is_admin(username):
    if not username:
        return False
    return username.replace("@", "") in ADMIN_USERNAMES

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
    
    user = message.from_user
    user_name = user.first_name if user.first_name else "صديقي"
    user_type = "👑 أدمن (رصيد مجاني غير محدود)" if is_admin(user.username) else "💳 الرصيد: Link 0"
    
    welcome_text = (
        f"أهلاً بك يا <b>{user_name}</b> في بوت Ⓢ ➂ Ⓔ Ⓔ Ⓓ 👑\n\n"
        "تم تفعيل حسابك بنجاح وأصبح جاهزًا للاستخدام.\n\n"
        f"{user_type}\n"
        "🎁 Free Link: غير متاحة\n"
        "🔗 1 Link = 30 Invite\n"
        "⚡ COMPLETE 60 = 30 Invite إضافية\n\n"
        "اختر الخدمة المطلوبة من القائمة بالأسفل 👇"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup, parse_mode="HTML")

# استقبال صور الإسبرين شوت (إثبات الدفع)
@bot.message_handler(content_types=['photo'])
def handle_docs_photo(message):
    user = message.from_user
    user_name = user.first_name if user.first_name else "مستخدم"
    username = f"@{user.username}" if user.username else "بدون يوزر"
    chat_id = message.chat.id

    bot.reply_to(message, f"📸 تسلم يا <b>{user_name}</b>، تم استلام إثبات الدفع بنجاح.\n\n⏳ جارٍ مراجعة تفاصيل التحويل والتأكد من وصول الأموال لإضافة اللينكات لحسابك فوراً.", parse_mode="HTML")

@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    text = message.text
    chat_id = message.chat.id
    user = message.from_user
    user_name = user.first_name if user.first_name else "صديقي"
    username = user.username
    
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
        bot.send_message(chat_id, f"🛒 **شراء Links**\n\nيا {user_name}، اختر الباقة المطلوبة من الأسفل لتظهر لك بيانات الدفع والتحويل.", reply_markup=markup, parse_mode="Markdown")
    
    elif text == '❌ إلغاء' or text == 'الغاء':
        send_welcome(message)
        
    elif text == '💳 رصيدي':
        if is_admin(username):
            balance_str = "👑 أدمن (رصيد دائم ومجاني غير محدود)"
        else:
            balance_str = "💳 الرصيد: Link 0 (يلزم الشراء للمتابعة)"
            
        bot.send_message(chat_id, f"💼 **رصيد حسابك يا {user_name}**\n\n{balance_str}\n🎁 Free Link: غير متاحة\n🔗 1 Link = 30 Invite\n⚡ COMPLETE 60 = 30 Invite إضافية", parse_mode="Markdown")
        
    elif text == '📞 تواصل مع الأدمن':
        admin_text = (
            f"📞 **تواصل مع الدعم يا {user_name}:**\n\n"
            "يمكنك مراسلة أحد الإداريين عبر اليوزرات التالية:\n"
            "👤 @Vartolugaming\n"
            "👤 @S1_MBA1\n"
            "👤 @SImba_5\n"
            "👤 @YAMAC_GAMING\n\n"
            "ارسل مشكلتك أو إثبات الدفع بعد التأكد من صحته وسيتم الرد عليك في أقرب وقت!"
        )
        bot.send_message(chat_id, admin_text, parse_mode="Markdown")

    elif 'Links' in text or 'Link' in text:
        payment_info = (
            f"📦 **تفاصيل طلب الشراء (يا {user_name}):**\n"
            f"الباقة المختارة: {text}\n\n"
            "💳 **بيانات الدفع (فودافون كاش / InstaPay):**\n"
            "• رقم المحفظة: `01507364191`\n"
            "• InstaPay: `01507364191`\n\n"
            "⚠️ **تنبيه هام جداً:**\n"
            "يجب التأكد من أن الأموال قد تم تحويلها بالفعل وبشكل صحيح قبل إرسال الإيصال.\n\n"
            "📸 **بعد التأكد والتحويل:**\n"
            "ابعت Screenshot التحويل هنا مباشرة، وسيتم مراجعته وإضافة اللينكات لحسابك!"
        )
        bot.send_message(chat_id, payment_info, parse_mode="Markdown")

    elif 'midasbuy.com' in text or 'short_link' in text:
        # التحقق: لو مستخدم عادي ورصيده 0، يمنعه ويطلب منه الشراء (ماعدا الأدمن)
        if not is_admin(username):
            bot.send_message(chat_id, f"❌ عذراً يا {user_name}، رصيدك غير كافي (Link 0). يرجى شراء باقة من القائمة للاستمرار.")
            return

        msg = bot.send_message(chat_id, f"🚀 يا {user_name}، Stark Bot يفحص الرابط ويحسب اللفات المتبقية لتنفيذها الآن...")
        success, res = send_3x_help(text.strip())
        bot.edit_message_text(f"⚡ **Stark Result:**\n\n{res}", chat_id=chat_id, message_id=msg.message_id, parse_mode="Markdown")
        
    else:
        bot.send_message(chat_id, f"⚡ أهلاً بك يا {user_name}، ابعت رابط ميداسباي 🚀 وهفحصه وأنفذه أوتوماتيك!")

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
