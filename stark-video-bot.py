import os
import yt_dlp
from pyrogram import Client, filters
from pyrogram.types import InputMediaPhoto
import requests

API_ID = 37361961
API_HASH = "36eca100c1861a8dc32ccec4fd284c24"
BOT_TOKEN = "8528693331:AAHhUHbnOKVgrEpAl5mbGLUft9Wzzlw3sVE"

app = Client(
    "stark_video_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

@app.on_message(filters.command("start"))
async def start_command(client, message):
    await message.reply_text(
        "👋 أهلاً بك في البوت المحدث!\n\n"
        "• أرسل اسم أي شخصية لجلب صورها 🖼️\n"
        "• أرسل رابط إنستجرام أو فيسبوك للتحميل المباشر 📥"
    )

@app.on_message(filters.text & ~filters.command("start"))
async def handle_incoming_text(client, message):
    text = message.text.strip()
    chat_id = message.chat.id
    
    # 1. البحث العشوائي عن الصور بالأسماء
    if not text.startswith("http"):
        msg = await message.reply_text(f"🔍 جاري جلب الصور لـ ({text})...")
        try:
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            api_url = f"https://duckduckgo.com/i.js?q={text}+HD&o=json&p=1"
            res = requests.get(api_url, headers=headers, timeout=10).json()
            results = res.get("results", [])
            
            if results:
                media_group = []
                for item in results[:4]:
                    img_url = item.get("image")
                    if img_url:
                        media_group.append(InputMediaPhoto(media=img_url))
                
                if media_group:
                    await client.send_media_group(chat_id, media=media_group)
                    await msg.delete()
                    return
        except Exception:
            pass
        
        await msg.edit_text("❌ لم يتم العثور على صور.")
        return

    # 2. منع يوتيوب نهائياً
    if "youtube.com" in text or "youtu.be" in text:
        await message.reply_text("❌ تم إلغاء دعم يوتيوب بناءً على رغبتك.")
        return

    msg = await message.reply_text("⏳ جاري المعالجة...")

    try:
        # 3. لو رابط إنستجرام صور (/p/) نستخدم API خارجي نظيف يجيب الصور مباشرة بدون أخطاء yt-dlp
        if "instagram.com" in text and "/p/" in text:
            api_json_url = f"https://apis.davidcyriltech.workers.dev/instagram?url={text}"
            r = requests.get(api_json_url, timeout=15).json()
            
            if r.get("success") and r.get("medias"):
                media_list = r["medias"]
                # لو صورة واحدة أو كذا صورة
                media_group = []
                for m in media_list[:4]: # أقصى حد 4 صور معاً
                    media_url = m.get("url")
                    if media_url:
                        media_group.append(InputMediaPhoto(media=media_url))
                
                if media_group:
                    await client.send_media_group(chat_id, media=media_group)
                    await msg.delete()
                    return

        # 4. لو ريلز إنستجرام أو فيسبوك (فيديو) -> يروح لـ yt-dlp بأمان تام
        os.makedirs("downloads", exist_ok=True)
        ydl_opts = {
            'cookiefile': 'cookies.txt',
            'outtmpl': 'downloads/%(id)s.%(ext)s',
            'format': 'best',
            'quiet': True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            res_info = ydl.extract_info(text, download=True)
            if 'entries' in res_info:
                res_info = res_info['entries'][0]
            filename = ydl.prepare_filename(res_info)
            
        await client.send_video(chat_id, video=filename, supports_streaming=True)
            
        if os.path.exists(filename):
            os.remove(filename)
        await msg.delete()
        
    except Exception as e:
        await msg.edit_text(f"❌ عذراً، حدث خطأ في معالجة الرابط:\n`{str(e)}`")

if __name__ == "__main__":
    app.run()
