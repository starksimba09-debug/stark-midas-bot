import os
import time
import requests
from flask import Flask
from threading import Thread
from concurrent.futures import ThreadPoolExecutor
import telebot
from telebot import types

TOKEN = "8961573070:AAEmTOgrp0tjG6rkeYJqeOqbHEF9uQvWBWg"
bot = telebot.TeleBot(TOKEN)

ADMIN_USERNAMES = ["YAMAC_GAMING", "S1_MBA1", "SImba_5", "Vartolugaming"]
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

def process_single_request(session, short_link_url, headers):
    try:
        response = session.post(short_link_url, headers=headers, json={}, timeout=3)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return None

def send_3x_help(short_link_url):
    start_time = time.time()
    
    session = requests.Session()
    # تعديل الـ Headers لتبدو وكأنها طلب حقيقي من متصفح هاتف/كمبيوتر لتجاوز حماية ميداسباي
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'ar,en-US;q=0.9,en;q=0.8',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36',
        'Referer': 'https://www.midasbuy.com/',
        'Origin': 'https://www.midasbuy.com',
        'Content-Type': 'application/json;charset=UTF-8',
        'X-Requested-With': 'XMLHttpRequest'
    }

    try:
        # الطلب الأول لجلب بيانات الحساب وصاحب الرابط
        first_res = session.post(short_link_url, headers=headers, json={}, timeout=5)
        
        # طباعة الاستجابة في الـ Logs للرؤية لو فيه مشكلة
        print(f"Midas Response Status: {first_res.status_code}")
        print(f"Midas Response Text: {first_res.text[:200]}")

        if first_res.status_code != 200:
            return False, "⚠️ عذراً، الرابط غير صالح أو مرفوض من Midasbuy."
        
        data = first_res.json()
        
        # استخراج بيانات الحساب بدقة من مسارات الاستجابة المختلفة
        account_info = data.get('data', {})
        if not isinstance(account_info, dict):
            account_info = data

        player_name = (
            account_info.get('roleName') or 
            account_info.get('nickname') or 
            account_info.get('name') or 
            data.get('roleName') or 
            data.get('nickname') or 
            "لاعب PUBG"
        )
        
        player_id = (
            account_info.get('roleId') or 
            account_info.get('uid') or 
            account_info.get('openId') or 
            data.get('roleId') or 
            data.get('uid') or 
            "غير معروف"
        )
        
        uc_balance = (
            account_info.get('balance') or 
            account_info.get('uc') or 
            data.get('balance') or 
            data.get('uc') or 
            "0"
        )
        
        # التحقق إذا كان الرابط خلصان (30/30) بناءً على الكود أو الرسالة
        res_text_lower = first_res.text.lower()
        ret_code = data.get('ret', data.get('code', 0))
        
        if ret_code not in [0, 200, "0", "200"] and 'success' not in res_text_lower:
            if 'limit' in res_text_lower or 'complete' in res_text_lower or 'ended' in res_text_lower or 'max' in res_text_lower:
                return False, "⚠️ عذراً، هذا الرابط مكتمل بالفعل (خلصان 30/30)!"
            
    except Exception as e:
        print(f"Error fetching player data: {e}")
        return False, "❌ حدث خطأ أثناء الاتصال بموقع ميداسباي."

    success_count = 1

    # إطلاق الـ 29 طلب الباقية بالتوازي بالسرعة القصوى
    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = [executor.submit(process_single_request, session, short_link_url, headers) for _ in range(29)]
        for future in futures:
            res_data = future.result()
            if res_data:
                r_code = res_data.get('ret', res_data.get('code', 0))
                if r_code in [0, 200, "0", "200"] or 'success' in str(res_data).lower():
                    success_count += 1

    elapsed_time = round(time.time() - start_time, 1)

    # تنسيق الرسالة النهائي المظبوط تماماً زي ما طلبت
    result_msg = (
        f"تم {success_count}/30\n"
        f"• {uc_balance} . 💰\n"
        f"• في {elapsed_time} ثانيه ⚙️\n"
        f"• {player_name} 🌸\n"
        f"• {player_id} 🆔"
    )
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
    
    elif call.data.startswith('buy_'):
        bot.answer_callback_query(call.id)
        package = call.data.split('_')[1]
        prices = {'1': '15 ج.م', '2': '30 ج.م', '5': '75 ج.م (+1 هدية)', '10': '125 ج.م'}
        price = prices.get(package, 'حسب الطلب')
        
        pay_text = (
            f"🛒 **تفاصيل طلب شراء {package} Link**\n\n"
            f"💰 السعر المطلوب: `{price}`\n\n"
            f"💳 **بيانات الدفع (فودافون كاش / InstaPay):**\n"
            f"• رقم المحفظة (فودافون كاش): `01507364191`\n"
            f"• InstaPay: `01507364191`\n\n"
            f"📸 **الرجاء إرسال صورة (Screenshot) للتحويل هنا في الشات وسيتم إضافة اللينكات لحسابك فوراً!**"
        )
        bot.send_message(chat_id, pay_text, parse_mode="Markdown")

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
        buy_markup = types.InlineKeyboardMarkup(row_width=2)
        buy_markup.add(
            types.InlineKeyboardButton("1 Link (15 EGP)", callback_data="buy_1"),
            types.InlineKeyboardButton("2 Links (30 EGP)", callback_data="buy_2"),
            types.InlineKeyboardButton("5 Links (+1 هدية)", callback_data="buy_5"),
            types.InlineKeyboardButton("10 Links (عرض خاص)", callback_data="buy_10")
        )
        bot.send_message(
            chat_id, 
            "🛒 **اختر الباقة المناسبة للشراء من الأزرار بالأسفل:**\n\n🎁 هدية لينك مجاني لكل 5 لينكات يتم شراؤها!", 
            reply_markup=buy_markup, 
            parse_mode="Markdown"
        )
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

        msg = bot.send_message(chat_id, f"🚀 جارٍ معالجة الرابط وجلب البيانات...")
        
        success, res = send_3x_help(text.strip())
        
        if not success:
            bot.edit_message_text(f"⚠️ **تنبيه:**\n\n{res}\n\n🛡️ <b>لم يتم خصم أي رصيد!</b>", chat_id=chat_id, message_id=msg.message_id, parse_mode="HTML")
            return

        if not is_admin(username):
            udata['balance'] -= 1

        bot.edit_message_text(res, chat_id=chat_id, message_id=msg.message_id)
        return
        
    else:
        bot.send_message(chat_id, f"⚡ أهلاً بك يا {user_name}، استخدم الأزرار بالأسفل أو ابعت رابط ميداسباي 🚀 وسأقوم بتنفيذه فوراً!")

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
