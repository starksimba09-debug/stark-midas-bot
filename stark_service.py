import os
import time
import random
import re
import json
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
    return "Stark Midas Bot is active with Manual Proxy Pool!"

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

# لستة البروكسيات الحقيقية المحدثة لتخطي حظر كلاود فلير
PROXIES_POOL = [
    "http://139.255.74.124:8080",
    "http://14.161.10.46:80",
    "http://165.101.230.76:8080",
    "http://66.135.27.9:443",
    "http://192.252.220.89:4145",
    "http://91.247.250.215:4145",
    "http://47.82.80.23:1011",
    "http://126.209.110.96:8087",
    "http://103.125.17.106:8080",
    "http://158.101.89.163:3123",
    "http://208.67.28.27:58090",
    "http://144.124.232.204:443",
    "http://171.245.89.241:12328",
    "http://118.179.167.238:55",
    "http://87.106.120.212:3128",
    "http://38.191.194.43:999",
    "http://92.112.125.102:8443",
    "http://115.127.112.178:1080",
    "http://24.249.199.4:4145",
    "http://123.138.24.112:8800",
    "http://89.251.21.45:8080",
    "http://176.12.72.62:3128",
    "http://107.149.141.54:5001",
    "http://5.129.214.191:8080",
    "http://186.227.196.104:3128",
    "http://23.143.160.193:999",
    "http://160.250.54.9:9000",
    "http://145.220.226.102:8080",
    "http://107.173.182.177:30368",
    "http://218.95.39.108:59999",
    "http://38.46.233.245:3127",
    "http://68.1.210.163:4145",
    "http://171.236.89.87:1080",
    "http://47.237.110.50:1080",
    "http://45.174.56.21:999",
    "http://192.3.20.150:3128",
    "http://223.111.182.16:1552",
    "http://103.112.163.131:8080",
    "http://178.252.165.226:1080",
    "http://51.222.13.193:10084",
    "http://98.190.239.3:4145",
    "http://198.98.57.207:1080",
    "http://145.220.226.174:8080",
    "http://168.138.219.12:8081",
    "http://134.249.86.47:8080",
    "http://200.121.48.195:999",
    "http://138.118.107.29:999",
    "http://38.58.117.72:8080",
    "http://72.37.216.68:4145",
    "http://162.214.74.29:8085",
    "http://120.28.169.31:5050",
    "http://145.220.226.54:8080",
    "http://212.3.127.242:10801",
    "http://103.97.141.40:8080",
    "http://43.242.227.10:9053",
    "http://38.190.1.70:1085",
    "http://192.145.228.209:8082",
    "http://180.191.14.210:8081",
    "http://197.248.16.109:8080",
    "http://38.76.196.46:9050",
    "http://106.51.185.233:8080",
    "http://124.105.79.237:8080",
    "http://116.107.186.72:1080",
    "http://98.178.72.30:4145",
    "http://101.255.32.41:8080",
    "http://185.157.111.3:5678",
    "http://39.129.25.66:8060",
    "http://157.254.221.38:20002",
    "http://88.204.134.234:1080",
    "http://66.135.16.53:80",
    "http://37.187.109.70:10111",
    "http://98.170.57.249:4145",
    "http://154.88.189.21:5678",
    "http://190.131.198.77:80",
    "http://94.23.218.74:10808"
]

def get_random_proxy():
    if PROXIES_POOL:
        p = random.choice(PROXIES_POOL)
        return {"http": p, "https": p}
    return None

def process_with_delay(target_url, headers):
    try:
        time.sleep(random.uniform(0.5, 1.5))
        proxy = get_random_proxy()
        browser = random.choice(["chrome110", "chrome120"])
        
        with requests.Session(impersonate=browser, proxies=proxy) as session:
            res = session.get(target_url, headers=headers, timeout=5)
            if res.status_code != 200:
                res = session.post(target_url, json={}, headers=headers, timeout=5)
            if res.status_code == 200:
                return res.json()
    except Exception:
        pass
    return None

def send_3x_help(target_url):
    start_time = time.time()
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://www.midasbuy.com/',
        'Origin': 'https://www.midasbuy.com',
        'Connection': 'keep-alive',
    }

    first_res = None
    account_info = {}
    
    for _ in range(3):
        try:
            proxy = get_random_proxy()
            temp_session = requests.Session(impersonate="chrome120", proxies=proxy)
            res = temp_session.get(target_url, headers=headers, timeout=5)
            if res.status_code != 200:
                res = temp_session.post(target_url, json={}, headers=headers, timeout=5)
                
            if res.status_code == 200:
                data = res.json()
                res_text_lower = res.text.lower()
                if any(word in res_text_lower for word in ['limit', 'complete', 'ended', 'max', 'finish']):
                    return False, "⚠️ عذراً، هذا الرابط مكتمل بالفعل (خلصان 30/30)!"
                
                first_res = data
                break
        except:
            continue

    if not first_res:
        return False, "⚠️ عذراً، رفض الموقع الاتصال وتجاوزت الحماية الحد الأقصى."

    try:
        account_info = first_res.get('data', {})
        if not isinstance(account_info, dict):
            account_info = first_res

        player_name = (account_info.get('roleName') or account_info.get('nickname') or first_res.get('roleName') or "لاعب PUBG")
        player_id = (account_info.get('roleId') or account_info.get('uid') or first_res.get('roleId') or "غير معروف")
        uc_balance = (account_info.get('balance') or account_info.get('uc') or first_res.get('balance') or "0")
    except Exception:
        player_name, player_id, uc_balance = "لاعب PUBG", "غير معروف", "0"

    success_count = 1

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(process_with_delay, target_url, headers) for _ in range(29)]
        for future in futures:
            res_data = future.result()
            if res_data:
                r_code = res_data.get('ret', res_data.get('code', -1))
                if str(r_code) in ["0", "200"] or 'success' in str(res_data).lower():
                    success_count += 1

    elapsed_time = round(time.time() - start_time, 1)

    result_msg = (
        f"تم {success_count}/30 بنجاح 🚀\n"
        f"• الرصيد: {uc_balance} 💰\n"
        f"• الوقت: {elapsed_time} ثانيه ⚙️\n"
        f"• الاسم: {player_name} 🌸\n"
        f"• الـ ID: {player_id} 🆔"
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
        "🔗 1 Link = 30 Invite\n\n"
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

        msg = bot.send_message(chat_id, f"🚀 جارٍ المعالجة بنظام البروكسيات المتعددة...")
        
        success, res = send_3x_help(extracted_url)
        
        if not success:
            bot.edit_message_text(f"⚠️ **تنبيه:**\n\n{res}\n\n🛡️ <b>لم يتم خصم أي رصيد!</b>", chat_id=chat_id, message_id=msg.message_id, parse_mode="HTML")
            return

        if not is_admin(username):
            udata['balance'] -= 1

        bot.edit_message_text(res, chat_id=chat_id, message_id=msg.message_id)
        return
        
    else:
        bot.send_message(chat_id, f"⚡ أهلاً بك يا {user_name}, أرسل رابط ميداسباي لنبدأ التنفيذ مباشرة.")

def run_telegram_bot():
    while True:
        try:
            bot.polling(non_stop=True, interval=1)
        except Exception:
            time.sleep(5)

if __name__ == "__main__":
    keep_alive()
    run_telegram_bot()
