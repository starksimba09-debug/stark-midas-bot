import telebot
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# توكن البوت الخاص بك
TOKEN = "8961573070:AAEmTOgrp0tjG6rkeYJqeOqbHEF9uQvWBWg"
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['check'])
def check_midas(message):
    bot.reply_to(message, "جاري تشغيل المتصفح الخفي لتخطى الحماية وسحب البيانات...")
    
    driver = None
    try:
        # إعدادات المتصفح الخفي (Headless Chrome) ليعمل بكفاءة على السيرفر
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36")

        # تشغيل المتصفح
        driver = webdriver.Chrome(options=chrome_options)
        
        # الخطوة 1: الدخول لموقع Midasbuy الأساسي لتوليد بصمة المتصفح والكوكيز الحقيقية
        driver.get("https://www.midasbuy.com/")
        time.sleep(3)
        
        # الخطوة 2: إرسال طلب الـ API من داخل جلسة المتصفح الحية لتجاوز حماية الـ 567
        script = """
        return fetch('https://pagedooapi.midasbuy.com/api/CallMpgo/osmidas/dd_help_model/HelpInfoListByUserId', {
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
        }).then(response => response.text());
        """
        
        response_text = driver.execute_script(script)
        
        if response_text:
            bot.reply_to(message, f"تم بنجاح! النتيجة:\n{response_text[:800]}")
        else:
            bot.reply_to(message, "فشل جلب الاستجابة من المتصفح.")

    except Exception as e:
        bot.reply_to(message, f"حدث خطأ أثناء التشغيل: {str(e)}")
        
    finally:
        if driver:
            driver.quit()

print("Bot with Selenium is running...")
bot.infinity_polling()
