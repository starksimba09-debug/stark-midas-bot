import os
import asyncio
import yt_dlp
from pyrogram import Client, filters
from pyrogram.types import InputMediaPhoto, InputMediaVideo
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
    download_videos=True,  # مسموح بتحميل الفيديوهات لو ظهرت جوه البوستات المختلطة
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
        "• أرسل رابط إنستجرام أو بينترست أو فيسبوك للتحميل 📥"
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

    msg = await message.reply_text("⏳ جاري تجهيز وإرسال المحتوى...")

    try:
        # 3. معالجة منشورات إنستجرام (/p/) - سواء صور فقط أو مكسطة (صور وفيديوهات)
        if "instagram.com" in text and "/p/" in text:
            shortcode = text.split("/p/")[1].split("/")[0].split("?")[0]
            post = instaloader.Post.from_shortcode(L.context, shortcode)
            
            media_items = []
            if post.mediacount > 1:
                for node in post.get_sidecar_nodes():
                    if node.is_video:
                        media_items.append({"type": "video", "url": node.video_url})
                    else:
                        media_items.append({"type": "photo", "url": node.display_url})
                media_items = media_items[::-1]
            else:
                if post.is_video:
                    media_items.append({"type": "video", "url": post.video_url})
                else:
                    media_items.append({"type": "photo", "url": post.url})
            
            if media_items:
                await msg.delete()
                # تقسيم العناصر وإرسالها
                photos_group = []
                for item in media_items:
                    if item["type"] == "photo":
                        photos_group.append(InputMediaPhoto(media=item["url"]))
                        if len(photos_group) == 10:
                            await client.send_media_group(chat_id, media=photos_group)
                            photos_group = []
                    else:
                        # لو فيه صور متراكمة قبل الفيديو، ابعتها الأول
                        if photos_group:
                            await client.send_media_group(chat_id, media=photos_group)
                            photos_group = []
                        # إرسال الفيديو المدمج في البوست مباشرة
                        await client.send_video(chat_id, video=item["url"], supports_streaming=True)
                
                # لو فضل صور أخيرًا متبقية
                if photos_group:
                    await client.send_media_group(chat_id, media=photos_group)
                return

        # 4. الريلز، فيديوهات وبوستات فيسبوك/بينترست (عبر yt-dlp)
        os.makedirs("downloads", exist_ok=True)
        ydl_opts = {
            'cookiefile': 'cookies.txt',
            'outtmpl': 'downloads/%(id)s.%(ext)s',
            'format': 'best',
            'quiet': True,
            'nocheckcertificate': True,
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            res_info = ydl.extract_info(text, download=True)
            if 'entries' in res_info:
                # لو بينتستر أو رابط فيه صور متعددة عبر yt-dlp
                image_urls = [e.get('url') for e in res_info['entries'] if e.get('url')]
                if image_urls:
                    await msg.delete()
                    for i in range(0, len(image_urls), 10):
                        chunk = image_urls[i:i+10]
                        media_group = [InputMediaPhoto(media=u) for u in chunk]
                        await client.send_media_group(chat_id, media=media_group)
                    return
                res_info = res_info['entries'][0]

            filename = ydl.prepare_filename(res_info)
            
        if filename.endswith(('.jpg', '.jpeg', '.png', '.webp')):
            await client.send_photo(chat_id, photo=filename, caption="📥 تم تنزيل الصورة بنجاح!")
        else:
            await client.send_video(chat_id, video=filename, supports_streaming=True)
            
        if os.path.exists(filename):
            os.remove(filename)
        await msg.delete()
        
    except Exception as e:
        await msg.edit_text(f"❌ عذراً، لم يتمكن البوت من تنزيل هذا الرابط:\n`{str(e)}`")

if __name__ == "__main__":
    app.run()
