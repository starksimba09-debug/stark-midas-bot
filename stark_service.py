import os
import time
import requests
from flask import Flask
from threading import Thread

# إعداد سيرفر الويب الخفي لضمان بقاء البوت شغال 24/7 على Render
app = Flask('')

@app.route('/')
def home():
    return "Stark Midas Bot is active and running 24/7!"

def run():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    server_thread = Thread(target=run)
    server_thread.daemon = True
    server_thread.start()

# دالة التشغيل الرئيسية للبوت
def main():
    print("Stark Midas Bot Service Started Successfully.")
    
    # حلقة تكرارية لضمان استمرار عمل الخدمة وتجنب التوقف
    while True:
        try:
            # مكان مهام البوت الأساسية أو الأوامر مستقبلاً
            pass
        except Exception as e:
            print(f"Error occurred: {e}")
            
        time.sleep(30)

if __name__ == "__main__":
    # تشغيل السيرفر الخفي أولاً
    keep_alive()
    # تشغيل مهام البوت
    main()
