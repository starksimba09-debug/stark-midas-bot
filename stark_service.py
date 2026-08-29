import telebot
import requests
import urllib3

# إيقاف تحذيرات الاتصال الآمن عشان ريلواي مايعلقش الطلب
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TOKEN = "8961573070:AAFojTKU_1EBpjxAg-M_gI2V3_t9E0dZ4io"
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    bot.reply_to(message, "🚀 جارٍ إرسال الطلب بالوضع السريع...")
    
    url = 'https://pagedooapi.midasbuy.com/api/CallMpgo/osmidas/dd_help_model/HelpInfoListByUserId'
    
    # هيدرز خفيفة ومحاكية لمتصفح موبايل حقيقي بيعدي من الحماية
    headers = {
        'Host': 'pagedooapi.midasbuy.com',
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'ar-EG,ar;q=0.9,en-US;q=0.8,en;q=0.7',
        'content-type': 'application/json',
        'origin': 'https://www.midasbuy.com',
        'referer': 'https://www.midasbuy.com/',
        'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Mobile Safari/537.36',
        'x-requested-with': 'XMLHttpRequest'
    }
    
    data = {
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
    
    try:
        # إرسال الطلب مع تجاهل التحقق العقيم لـ SSL وتحديد وقت انتظار (Timeout)
        response = requests.post(url, headers=headers, json=data, verify=False, timeout=15)
        
        result_text = f"Status Code: {response.status_code}\n\nResponse:\n{response.text[:900]}"
        bot.reply_to(message, result_text)
        
    except Exception as e:
        bot.reply_to(message, f"❌ حدث خطأ شبكة: {str(e)}")

print("Fast Bot is running...")
bot.infinity_polling()
