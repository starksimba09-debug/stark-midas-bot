import requests
import json

url = 'https://pagedooapi.midasbuy.com/api/CallMpgo/osmidas/dd_help_model/HelpInfoListByUserId'

headers = {
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'ar-EG',
    'content-type': 'application/json',
    'cookie': '_gcl_au=1.1.786793852.1788028844; _gid=GA1.2.1911735912.1788028844; forterToken=af9908db7444b4694c34638e4973aa6_1788053200887__UDF43-m4_27ck_; _ga=GA1.2.1582460889.1788028844; _ga_NQX2JD8STG=GS2.1.s1788053196$o4$g1$t1788055130$j48$l0$h0',
    'origin': 'https://www.midasbuy.com',
    'priority': 'u=1, i',
    'referer': 'https://www.midasbuy.com/',
    'sec-ch-ua': '"Chromium";v="127", "Not)A;Brand";v="99", "Microsoft Edge Simulate";v="127", "Lemur";v="127"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Linux"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'traceparent': '00-1cf30428ab624063c5d4c0e2accdd7ca-2f64bcb7115dea31-01',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
    'x-request-id': 'jLsYUUgmp_JN-skMyZB8Z-7',
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

try:
    response = requests.post(url, headers=headers, json=payload)
    print("Status Code:", response.status_code)
    print("Raw Response Text:", response.text)
    
    if response.text.strip():
        try:
            print("Response JSON:", response.json())
        except json.JSONDecodeError:
            print("الرد ليس بصيغة JSON صالح (ربما صفحة حماية أو خطأ HTML).")
    else:
        print("الرد فارغ تماماً من السيرفر.")
        
except Exception as e:
    print(f"حدث خطأ أثناء المعالجة: {e}")
