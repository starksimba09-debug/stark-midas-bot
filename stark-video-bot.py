import os
import yt_dlp
from pyrogram import Client, filters
from pyrogram.types import InputMediaPhoto
import requests
from bs4 import BeautifulSoup

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
        "👋 أهلاً بك في بوت التحميل المباشر!\n\n"
        "• أرسل لي **اسم أي شخصية** وسأرسل لك صورها مباشرة 🖼️\n"
        "• أرسل لي **رابط إنستجرام (ريلز أو صور)** وسأقوم بإرساله فوراً 📥"
    )

@app.on_message(filters.text & ~filters.command("start"))
async def handle_incoming_text(client, message):
    text = message.text.strip()
    chat_id = message.chat.id
    
    # 1. البحث عن الصور بالأسماء
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
        
        await msg.edit_text("❌ لم يتم العثور على صور، جرب كلمة أخرى.")
        return

    # 2. منع يوتيوب نهائياً
    if "youtube.com" in text or "youtu.be" in text:
        await message.reply_text("❌ تم إلغاء دعم يوتيوب، أرسل روابط إنستجرام أو فيسبوك فقط.")
        return

    # 3. معالجة روابط إنستجرام (لو منشور صور /p/ سحبه كصورة، لو ريلز كفيديو)
    msg = await message.reply_text("⏳ جاري المعالجة والإرسال...")
    
    try:
        if "instagram.com" in text and ("/p/" in text or "/tv/" in text):
            # سحب الصورة مباشرة من meta tags الخاصة بالمنشور
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
            r = requests.get(text, headers=headers, timeout=10)
            soup = BeautifulSoup(r.text, 'html.parser')
            img_tag = soup.find("meta", property="og:image")
            
            if img_tag and img_tag.get("content"):
                await client.send_photo(chat_id, photo=img_tag["content"], caption="📥 تم إرسال الصورة بنجاح!")
                await msg.delete()
                return

        # 4. لو فيديو (ريلز إنستجرام أو فيسبوك) يتم تحميله بـ yt-dlp
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
        await msg.edit_text(f"❌ عذراً، لم أتمكن من معالجة هذا الرابط:\n`{str(e)}`")

if __name__ == "__main__":
    app.run()
