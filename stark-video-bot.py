import os
import yt_dlp
from pyrogram import Client, filters
from pyrogram.types import InputMediaPhoto
import requests
import instaloader

API_ID = 37361961
API_HASH = "36eca100c1861a8dc32ccec4fd284c24"
BOT_TOKEN = "8528693331:AAHhUHbnOKVgrEpAl5mbGLUft9Wzzlw3sVE"

app = Client(
    "stark_video_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

L = instaloader.Instaloader(
    download_videos=False,
    download_video_thumbnails=False,
    download_geotags=False,
    download_comments=False,
    save_metadata=False
)

@app.on_message(filters.command("start"))
async def start_command(client, message):
    await message.reply_text(
        "👋 أهلاً بك في البوت!\n\n"
        "• أرسل اسم أي شخصية لجلب صورها 🖼️\n"
        "• أرسل رابط إنستجرام (حتى لو فيه 20 صورة) أو ريلز للتحميل 📥"
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
        
        await msg.edit_text("❌ لم يتم العثور على صور.")
        return

    # 2. منع يوتيوب نهائياً
    if "youtube.com" in text or "youtu.be" in text:
        await message.reply_text("❌ تم إلغاء دعم يوتيوب.")
        return

    msg = await message.reply_text("⏳ جاري سحب وتحميل الصور (قد يستغرق لحظات لو البوست كبير)...")

    try:
        # 3. معالجة منشورات الصور في إنستجرام (/p/) ودعم أكثر من 10 صور بتسريحها على دفعات
        if "instagram.com" in text and ("/p/" in text or "/tv/" in text):
            shortcode = text.split("/p/")[-1].split("/tv/")[-1].split("/")[0].split("?")[0]
            post = instaloader.Post.from_shortcode(L.context, shortcode)
            
            all_urls = []
            if post.mediacount > 1:
                for node in post.get_sidecar_nodes():
                    if not node.is_video:
                        all_urls.append(node.display_url)
            else:
                if post.url:
                    all_urls.append(post.url)
            
            if all_urls:
                await msg.delete()
                # تقسيم الصور على دفعات كل دفعة 10 صور (لأن تيليجرام مش بيقبل أكتر من 10 في المرة)
                for i in range(0, len(all_urls), 10):
                    chunk = all_urls[i:i+10]
                    media_group = [InputMediaPhoto(media=url) for url in chunk]
                    await client.send_media_group(chat_id, media=media_group)
                return

        # 4. الريلز والفيديوهات
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
        await msg.edit_text(f"❌ عذراً، لم يتمكن البوت من تنزيل هذا الرابط:\n`{str(e)}`")

if __name__ == "__main__":
    app.run()
