import requests
import json

# رابط الـ API الفعلي اللي جبناه من الـ Network
url = "https://pagedooapi.midasbuy.com/api/CallMpgo/osmidas/dd_help_model/HelpInfoListByUserId"

# الـ Headers (تحتاج تضيف الكوكيز أو التوكن الخاص بجلستك عشان السيرفر يقبل الطلب)
headers = {
    "accept": "application/json, text/plain, */*",
    "content-type": "application/json",
    "user-agent": "Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Mobile Safari/537.36",
    # "cookie": "حط الكوكيز بتاعتك هنا لو طلب مصادقة"
}

# الـ Payload (البيانات اللي بعتها الحساب بتاعتك)
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

try:
    # إرسال الطلب نوع POST
    response = requests.post(url, headers=headers, json=payload)
    
    print("Status Code:", response.status_code)
    print("Response Data:")
    print(json.dumps(response.json(), indent=4, ensure_ascii=False))
    
except Exception as e:
    print(f"حدث خطأ: {e}")
