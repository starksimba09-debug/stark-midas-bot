import os
import time
import requests
from flask import Flask
from threading import Thread
from concurrent.futures import ThreadPoolExecutor
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import telebot
from telebot import types

TOKEN = "8961573070:AAEmTOgrp0tjG6rkeYJqeOqbHEF9uQvWBWg"
bot = telebot.TeleBot(TOKEN)

ADMIN_USERNAMES = ["YAMAC_GAMING", "S1_MBA1", "SImba_5", "Vartolugaming"]
users_db = {}

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

def process_single_request(session, short_link_url, headers):
    try:
        response = session.post(short_link_url, headers=headers, json={}, timeout=5)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return None

def send_3x_help(short_link_url):
    cookies = get_cached_cookies()
    if not cookies:
        return False, "❌ فشل الاتصال بموقع ميداسباي، حاول مرة أخرى.", None

    session = requests.Session()
    session.cookies.update(cookies)
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'https://www.midasbuy.com/',
        'Origin': 'https://www.midasbuy.com',
        'Content-Type': 'application/json',
        'X-Requested-With': 'XMLHttpRequest'
    }

    # الطلب الأول لجلب بيانات صاحب الرابط الحقيقية (ID, Name, Invites, etc.)
    try:
        first_res = session.post(short_link_url, headers=headers, json={}, timeout=5)
        if first_res.status_code != 200:
            return True, "⚠️ عذراً، الرابط غير صالح أو منتهي!", None
        
        data = first_res.json()
        ret_code = data.get('ret', data.get('code', -1))
        
        # استخراج بيانات الحساب من الاستجابة الفعلية لميداسباي
        # (حسب هيكل استجابة Midasbuy الشائع للروابط القصيرة)
        account_info = data.get('data', {})
        player_id = account_info.get('roleId', account_info.get('uid', account_info.get('openId', 'غير معروف')))
        player_name = account_info.get('roleName', account_info.get('nickname', 'لاعب PUBG'))
        uc_balance = account_info.get('balance', account_info.get('uc', '---'))
        invites_count = account_info.get('invites', account_info.get('count', '0/60'))

        if ret_code not in [0, 200] and 'success' not in first_res.text.lower():
            if 'limit' in first_res.text.lower() or 'complete' in first_res.text.lower():
                return True, "⚠️ عذراً، هذا الرابط مكتمل بالفعل (خلصان 30/30)!", None
    except Exception as e:
        print(f"Error fetching player data: {e}")
        return True, "❌ حدث خطأ أثناء قراءة تفاصيل الرابط.", None

    success_count = 1  # الطلب الأول نجح وتم احتسابه

    # إطلاق باقي الـ 29 طلب بشكل متوازي (بالسرعة القصوى في نفس اللحظة)
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(process_single_request, session, short_link_url, headers) for _ in range(29)]
        for future in futures:
            res_data = future.result()
            if res_data:
                r_code = res_data.get('ret', res_data.get('code', -1))
                if r_code == 0 or 'success' in str(res_data).lower():
                    success_count += 1

    result_msg = (
        f"🆔 **ID:** `{player_id}`\n"
        f"👤 **Name:** `{player_name}`\n"
        f"🎟️ **UC:** `{uc_balance}`\n"
        f"📊 **Invites:** `{success_count}/60`\n\n"
        f"🎯 تم تنفيذ اللفات بنجاح وسرعة فائقة! (الناجح: {success_count})"
    )
    return True, result_msg, player_id

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

def get_main_keyboard(lang='ar'):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    if lang == 'ar':
        btn1 = types.KeyboardButton('🛒 شراء Links')
        btn2 = types.KeyboardButton('💳 رصيدي')
        btn3 = types.KeyboardButton('🔗 دعوة صديق')
        btn4 = types.KeyboardButton('📞 تواصل مع الأدمن')
    else:
        btn1 = types.KeyboardButton('🛒 Buy Links')
        btn2 = types.KeyboardButton('💳 My Balance')
        btn3 = types.KeyboardButton('🔗 Invite Friend')
        btn4 = types.KeyboardButton('📞 Contact Admin')
    markup.add(btn1, btn2, btn3, btn4)
    return markup

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
            "اختر الخدمة المطلوبة من الأزرار بالأسفل 👇"
        )
    else:
        welcome_text = (
            f"Welcome <b>{user_name}</b> to <b>STARK</b> Bot 👑\n\n"
            f"{balance_display}\n"
            "🔗 1 Link = 30 Invite\n"
            "🎁 Bonus link for every 5 bought + bonus for inviting friends!\n\n"
            "Choose a service below 👇"
        )
        
    bot.send_message(message.chat.id, welcome_text, reply_markup=get_main_keyboard(lang), parse_mode="HTML")

@bot.callback_query_handler(func=lambda call: True)
def handle_inline(call):
    user_id = call.from_user.id
    username = call.from_user.username
    chat_id = call.message.chat.id
    
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

    if text in ['🛒 شراء Links', '🛒 Buy Links']:
        if lang == 'ar':
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
        return

    elif text in ['💳 رصيدي', '💳 My Balance']:
        if is_admin(username):
            balance_str = "👑 أدمن (رصيد مجاني غير محدود)"
        else:
            balance_str = f"💳 رصيدك الحالي: {udata['balance']} Link"
        bot.send_message(chat_id, f"💼 **رصيد حسابك:**\n\n{balance_str}", parse_mode="Markdown")
        return

    elif text in ['🔗 دعوة صديق', '🔗 Invite Friend']:
        bot_info = bot.get_me()
        bot_link = f"https://t.me/{bot_info.username}?start={user_id}"
        invite_msg = (
            f"🔗 **رابط دعوة الأصدقاء الخاص بك:**\n\n"
            f"`{bot_link}`\n\n"
            "🎁 شارك هذا الرابط مع أصدقائك، وعندما ينضم أحدهم ستحصل فوراً على **لينك هدية**!"
        )
        bot.send_message(chat_id, invite_msg, parse_mode="Markdown")
        return

    elif text in ['📞 تواصل مع الأدمن', '📞 Contact Admin']:
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
        return

    if 'midasbuy.com' in text or 'http' in text:
        if not is_admin(username):
            if udata['balance'] <= 0:
                bot.send_message(chat_id, f"❌ عذراً يا {user_name}، رصيدك غير كافي (0 Link). يرجى شراء باقة للاستمرار.")
                return

        msg = bot.send_message(chat_id, f"🚀 جارٍ فحص الحساب وتنفيذ اللفات بسرعة الصاروخ...")
        
        success, res, pid = send_3x_help(text.strip())
        
        if "مكتمل بالفعل" in res or "منتهية بالكامل" in res or "غير صالح" in res or "خطأ" in res:
            bot.edit_message_text(f"⚡ **STARK Result:**\n\n{res}\n\n🛡️ <b>ملاحظة:</b> لم يتم خصم أي رصيد لأن الرابط غير صالح أو مكتمل!", chat_id=chat_id, message_id=msg.message_id, parse_mode="HTML")
            return

        if not is_admin(username):
            udata['balance'] -= 1

        bot.edit_message_text(f"⚡ **STARK Result:**\n\n{res}\n\n💳 تم خصم 1 Link. رصيدك المتبقي: {udata['balance']} Link", chat_id=chat_id, message_id=msg.message_id, parse_mode="Markdown")
        return
        
    else:
        bot.send_message(chat_id, f"⚡ أهلاً بك يا {user_name}، استخدم الأزرار بالأسفل أو ابعت رابط ميداسباي 🚀 وسأقوم بتنفيذه في ثوانٍ!")

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
