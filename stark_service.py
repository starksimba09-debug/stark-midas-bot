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

ADMIN_USERNAMES = ["YAMAC_GAMING", "S1_MBA1", "SImba_5", "Vartolugaming"]
users_db = {}

# كاش عام لتخزين الكوكيز وتحديثها لتجنب بطء السيلينيوم المتكرر
cached_cookies = None
last_cookie_time = 0

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

def get_cached_cookies():
    global cached_cookies, last_cookie_time
    if cached_cookies and (time.time() - last_cookie_time < 600):
        return cached_cookies

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    
    driver = webdriver.Chrome(options=chrome_options)
    try:
        driver.get("https://www.midasbuy.com/midasbuy/ot/ug/buy/pubgm")
        time.sleep(2)
        selenium_cookies = driver.get_cookies()
        cached_cookies = {cookie['name']: cookie['value'] for cookie in selenium_cookies}
        last_cookie_time = time.time()
        print("✅ تم تحديث كوكيز ميداسباي بنجاح!")
        return cached_cookies
    except Exception as e:
        print(f"❌ خطأ في توليد الكوكيز: {e}")
        return None
    finally:
        driver.quit()

def send_3x_help(short_link_url):
    cookies = get_cached_cookies()
    if not cookies:
        return False, "❌ فشل الاتصال بموقع ميداسباي، حاول مرة أخرى."

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
            response = session.post(short_link_url, headers=headers, json={}, timeout=5)
            print(f"Request {i+1}: Status {response.status_code} - Text: {response.text[:100]}")
            
            if response.status_code == 200:
                data = response.json()
                ret_code = data.get('ret', data.get('code', -1))
                
                if ret_code == 0 or 'success' in response.text.lower():
                    success_count += 1
                elif 'limit' in response.text.lower() or 'complete' in response.text.lower() or ret_code in [1001, 2001, 400, 500]:
                    if success_count == 0 and i == 0:
                        return True, "⚠️ عذراً، هذا الرابط دعواته منتهية بالكامل (خلصان 30/30)!"
                    break
                else:
                    failed_count += 1
            else:
                failed_count += 1
                
            time.sleep(0.1)
        except Exception as e:
            print(f"Error in request {i+1}: {e}")
            failed_count += 1

    if success_count == 0:
        return True, "⚠️ عذراً، هذا الرابط مكتمل بالفعل (خلصان) أو غير صالح!"

    result_msg = f"🎯 تم تنفيذ اللفات بنجاح حقيقي!\n✅ عدد اللفات الناجحة: <b>{success_count} / 30</b> ⚡"
    return True, result_msg

def is_admin(username):
    if not username:
        return False
    return username.replace("@", "") in ADMIN_USERNAMES

def get_user_data(user_id, username=''):
    if user_id not in users_db:
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
    
    if len(args) > 1:
        try:
            referrer_id = int(args[1])
            if referrer_id != user_id and referrer_id in users_db:
                users_db[referrer_id]['balance'] += 1
                try:
                    bot.send_message(referrer_id, "🎉 مبروك! صديقك انضم للبوت من خلال رابطك، حصلت على (1 Link) هدية!")
                except:
                    pass
        except:
            pass

    udata = get_user_data(user_id, username)
    lang = udata['lang']
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    if lang == 'ar':
        btn1 = types.InlineKeyboardButton('🛒 شراء Links', callback_data='buy_links')
        btn2 = types.InlineKeyboardButton('🔗 إرسال رابط (دعوة صديق)', callback_data='invite_friend')
        btn3 = types.InlineKeyboardButton('💳 رصيدي', callback_data='my_balance')
        btn4 = types.InlineKeyboardButton('📞 تواصل مع الأدمن', callback_data='contact_admin')
        btn5 = types.InlineKeyboardButton('🌐 Change Language / English', callback_data='change_lang')
    else:
        btn1 = types.InlineKeyboardButton('🛒 Buy Links', callback_data='buy_links')
        btn2 = types.InlineKeyboardButton('🔗 Invite Friend', callback_data='invite_friend')
        btn3 = types.InlineKeyboardButton('💳 My Balance', callback_data='my_balance')
        btn4 = types.InlineKeyboardButton('📞 Contact Admin', callback_data='contact_admin')
        btn5 = types.InlineKeyboardButton('🌐 تغيير اللغة / العربية', callback_data='change_lang')
        
    markup.add(btn1, btn2)
    markup.add(btn3, btn4)
    markup.add(btn5)
    
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

@bot.callback_query_handler(func=lambda call: True)
def handle_inline(call):
    user_id = call.from_user.id
    username = call.from_user.username
    chat_id = call.message.chat.id
    udata = get_user_data(user_id, username)
    lang = udata['lang']

    if call.data == 'contact_admin':
        bot.answer_callback_query(call.id)
        admin_markup = types.InlineKeyboardMarkup(row_width=2)
        admin_markup.add(
            types.InlineKeyboardButton("👤 YAMAC_GAMING", url="https://t.me/YAMAC_GAMING"),
            types.InlineKeyboardButton("👤 S1_MBA1", url="https://t.me/S1_MBA1"),
            types.InlineKeyboardButton("👤 SImba_5", url="https://t.me/SImba_5"),
            types.InlineKeyboardButton("👤 Vartolugaming", url="https://t.me/Vartolugaming")
        )
        bot.send_message(
            chat_id, 
            "📞 **اختر الأدمن الذي تريد التحدث معه مباشرة:**\n\nارسل مشكلتك أو إثبات التحويل وسيتم الرد عليك في أقرب وقت!", 
            reply_markup=admin_markup, 
            parse_mode="Markdown"
        )

    elif call.data == 'change_lang':
        udata['lang'] = 'en' if lang == 'ar' else 'ar'
        bot.answer_callback_query(call.id)
        fake_msg = call.message
        fake_msg.text = "/start"
        send_welcome(fake_msg)

    elif call.data == 'buy_links':
        bot.answer_callback_query(call.id)
        if udata['lang'] == 'ar':
            buy_text = (
                "🛒 **شراء Links**\n\n"
                "• 1 Link • 15 EGP\n"
                "• 2 Links • 30 EGP\n"
                "• 5 Links • 75 EGP (+1 هدية)\n"
                "• 10 Links • 125 EGP (عرض خاص)\n"
                "• عدد مخصص (اللينك بـ 15 + هدية كل 5)\n\n"
                "💳 **بيانات الدفع (فودافون كاش / InstaPay):**\n"
                "• رقم المحفظة: `01507364191`\n"
                "• InstaPay: `01507364191`\n\n"
                "📸 ابعت Screenshot التحويل هنا مباشرة بعد التحويل!"
            )
        else:
            buy_text = (
                "🛒 **Buy Links**\n\n"
                "• 1 Link • 15 EGP\n"
                "• 2 Links • 30 EGP\n"
                "• 5 Links • 75 EGP (+1 Bonus)\n"
                "• 10 Links • 125 EGP\n"
                "• Custom Amount\n\n"
                "💳 **Payment Info (Vodafone Cash / InstaPay):**\n"
                "• Wallet: `01507364191`\n\n"
                "📸 Send screenshot here after transfer!"
            )
        bot.send_message(chat_id, buy_text, parse_mode="Markdown")

    elif call.data == 'my_balance':
        bot.answer_callback_query(call.id)
        if is_admin(username):
            balance_str = "👑 أدمن (رصيد مجاني غير محدود)"
        else:
            balance_str = f"💳 رصيدك الحالي: {udata['balance']} Link"
        bot.send_message(chat_id, f"💼 **رصيد حسابك:**\n\n{balance_str}", parse_mode="Markdown")

    elif call.data == 'invite_friend':
        bot.answer_callback_query(call.id)
        bot_info = bot.get_me()
        bot_link = f"https://t.me/{bot_info.username}?start={user_id}"
        invite_msg = (
            f"🔗 **رابط دعوة الأصدقاء الخاص بك:**\n\n"
            f"`{bot_link}`\n\n"
            "🎁 شارك هذا الرابط مع أصدقائك، وعندما ينضم أحدهم ستحصل فوراً على **لينك هدية**!"
        )
        bot.send_message(chat_id, invite_msg, parse_mode="Markdown")

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

    if 'midasbuy.com' in text or 'http' in text:
        if not is_admin(username):
            if udata['balance'] <= 0:
                bot.send_message(chat_id, f"❌ عذراً يا {user_name}، رصيدك غير كافي (0 Link). يرجى شراء باقة للاستمرار.")
                return

        msg = bot.send_message(chat_id, f"🚀 جارٍ فحص حالة الرابط وتنفيذ اللفات...")
        
        success, res = send_3x_help(text.strip())
        
        # حماية الرصيد: لو الرابط خلصان أو منتهي مش بيخصم رصيد
        if "مكتمل بالفعل" in res or "منتهية بالكامل" in res or "غير صالح" in res or "فشل" in res:
            bot.edit_message_text(f"⚡ **STARK Result:**\n\n{res}\n\n🛡️ <b>ملاحظة:</b> لم يتم خصم أي رصيد لأن الرابط غير صالح أو مكتمل!", chat_id=chat_id, message_id=msg.message_id, parse_mode="HTML")
            return

        if not is_admin(username):
            udata['balance'] -= 1

        bot.edit_message_text(f"⚡ **STARK Result:**\n\n{res}\n\n💳 تم خصم 1 Link بنجاح. رصيدك المتبقي: {udata['balance']} Link", chat_id=chat_id, message_id=msg.message_id, parse_mode="HTML")
        return
        
    else:
        bot.send_message(chat_id, f"⚡ أهلاً بك يا {user_name}، ابعت رابط ميداسباي 🚀 وهفحصه وأنفذه في ثوانٍ معدودة!")

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
