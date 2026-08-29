import requests
import json

url = 'https://pagedooapi.midasbuy.com/api/CallMpgo/osmidas/dd_help_model/HelpInfoListByUserId'

headers = {
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'ar-EG',
    'content-type': 'application/json',
    'cookie': '_gcl_au=1.1.786793852.1788028844; _gid=GA1.2.1911735912.1788028844; _ga_NQX2JD8STG=GS2.1.s1788034469$o2$g1$t1788036263$j48$l0$h0; _ga=GA1.2.1582460889.1788028844; forterToken=af9908bdb7444b4694c34638e4973aa6_1788036265042__UDF43-m4_27ck_',
    'origin': 'https://www.midasbuy.com',
    'priority': 'u=1, i',
    'referer': 'https://www.midasbuy.com/',
    'sec-ch-ua': '"Chromium";v="127", "Not)A;Brand";v="99", "Microsoft Edge Simulate";v="127", "Lemur";v="127"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Linux"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'traceparent': '00-078597c3c1f9e5a8add820a92b6cc1ed-6a3831693239849f-01',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
    'x-request-id': 'omWsoKToiRDiqsGOdOTlI-0',
    'x-tencent-login-check': '{"accountType":"midasbuy","appid":"123123","endpoint_type":"mpgo_activity","offer_id":"1450015065","openid":"62695321247286568","openkey":"nokey","pf":"mds_pc_browser-v2-android-midasweb","session_id":"hy_gameid","session_type":"st_dummy","token":"9ca8360c3d76626452367a14ea5060b786e9cc3a2979e6c04f746c9ae03627b3","userType":"hy_gameid"}'
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

print("جاري إرسال الطلب بالبصمة الفريش...")
response = requests.post(url, headers=headers, json=data)

print("Response Code:", response.status_code)
print("Response Text:", response.text[:1000])
