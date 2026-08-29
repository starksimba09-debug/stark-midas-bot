import os
import time
import re
from curl_cffi import requests
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
    return "Stark Midas Bot with Dynamic Session & Cookies is active!"

def run():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    server_thread = Thread(target=run)
    server_thread.daemon = True
    server_thread.start()

def extract_url(text):
    if not text:
        return None
    urls = re.findall(r'(https?://[^\s]+midasbuy\.com[^\s]+)', text)
    if urls:
        return urls[0].strip()
    return None

def process_with_session(session, url, headers):
    try:
        res = session.get(url, headers=headers, timeout=5)
        if res.status_code != 200:
            res = session.post(url, json={}, headers=headers, timeout=5)
        if res.status_code == 200:
            return res.json()
    except Exception:
        pass
    return None

def send_3x_help(target_url):
    start_time = time.time()
    
    session = requests.Session(impersonate="chrome110")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://www.midasbuy.com/',
        'Origin': 'https://www.midasbuy.com',
        'Connection': 'keep-alive',
    }

    try:
        session.get('https://www.midasbuy.com/', headers=headers, timeout=10)
        first_res = session.get(target_url, headers=headers, timeout=10)
        if first_res.status_code != 200:
            first_res = session.post(target_url, json={}, headers=headers, timeout=10)
            
        if first_res.status_code != 200:
            return False, f"⚠️ عذراً، الموقع رفض الاتصال (كود: {first_res.status_code})."
        
        try:
            data = first_res.json()
        except:
            raw_text = first_res.text[:300]
            return False, f"⚠️ استجابة الموقع ليست JSON.\nالرد:\n<code>{raw_text}</code>"

        res_text_lower = first_res.text.lower()
        if any(word in res_text_lower for word in ['limit', 'complete', 'ended', 'max', 'finish']):
            return False, "⚠️ عذراً، هذا الرابط مكتمل بالفعل (خلصان 30/30)!"

        account_info = data.get('data', {})
        if not isinstance(account_info, dict):
            account_info = data

        player_name = (account_info.get('roleName') or account_info.get('nickname') or data.get('roleName') or "لاعب PUBG")
        player_id = (account_info.get('roleId') or account_info.get('uid') or data.get('roleId') or "غير معروف")
        uc_balance = (account_info.get('balance') or account_info.get('uc') or data.get('balance') or "0")
            
    except Exception as e:
        print(f"Connection Error: {e}")
        return False, f"❌ حدث خطأ أثناء الاتصال: {str(e)}"

    success_count = 1

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(process_with_session, session, target_url, headers) for _ in range(29)]
        for future in futures:
            res_data = future.result()
            if res_data:
                r_code = res_data.get('ret', res_data.get('code', -1))
                if str(r_code) in ["0", "200"] or 'success' in str(res_data).lower():
                    success_count += 1

    elapsed_time = round(time.time() - start_time, 1)

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
        users_db[user_id] = {'balance': 1, 'username': username}
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
        "اختر الخدمة المطلوبة أو أرسل الرابط مباشرة 👇"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=get_main_keyboard(), parse_mode="HTML")

@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    text = message.text.strip()
    chat_id = message.chat.id
    user_id = message.from_user.id
    username = message.from_user.username
    user_name = message.from_user.first_name if message.from_user.first_name else "صديقي"
    
    udata = get_user_data(user_id, username)

    if text == '🛒 شراء Links':
        pay_text = (
            f"🛒 **تواصل مع الأدمن لشراء باقة Links:**\n\n"
            f"💳 **بيانات الدفع (فودافون كاش / InstaPay):**\n"
            f"• رقم المحفظة: `01507364191`\n\n"
            f"📸 **ارسل إثبات التحويل (Screenshot) هنا وسيتم شحن رصيدك فوراً!**"
        )
        bot.send_message(chat_id, pay_text, parse_mode="Markdown")
        return

    elif text == '💳 رصيدي':
        bal = "أدمن (غير محدود) 👑" if is_admin(username) else f"{udata['balance']} Link 💳"
        bot.send_message(chat_id, f"💼 **رصيد حسابك:** {bal}", parse_mode="Markdown")
        return

    elif text == '🔗 دعوة صديق':
        bot_info = bot.get_me()
        bot_link = f"https://t.me/{bot_info.username}?start={user_id}"
        invite_msg = (
            f"🔗 **رابط الدعوة الخاص بك:**\n`{bot_link}`\n\n"
            "🎁 شارك الرابط مع أصدقائك وخذ لينك هدية لكل شخص ينضم!"
        )
        bot.send_message(chat_id, invite_msg, parse_mode="Markdown")
        return

    elif text == '📞 تواصل مع الأدمن':
        admin_markup = types.InlineKeyboardMarkup(row_width=2)
        admin_markup.add(
            types.InlineKeyboardButton("👤 YAMAC_GAMING", url="https://t.me/YAMAC_GAMING"),
            types.InlineKeyboardButton("👤 S1_MBA1", url="https://t.me/S1_MBA1")
        )
        bot.send_message(chat_id, "📞 **اختر الأدمن للمراسلة المباشرة:**", reply_markup=admin_markup, parse_mode="Markdown")
        return

    extracted_url = extract_url(text)
    if extracted_url:
        if not is_admin(username) and udata['balance'] <= 0:
            bot.send_message(chat_id, f"❌ عذراً يا {user_name}، رصيدك غير كافي (0 Link). يرجى الشراء للاستمرار.")
            return

        msg = bot.send_message(chat_id, f"🚀 جارٍ إنشاء جلسة آمنة وتجاوز حماية الموقع...")
        
        success, res = send_3x_help(extracted_url)
        
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
            bot.polling(non_stop=True, interval=1)
        except Exception as e:
            time.sleep(5)

if __name__ == "__main__":
    keep_alive()
    run_telegram_bot()
