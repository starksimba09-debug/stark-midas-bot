import os
import requests
from telegram import Update
from telegram.ext import ContextTypes

async def download_and_send_movie(update: Update, context: ContextTypes.DEFAULT_TYPE):
    movie_url = "رابط_الفيلم_المباشر"
    file_name = "movie.mp4"
    
    # 1. تحميل الفيلم مؤقتاً
    response = requests.get(movie_url, stream=True)
    with open(file_name, "wb") as f:
        for chunk in response.iter_content(chunk_size=1024 * 1024): # تحميل بقطع حجمها 1 ميجا
            if chunk:
                f.write(chunk)
                
    # 2. إرسال الفيلم لتيليجرام
    with open(file_name, "rb") as movie_file:
        await update.message.reply_video(video=movie_file)
        
    # 3. مسح الملف من سيرفر البوت لتوفير المساحة
    os.remove(file_name)
