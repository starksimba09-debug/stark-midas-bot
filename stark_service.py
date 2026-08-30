import os
import requests
import json
import time

TOKEN = "8961573070:AAFojTKU_1EBpjxAg-M_gI2V3_t9E0dZ4io"
URL_API = "https://pagedooapi.midasbuy.com/api/CallMpgo/osmidas/dd_help_model/HelpInfoListByUserId"

headers = {
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'ar-EG',
    'content-type': 'application/json',
    'cookie': '_gcl_au=1.1.786793852.1788028844; _gid=GA1.2.1911735912.1788028844; forterToken=af9908db7444b4694c34638e4973aa6_1788053200887__UDF43-m4_27ck_; _gat_UA-21773189-2=1; _ga=GA1.2.1582460889.1788028844; _ga_NQX2JD8STG=GS2.1.s1788053196$o4$g1$t1788056195$j45$l0$h0',
    'origin': 'https://www.midasbuy.com',
    'referer': 'https://www.midasbuy.com/',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
    'x-request-id': 'qQ9MlilnjNw-zj1YjS6OJ-0',
    'x-tencent-login-check': '{"accountType":"midasbuy","appid":"123123","endpoint_type":"mpgo_activity","offer_id":"1450015065","openid":"62695321247286568","openkey":"nokey","pf":"mds_pc_browser-v2-android-midasweb","session_id":"hy_gameid","session_type":"st_dummy","token":"43416bf502ba607a1f677e7002dc66efbc8f0f68ffc9afb2ba09bdd5edafa221","userType":"hy_gameid"}'
}

payload = {
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
        "adtag": "popup.topup"
    }
}

def send_telegram_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": text})

def check_midasbuy():
    try:
        response = requests.post(URL_API, headers=headers, json=payload, timeout=10)
        if response.headers.get('content-type', '').startswith('application/json'):
            res_json = response.json()
            if res_json.get("result_code") == "0":
                list_data = res_json.get("data", {}).get("mp_help_list", [{}])[0]
                now_people = list_data.get("mp_help_now_people", 0)
                max_people = list_data.get("mp_help_count_max", 60)
                return f"✅ حالة الحدث الحالية:\n- عدد المساعدات: {now_people} / {max_people}"
            else:
                return f"⚠️ خطأ من السيرفر: {res_json.get('result_info', 'Unknown')}"
        else:
            return "❌ السيرفر رد بصفحة حماية (Cloudflare/EdgeOne Block)."
    except Exception as e:
        return f"❌ حدث خطأ في الاتصال: {e}"

def main():
    offset = 0
    print("🤖 البوت شغال الآن وجاهز للاستجابة...")
    while True:
        try:
            url = f"https://api.telegram.org/bot{TOKEN}/getUpdates?offset={offset}&timeout=30"
            resp = requests.get(url, timeout=35).json()
            
            if "result" in resp:
                for update in resp["result"]:
                    offset = update["update_id"] + 1
                    message = update.get("message", {})
                    chat_id = message.get("chat", {}).get("id")
                    
                    if chat_id:
                        reply_text = check_midasbuy()
                        send_telegram_message(chat_id, reply_text)
        except Exception as e:
            print(f"خطأ: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
