import telebot
from curl_cffi import requests

TOKEN = "8961573070:AAFojTKU_1EBpjxAg-M_gI2V3_t9E0dZ4io"
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    bot.reply_to(message, "🚀 جاري جلب البيانات بجلسة الحساب النشطة...")
    
    try:
        # تجميع الكوكيز الحقيقية من متصفحك
        cookies = (
            "session_token=9ca8360c3d76626452367a14ea5060b786e9cc3a2979e6c04f746c9ae03627b3; "
            "midasbuyDeviceId=0092166902720319581788028726879; "
            "UUID=07666804840699624178804062466468871; "
            "forterToken=af9908bdb7444b4694c34638e4973aa6_1788040690745__UDF43-m4_27ck_; "
            "country=eg; select_country=eg; shopcode=midasbuy"
        )
        
        response = requests.post(
            'https://pagedooapi.midasbuy.com/api/CallMpgo/osmidas/dd_help_model/HelpInfoListByUserId',
            impersonate="chrome120",
            headers={
                'content-type': 'application/json',
                'accept': 'application/json, text/plain, */*',
                'origin': 'https://www.midasbuy.com',
                'referer': 'https://www.midasbuy.com/eg/buy/pubgm?adtag=event.couponhelper',
                'cookie': cookies
            },
            json={
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
            },
            timeout=15
        )
        
        result = response.text
        if not result:
            result = "الاستجابة فارغة."
            
        bot.reply_to(message, f"📌 النتيجة:\n{result[:3500]}")
        
    except Exception as e:
        bot.reply_to(message, f"❌ حدث خطأ:\n{str(e)}")

print("Bot is ready...")
bot.infinity_polling()
