import telebot
import asyncio
from playwright.async_api import async_playwright
from curl_cffi import requests

TOKEN = "8961573070:AAFojTKU_1EBpjxAg-M_gI2V3_t9E0dZ4io"
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    bot.reply_to(message, "🚀 جاري استخراج جلسة الحساب عبر المتصفح...")
    
    async def get_cookies_and_fetch():
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True, 
                args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-setuid-sandbox"]
            )
            
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
                viewport={"width": 390, "height": 844}
            )
            
            page = await context.new_page()
            
            # الدخول لصفحة الموقع الحقيقية لإنشاء الجلسة
            await page.goto("https://www.midasbuy.com/eg/buy/pubgm?adtag=event.couponhelper", timeout=60000)
            await asyncio.sleep(4)
            
            # سحب كل الكوكيز النشطة من المتصفح الوهمي
            cookies_list = await context.cookies()
            cookies_str = "; ".join([f"{c['name']}={c['value']}" for c in cookies_list])
            
            await browser.close()
            return cookies_str

    try:
        # تشغيل بلاي شيرت لجلب الكوكيز الحية
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        live_cookies = loop.run_until_complete(get_cookies_and_fetch())
        
        # إرسال الطلب عبر curl_cffi باستخدام الكوكيز الطازجة المستخرجة
        response = requests.post(
            'https://pagedooapi.midasbuy.com/api/CallMpgo/osmidas/dd_help_model/HelpInfoListByUserId',
            impersonate="chrome120",
            headers={
                'content-type': 'application/json',
                'accept': 'application/json, text/plain, */*',
                'origin': 'https://www.midasbuy.com',
                'referer': 'https://www.midasbuy.com/eg/buy/pubgm?adtag=event.couponhelper',
                'cookie': live_cookies
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
