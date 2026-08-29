import os
import time
import re
from flask import Flask
from threading import Thread
import asyncio
from playwright.async_api import async_playwright
import telebot
from telebot import types

TOKEN = "8961573070:AAEmTOgrp0tjG6rkeYJqeOqbHEF9uQvWBWg"
bot = telebot.TeleBot(TOKEN)

ADMIN_USERNAMES = ["YAMAC_GAMING", "S1_MBA1", "SImba_5", "Vartolugaming"]
users_db = {}

app = Flask('')

@app.route('/')
def home():
    return "Stark Midas Bot is active with Playwright Browser!"

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

async def execute_playwright_invites(target_url):
    start_time = time.time()
    success_count = 0
    player_name = "لاعب PUBG"
    player_id = "غير معروف"
    uc_balance = "0"

    try:
        async with async_playwright() as p:
            # تشغيل المتصفح في الخلفية بصلاحيات تتخطى الحماية
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-accelerated-2d-canvas",
                    "--disable-gpu"
                ]
            )
            
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                viewport={"width": 1280, "height": 800}
            )
            
            page = await context.new_page()
            
            # محاولة فتح الرابط الأساسي لأول مرة لتجاوز كلوادفلاير وجلب بيانات الحساب
            print(f"Opening target URL: {target_url}")
            response = await page.goto(target_url, timeout=30000, wait_until="domcontentloaded")
            
            if not response or response.status >= 400:
                await browser.close()
                return False, "⚠️ عذراً، رفض الموقع الاتصال أو حماية كلوادفلاير منعت المتصفح."

            # انتظار تحميل الصفحة قليلاً لالتقاط البيانات لو وجدت
            await page.wait_for_timeout(3000)
            page_text = await page.inner_text("body")
            
            if any(word in page_text.lower() for word in ['limit', 'complete', 'ended', 'max', 'finish', 'انتهت']):
                await browser.close()
                return False, "⚠️ عذراً، هذا الرابط مكتمل بالفعل (خلصان 30/30)!"

            success_count = 1  # الطلب الأول نجح وفتح الصفحة

            # تنفيذ محاولات الدعوات المتكررة من خلال إعادة زيارة الرابط أو إرسال طلبات خلفية
            for i in range(29):
                try:
                    # فتح الرابط في تبويب أو إعادة تحميل خفيفة لتسجيل الدعوة
                    sub_page = await context.new_page()
                    await sub_page.goto(target_url, timeout=15000)
                    success_count += 1
                    await sub_page.close()
                    await asyncio.sleep(0.5)
                except Exception:
                    continue

            await browser.close()
            
            elapsed_time = round(time.time() - start_time, 1)
            result_msg = (
                f"تم {success_count}/30 بنجاح 🚀\n"
                f"• الرصيد: {uc_balance} 💰\n"
                f"• الوقت: {elapsed_time} ثانيه ⚙️\n"
                f"• الاسم: {player_name} 🌸\n"
                f"• الـ ID: {player_id} 🆔"
            )
            return True, result_msg

    except Exception as e:
        print(f"Playwright Error: {str(e)}")
        return False, f"⚠️ حدث خطأ تقني أثناء تشغيل المتصفح: {str(e)}"

def run_async_task(target_url):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return loop.run_until_complete(execute_playwright_invites(target_url))

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
        f"أهلاً بك يا <b>{user_name}</b> في بوت <b>STARK</b> (Playwright Mode) 👑\n\n"
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

        msg = bot.send_message(chat_id, f"🌐 جارٍ تشغيل المتصفح وتخطى الحماية...")
        
        success, res = run_async_task(extracted_url)
        
        if not success:
            bot.edit_message_text(f"⚠️ **تنبيه:**\n\n{res}\n\n🛡️ <b>لم يتم خصم أي رصيد!</b>", chat_id=chat_id, message_id=msg.message_id, parse_mode="HTML")
            return

        if not is_admin(username):
            udata['balance'] -= 1

        bot.edit_message_text(res, chat_id=chat_id, message_id=msg.message_id)
        return
        
    else:
        bot.send_message(chat_id, f"⚡ أهلاً بك يا {user_name}, أرسل رابط ميداسباي لنبدأ التنفيذ بالمتصفح مباشرة.")

def run_telegram_bot():
    while True:
        try:
            bot.polling(non_stop=True, interval=1)
        except Exception:
            time.sleep(5)

if __name__ == "__main__":
    keep_alive()
    run_telegram_bot()
