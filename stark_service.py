import os
import time
import requests
from flask import Flask
from threading import Thread
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import telebot
from telebot import types

TOKEN = "8961573070:AAEmTOgrp0tjG6rkeYJqeOqbHEF9uQvWBWg"
bot = telebot.TeleBot(TOKEN)

# يوزرات الأدمن بدقة (بدون علامة @)
ADMIN_USERNAMES = ["Vartolugaming", "S1_MBA1", "SImba_5", "YAMAC_GAMING"]

# قاعدة بيانات مؤقتة لتخزين (رصيد المستخدمين، اللغة، وهل أخد هدية أول مرة ولا لأ، ورابط الدعوة)
users_db = {}

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

    for i in range(30):
        try:
            response = session.post(short_link_url, headers=headers, json={}, timeout=10)
            if response.status_code == 200:
                data = response.json()
                ret_code = data.get('ret', data.get('code', -1))
                
                if ret_code == 0 or 'success' in response.text.lower():
                    success_count += 1
                elif 'limit' in response.text.lower() or 'complete' in response.text.lower() or ret_code == 1001 or ret_code == 2001:
                    if success_count == 0 and i == 0:
                        return True, "⚠️ عذراً، هذا الرابط دعواته منتهية بالكامل (خلصان 30/30)!"
                    break
                else:
                    failed_count += 1
            else:
                failed_count += 1
                
            time.sleep(1.2)
        except Exception as e:
            failed_count += 1

    if success_count == 0:
        return True, "⚠️ عذراً، هذا الرابط مكتمل بالفعل (خلصان) أو غير صالح!"

    result_msg = f"🎯 عدد اللفات التي تم تنفيذها بنجاح: {success_count} لفة"
    return True, result_msg

def is_admin(username):
    if not username:
        return False
    return username.replace("@", "") in ADMIN_USERNAMES

def get_user_data(user_id, username=''):
    if user_id not in users_db:
        # أول مرة يستخدم البوت -> ياخد 1 لينك هدية مجاني!
        users_db[user_id] = {
            'balance': 1, 
            'lang': 'ar',
            'username': username
        }
    return users_db[user_id]

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    username = message.from_user.username
    args = message.text.split()
    
    # نظام الدعوات (لو دخل من خلال رابط صديقه)
    if len(args) > 1:
        try:
            referrer_id = int(args[1])
            if referrer_id != user_id and referrer_id in users_db:
                # Give referrer a bonus link
                users_db[referrer_id]['balance'] += 1
                try:
                    bot.send_message(referrer_id, "🎉 مبروك! صديقك انضم للبوت من خلال رابطك واشتريت، حصلت على (1 Link) هدية!")
                except:
                    pass
        except:
            pass

    udata = get_user_data(user_id, username)
    lang = udata['lang']
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    if lang == 'ar':
        btn1 = types.KeyboardButton('🛒 شراء Links')
        btn2 = types.KeyboardButton('🔗 إرسال رابط (دعوة صديق)')
        btn3 = types.KeyboardButton('💳 رصيدي')
        btn4 = types.KeyboardButton('📞 تواصل مع الأدمن')
        btn5 = types.KeyboardButton('🌐 Change Language / English')
    else:
        btn1 = types.KeyboardButton('🛒 Buy Links')
        btn2 = types.KeyboardButton('🔗 Invite Friend')
        btn3 = types.KeyboardButton('💳 My Balance')
        btn4 = types.KeyboardButton('📞 Contact Admin')
        btn5 = types.KeyboardButton('🌐 تغيير اللغة / العربية')
        
    markup.add(btn1, btn2, btn3, btn4, btn5)
    
    user_name = message.from_user.first_name if message.from_user.first_name else "صديقي"
    
    if is_admin(username):
        balance_display = "👑 أدمن (رصيد مجاني غير محدود)"
    else:
        balance_display = f"💳 رصيدك الحالي: {udata['balance']} Link (تم إعطاء 1 لينك هدية ترحيبية لأول استخدام 🎁)"

    if lang == 'ar':
        welcome_text = (
            f"أهلاً بك يا <b>{user_name}</b> في بوت <b>STARK</b> 👑\n\n"
            f"{balance_display}\n"
            "🔗 1 Link = 30 Invite\n"
            "🎁 هدية لينك مجاني لكل 5 لينكات يتم شراؤها + لينك هدية عند دعوة صديق!\n\n"
            "اختر الخدمة المطلوبة من القائمة بالأسفل 👇"
        )
    else:
        welcome_text = (
            f"Welcome <b>{user_name}</b> to <b>STARK</b> Bot 👑\n\n"
            f"{balance_display}\n"
            "🔗 1 Link = 30 Invite\n"
            "🎁 Bonus link for every 5 bought + bonus for inviting friends!\n\n"
            "Choose a service below 👇"
        )
        
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup, parse_mode="HTML")

@bot.message_handler(content_types=['photo'])
def handle_docs_photo(message):
    user_name = message.from_user.first_name if message.from_user.first_name else "مستخدم"
    bot.reply_to(message, f"📸 تسلم يا <b>{user_name}</b>، تم استلام إثبات الدفع بنجاح.\n\n⏳ جارٍ مراجعة تفاصيل التحويل وإضافة اللينكات لحسابك فوراً.", parse_mode="HTML")

@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    text = message.text
    chat_id = message.chat.id
    user_id = message.from_user.id
    username = message.from_user.username
    user_name = message.from_user.first_name if message.from_user.first_name else "صديقي"
    
    udata = get_user_data(user_id, username)
    lang = udata['lang']

    if text in ['🌐 Change Language / English', '🌐 تغيير اللغة / العربية']:
        if udata['lang'] == 'ar':
            udata['lang'] = 'en'
        else:
            udata['lang'] = 'ar'
        send_welcome(message)
        return

    if text in ['🛒 شراء Links', '🛒 Buy Links']:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        if lang == 'ar':
            markup.add(
                types.KeyboardButton('🛒 1 Link • 15 EGP'),
                types.KeyboardButton('🛒 2 Links • 30 EGP'),
                types.KeyboardButton('🔥 10 Links • 125 EGP (عرض خاص)'),
                types.KeyboardButton('🛒 5 Links • 75 EGP (+1 هدية)'),
                types.KeyboardButton('✍️ عدد مخصص (اللينك بـ 15 + هدية كل 5)'),
                types.KeyboardButton('❌ إلغاء')
            )
            bot.send_message(chat_id, f"🛒 **شراء Links**\n\nيا {user_name}، اختر الباقة المطلوبة:", reply_markup=markup, parse_mode="Markdown")
        else:
            markup.add(
                types.KeyboardButton('🛒 1 Link • 15 EGP'),
                types.KeyboardButton('🛒 2 Links • 30 EGP'),
                types.KeyboardButton('🔥 10 Links • 125 EGP'),
                types.KeyboardButton('🛒 5 Links • 75 EGP (+1 Bonus)'),
                types.KeyboardButton('✍️ Custom Amount'),
                types.KeyboardButton('❌ Cancel')
            )
            bot.send_message(chat_id, f"🛒 **Buy Links**\n\nChoose your package:", reply_markup=markup, parse_mode="Markdown")
    
    elif text in ['❌ إلغاء', '❌ Cancel', 'الغاء']:
        send_welcome(message)
        
    elif text in ['💳 رصيدي', '💳 My Balance']:
        if is_admin(username):
            balance_str = "👑 أدمن (رصيد مجاني غير محدود)"
        else:
            balance_str = f"💳 رصيدك الحالي: {udata['balance']} Link"
            
        bot.send_message(chat_id, f"💼 **رصيد حسابك:**\n\n{balance_str}", parse_mode="Markdown")
        
    elif text in ['📞 تواصل مع الأدمن', '📞 Contact Admin']:
        admin_text = (
            "📞 **تواصل مع الدعم:**\n\n"
            "👤 @Vartolugaming\n"
            "👤 @S1_MBA1\n"
            "👤 @SImba_5\n"
            "👤 @YAMAC_GAMING\n"
        )
        bot.send_message(chat_id, admin_text, parse_mode="Markdown")

    elif text in ['🔗 إرسال رابط (دعوة صديق)', '🔗 Invite Friend']:
        bot_info = bot.get_me()
        bot_link = f"https://t.me/{bot_info.username}?start={user_id}"
        invite_msg = (
            f"🔗 **رابط دعوة الأصدقاء الخاص بك:**\n\n"
            f"`{bot_link}`\n\n"
            "🎁 شارك هذا الرابط مع أصدقائك، وعندما ينضم أحدهم ويقوم بالشراء ستحصل فوراً على **لينك هدية**!"
        )
        bot.send_message(chat_id, invite_msg, parse_mode="Markdown")

    elif 'Link' in text or 'Links' in text or 'EGP' in text or 'عدد مخصص' in text or 'Custom Amount' in text:
        payment_info = (
            f"📦 **تفاصيل طلب الشراء:**\n"
            f"الباقة: {text}\n\n"
            "💳 **بيانات الدفع (فودافون كاش / InstaPay):**\n"
            "• رقم المحفظة: `01507364191`\n"
            "• InstaPay: `01507364191`\n\n"
            "⚠️ **تنبيه هام:**\n"
            "تأكد من صحة التحويل ووصول الأموال، ثم ابعت Screenshot (صورة التحويل) هنا في البوت مباشرة لإضافة اللينكات ورصيد الهدايا لحسابك!"
        )
        bot.send_message(chat_id, payment_info, parse_mode="Markdown")

    elif 'midasbuy.com' in text or 'http' in text:
        if not is_admin(username):
            if udata['balance'] <= 0:
                bot.send_message(chat_id, f"❌ عذراً يا {user_name}، رصيدك غير كافي (0 Link). يرجى شراء باقة للاستمرار.")
                return
            udata['balance'] -= 1  # خصم لينك مقابل التنفيذ

        msg = bot.send_message(chat_id, f"🚀 جارٍ فحص الرابط وتنفيذ اللفات...")
        success, res = send_3x_help(text.strip())
        bot.edit_message_text(f"⚡ **STARK Result:**\n\n{res}", chat_id=chat_id, message_id=msg.message_id, parse_mode="Markdown")
        
    else:
        bot.send_message(chat_id, f"⚡ أهلاً بك يا {user_name}، ابعت رابط ميداسباي 🚀 وهفحصه وأنفذه أوتوماتيك!")

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
