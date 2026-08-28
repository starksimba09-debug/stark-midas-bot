import os
import time
import re
import requests
from flask import Flask
from threading import Thread
from concurrent.futures import ThreadPoolExecutor
import telebot
from telebot import types

TOKEN = "8961573070:AAEmTOgrp0tjG6rkeYJqeOqbHEF9uQvWBWg" # توكن بوتك
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

def extract_url(text):
    # استخراج دقيق لأي رابط ميداسباي سواء قصير أو API
    urls = re.findall(r'(https?://[^\s]+midasbuy\.com[^\s]+)', text)
    if urls:
        return urls[0].strip()
    return None

def process_single_request(url, headers):
    try:
        # استخدام جلسة مؤقتة سريعة لكل طلب
        with requests.Session() as s:
            res = s.get(url, headers=headers, timeout=3, verify=False)
            if res.status_code == 200:
                return res.json()
    except:
        pass
    return None

def send_3x_help(target_url):
    start_time = time.time()
    
    # هيدرز احترافية لتخطي حماية ميداسباي والظهور كمتصفح موبايل حقيقي
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 13; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'ar,en-US;q=0.9,en;q=0.8',
        'Referer': 'https://www.midasbuy.com/midasbuy/ot/ug/buy/pubgm',
        'Origin': 'https://www.midasbuy.com',
        'Connection': 'keep-alive',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'X-Requested-With': 'XMLHttpRequest'
    }

    try:
        # الطلب الأساسي لجلب البيانات
        first_res = requests.get(target_url, headers=headers, timeout=5, verify=False)
        
        if first_res.status_code != 200:
            return False, f"⚠️ عذراً، الموقع رفض الاتصال (كود {first_res.status_code}). تأكد من الرابط."
        
        try:
            data = first_res.json()
        except:
            return False, "⚠️ عذراً، استجابة موقع ميداسباي غير صالحة."

        res_text_lower = first_res.text.lower()
        if 'limit' in res_text_lower or 'complete' in res_text_lower or 'ended' in res_text_lower or 'max' in res_text_lower or 'finish' in res_text_lower:
            return False, "⚠️ عذراً، هذا الرابط مكتمل بالفعل (خلصان 30/30)!"

        # استخراج البيانات بذكاء
        account_info = data.get('data', {})
        if not isinstance(account_info, dict):
            account_info = data

        player_name = (account_info.get('roleName') or account_info.get('nickname') or data.get('roleName') or "غير معروف")
        player_id = (account_info.get('roleId') or account_info.get('uid') or data.get('roleId') or "غير معروف")
        uc_balance = (account_info.get('balance') or account_info.get('uc') or data.get('balance') or "0")
            
    except Exception as e:
        print(f"Connection Error: {e}")
        return False, "❌ حدث خطأ أثناء الاتصال بموقع ميداسباي."

    success_count = 1

    # تنفيذ باقي الـ 29 طلب بسرعة الصاروخ
    with ThreadPoolExecutor(max_workers=30) as executor:
        futures = [executor.submit(process_single_request, target_url, headers) for _ in range(29)]
        for future in futures:
            res_data = future.result()
            if res_data:
                # التحقق من نجاح الطلب
                r_code = res_data.get('ret', res_data.get('code', -1))
                if str(r_code) in ["0", "200"] or 'success' in str(res_data).lower():
                    success_count += 1

    elapsed_time = round(time.time() - start_time, 1)

    # الرسالة المطابقة للبوت التاني بالظبط
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
        users_db[user_id] = {'balance': 1, 'lang': 'ar', 'username': username}
    return users_db[user_id]

def get_main_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton('🛒 شراء Links'),
        types.KeyboardButton('💳 رصيدي'),
        types.KeyboardButton('🔗 دعوة صديق'),
        types.KeyboardButton('📞 تواصل مع الأدمن')
    )
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    username = message.from_user.username
    udata = get_user_data(user_id, username)
    user_name = message.from_user.first_name if message.from_user.first_name else "صديقي"
    
    if is_admin(username):
        balance_display = "👑 أدمن (رصيد مجاني غير محدود)"
    else:
        balance_display = f"💳 رصيدك الحالي: {udata['balance']} Link"

    welcome_text = (
        f"أهلاً بك يا <b>{user_name}</b> في بوت <b>STARK</b> 👑\n\n"
        f"{balance_display}\n"
        "🔗 1 Link = 30 Invite\n"
        "🎁 هدية لينك مجاني لكل 5 لينكات يتم شراؤها + لينك هدية عند دعوة صديق!\n\n"
        "اختر الخدمة المطلوبة من الأزرار بالأسفل 👇"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=get_main_keyboard(), parse_mode="HTML")

@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    text = message.text
    chat_id = message.chat.id
    user_id = message.from_user.id
    username = message.from_user.username
    user_name = message.from_user.first_name if message.from_user.first_name else "صديقي"
    
    udata = get_user_data(user_id, username)

    # الأزرار الأساسية
    if text == '🛒 شراء Links':
        bot.send_message(chat_id, "🛒 تواصل مع الأدمن لشراء باقة.")
        return
    elif text == '💳 رصيدي':
        bal = "أدمن" if is_admin(username) else f"{udata['balance']} Link"
        bot.send_message(chat_id, f"💼 **رصيد حسابك:** {bal}", parse_mode="Markdown")
        return
    elif text == '🔗 دعوة صديق':
        bot.send_message(chat_id, "🔗 رابط الدعوة الخاص بك...")
        return
    elif text == '📞 تواصل مع الأدمن':
        bot.send_message(chat_id, "📞 تواصل مع: @YAMAC_GAMING")
        return

    # استخراج الرابط من رسالة اللعبة
    extracted_url = extract_url(text)
    
    if extracted_url:
        if not is_admin(username) and udata['balance'] <= 0:
            bot.send_message(chat_id, f"❌ رصيدك غير كافي (0 Link).")
            return

        msg = bot.send_message(chat_id, f"🚀 جارٍ التنفيذ الفوري...")
        
        # إرسال الرابط للمعالجة
        success, res = send_3x_help(extracted_url)
        
        if not success:
            bot.edit_message_text(f"⚠️ **تنبيه:**\n\n{res}\n\n🛡️ <b>لم يتم خصم أي رصيد!</b>", chat_id=chat_id, message_id=msg.message_id, parse_mode="HTML")
            return

        # خصم الرصيد في حالة النجاح فقط
        if not is_admin(username):
            udata['balance'] -= 1

        bot.edit_message_text(res, chat_id=chat_id, message_id=msg.message_id)
    else:
        bot.send_message(chat_id, f"⚡ ابعت رابط ميداسباي 🚀 وسأقوم بتنفيذه فوراً!")

def run_telegram_bot():
    while True:
        try:
            bot.polling(non_stop=True)
        except Exception as e:
            time.sleep(5)

if __name__ == "__main__":
    keep_alive()
    run_telegram_bot()
