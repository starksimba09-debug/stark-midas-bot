import requests
import json
import telebot

# توكن بوت تليجرام الخاص بـ Stark-midas-bot
TELEGRAM_TOKEN = "8961573070:AAEmTOgrp0tjG6rkeYJqeOqbHEF9uQvWBWg"
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# بيانات Midasbuy المُحدثة
MIDAS_URL = "https://pagedooapi.midasbuy.com/api/CallMpgo/osmidas/dd_help_model/HelpInfoListByUserId"

HEADERS = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "ar-EG",
    "content-type": "application/json",
    "priority": "u=1, i",
    "sec-ch-ua": '"Chromium";v="127", "Not)A;Brand";v="99", "Microsoft Edge Simulate";v="127", "Lemur";v="127"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Linux"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "traceparent": "00-b3ca8871571ce9948db83fb70c1450f3-97bfd81da2c55d11-01",
    "x-request-id": "5lhAd-bY-oxCIviKiFl3l-0",
    "x-tencent-login-check": json.dumps({
        "accountType": "midasbuy",
        "appid": "123123",
        "endpoint_type": "mpgo_activity",
        "offer_id": "1450015065",
        "openid": "62695321247286568",
        "openkey": "nokey",
        "pf": "mds_pc_browser-v2-android-midasweb",
        "session_id": "hy_gameid",
        "session_type": "st_dummy",
        "token": "9ca8360c3d76626452367a14ea5060b786e9cc3a2979e6c04f746c9ae03627b3",
        "userType": "hy_gameid"
    }),
    "Referer": "https://www.midasbuy.com/",
    "Referrer-Policy": "strict-origin-when-cross-origin"
}

PAYLOAD = {
    "mp_activity_id": "Activity_1784618952_EQXYLI",
    "mp_app_id": "1450015065",
    "query_page_num": 1,
    "query_page_size": 10,
    "mp_sub_activity_id": "1784618952184467302LJI",
    "user_id": "62695321247286568",
    "user_id_type": "hy_gameid",
    "meta_data": {
        "ori_zoneid": "1",
        "client_ver": "android",
        "server_id": "1",
        "role_id": "",
        "muid": "U24l1ch1oeyfdr",
        "player_id": "51215330344",
        "pf": "false.",
        "adtag": "event.couponhelper"
    }
}

# أمر البداية في تيليجرام
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "أهلاً بك يا بطل في Stark-midas-bot! البوت جاهز. اكتب /check لفحص حالة الحدث والدعوات أوتوماتيك.")

# أمر فحص الحدث وجلب النتيجة
@bot.message_handler(commands=['check'])
def check_midasbuy(message):
    try:
        bot.reply_to(message, "جاري إرسال الطلب إلى Midasbuy ومعالجة البيانات...")
        response = requests.post(MIDAS_URL, headers=HEADERS, json=PAYLOAD)
        
        if response.status_code == 200:
            data = response.json()
            pretty_result = json.dumps(data, indent=2, ensure_ascii=False)
            if len(pretty_result) > 4000:
                pretty_result = pretty_result[:4000]
            bot.reply_to(message, f"✅ تمت العملية بنجاح:\n\n`{pretty_result}`", parse_mode="Markdown")
        else:
            bot.reply_to(message, f"⚠️ حدث خطأ في الاستجابة، كود الحالة: {response.status_code}\n`{response.text}`", parse_mode="Markdown")
            
    except Exception as e:
        bot.reply_to(message, f"❌ حدث خطأ أثناء الاتصال: {str(e)}")

if __name__ == "__main__":
    print("Stark-midas-bot يعمل الآن بنجاح...")
    bot.infinity_polling()
