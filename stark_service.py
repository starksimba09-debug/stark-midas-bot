import telebot
import asyncio
from playwright.async_api import async_playwright

TOKEN = "8961573070:AAFojTKU_1EBpjxAg-M_gI2V3_t9E0dZ4io"
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    bot.reply_to(message, "🚀 جارٍ تشغيل متصفح Playwright لتخطي حماية Midasbuy...")
    
    # تشغيل كود أسمرونك داخل دالة عادية لتوافقية التليجرام
    async def run_browser():
        async with async_playwright() as p:
            # تشغيل متصفح خفي يدعم كل الحمايات الحديثة
            browser = await p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-dev-shm-usage"])
            page = await browser.new_page(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36")
            
            # الدخول للموقع لتوليد الكوكيز والبصمة الحقيقية
            await page.goto("https://www.midasbuy.com/", timeout=60000)
            await asyncio.sleep(3)
            
            # تنفيذ الـ fetch من جوه المتصفح الحقيقي
            response_text = await page.evaluate("""async () => {
                const res = await fetch('https://pagedooapi.midasbuy.com/api/CallMpgo/osmidas/dd_help_model/HelpInfoListByUserId', {
                    method: 'POST',
                    headers: {
                        'content-type': 'application/json',
                        'accept': 'application/json, text/plain, */*'
                    },
                    body: JSON.stringify({
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
                    })
                });
                return await res.text();
            }""")
            
            await browser.close()
            return response_text

    try:
        # تنفيذ الدالة غير المتزامنة
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(run_browser())
        
        if result:
            bot.reply_to(message, f"✅ النتيجة بنجاح:\n{result[:900]}")
        else:
            bot.reply_to(message, "❌ الاستجابة فارغة.")
            
    except Exception as e:
        bot.reply_to(message, f"❌ حدث خطأ في Playwright:\n{str(e)}")

print("Playwright Bot is running...")
bot.infinity_polling()
