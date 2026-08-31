import os
import requests
import yt_dlp
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto

API_ID = 37361961
API_HASH = "36eca100c1861a8dc32ccec4fd284c24"
BOT_TOKEN = "8528693331:AAHhUHbnOKVgrEpAl5mbGLUft9Wzzlw3sVE"

app = Client(
    "stark_video_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

user_queries = {}

@app.on_message(filters.command("start"))
async def start_command(client, message):
    await message.reply_text(
        "👋 أهلاً بك في بوت التحميل (Stark Video Bot)!\n\n"
        "• أرسل لي **اسم أي شخصية** وسأبحث لك عن صور عالية الجودة لها 🖼️\n"
        "• أرسل لي **رابط بينتريست (Pinterest) أو إنستجرام أو يوتيوب** وسأقوم بتحميله 📥\n"
        "• أو أرسل **اسم أغنية** لتحميلها صوت أو فيديو 🎶"
    )

@app.on_message(filters.text & ~filters.command("start"))
async def handle_incoming_text(client, message):
    text = message.text.strip()
    chat_id = message.chat.id
    
    # 1. معالجة روابط بينتريست مباشرة
    if "pin.it" in text or "pinterest.com" in text:
        msg = await message.reply_text("⏳ جاري استخراج الصورة من بينتريست...")
        try:
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
            # تتبع الرابط المختصر لو كان pin.it
            r = requests.get(text, headers=headers, allow_redirects=True)
            real_url = r.url
            
            # استخراج الصورة باستخدام yt-dlp بشكل صحيح كموقع صور أو استخراج رابط الـ og:image
            ydl_opts = {'cookiefile': 'cookies.txt', 'quiet': True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(real_url, download=False)
                img_url = info.get('thumbnail') or info.get('url')
                
            if img_url:
                await client.send_photo(chat_id, photo=img_url, caption="📌 صورة من Pinterest")
                await msg.delete()
                return
            else:
                raise Exception("لم يتم العثور على رابط الصورة.")
        except Exception as e:
            await msg.edit_text(f"❌ عذراً، فشل تحميل رابط Pinterest:\n`{str(e)}`")
            return

    # 2. البحث عن شخصية أو اسم لجلب صور عالية الجودة عبر DuckDuckGo Images
    if not text.startswith("http"):
        msg = await message.reply_text(f"🔍 جاري البحث عن صور لـ ({text})...")
        try:
            # استخدام بحث صور DuckDuckGo لجلب صور حقيقية عالية الجودة وليست مجرد مصغرات فيديو
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            # الخطوة الأولى: جلب رمز البحث vqd الخاص بـ DuckDuckGo
            url = f"https://html.duckduckgo.com/html/?q={text}+HD+images"
            res = requests.get(url, headers=headers)
            
            # طريقة أسرع وأضمن عبر استخراج الصور المباشرة من الـ API العام لـ DuckDuckGo
            api_url = f"https://duckduckgo.com/i.js?q={text}&o=json&p=1"
            response = requests.get(api_url, headers=headers).json()
            results = response.get("results", [])
            
            if results:
                # نأخذ أول 4 صور حقيقية عالية الجودة ونرسلها كألبوم
                media_group = []
                for item in results[:4]:
                    img_url = item.get("image")
                    if img_url:
                        media_group.append(InputMediaPhoto(media=img_url))
                
                if media_group:
                    await client.send_media_group(chat_id, media=media_group)
                    await msg.delete()
                    return
            
            # لو لم تنجح الطريقة، نبحث عبر yt-dlp كبديل
            query = f"ytsearch1:{text} 4K wallpaper"
        except:
            query = f"ytsearch1:{text} HD"
    else:
        query = text

    user_queries[chat_id] = query
    if not text.startswith("http"):
        return # لو تم إرسال الصور بالفعل نتخطى الباقي
        
    msg = await message.reply_text("🔍 جاري التحضير...")
    
    try:
        ydl_opts = {'cookiefile': 'cookies.txt', 'quiet': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(query, download=False)
            if 'entries' in info:
                info = info['entries'][0]
            title = info.get('title', 'Media')
            
        keyboard = [
            [InlineKeyboardButton("🎵 تحميل صوت (MP3)", callback_data="dl_audio")],
            [InlineKeyboardButton("🎬 تحميل فيديو (MP4)", callback_data="dl_video")]
        ]
        
        await msg.edit_text(
            f"🎵 **تم العثور على النتيجة:**\n`{title}`\n\nاختر صيغة التحميل المطلوبة:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    except Exception as e:
        await msg.edit_text(f"❌ حدث خطأ:\n`{str(e)}`")

@app.on_callback_query()
async def download_callback(client, callback_query):
    data = callback_query.data
    chat_id = callback_query.message.chat.id
    query = user_queries.get(chat_id)
    
    if not query:
        await callback_query.message.edit_text("❌ انتهت صلاحية الجلسة.")
        return

    await callback_query.message.edit_text("⏳ جاري التحميل...")
    
    try:
        os.makedirs("downloads", exist_ok=True)
        ydl_opts = {
            'cookiefile': 'cookies.txt',
            'outtmpl': 'downloads/%(title)s.%(ext)s',
            'format': 'bestaudio/best' if data == "dl_audio" else 'best[height<=720]/best'
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            res_info = ydl.extract_info(query, download=True)
            if 'entries' in res_info:
                res_info = res_info['entries'][0]
            filename = ydl.prepare_filename(res_info)
            
        await callback_query.message.edit_text("📤 جاري الإرسال...")
        
        if data == "dl_audio":
            await client.send_audio(chat_id, audio=filename)
        else:
            await client.send_video(chat_id, video=filename)
            
        os.remove(filename)
        await callback_query.message.delete()
    except Exception as e:
        await callback_query.message.edit_text(f"❌ خطأ أثناء التحميل: {str(e)}")

if __name__ == "__main__":
    app.run()
