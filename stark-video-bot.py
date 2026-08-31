import os
import requests
from bs4 import BeautifulSoup
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
        "• أرسل لي **اسم أي شخصية** وسأبحث لك عن صورها 🖼️\n"
        "• أرسل لي **رابط (انستجرام، فيسبوك، بينتريست، يوتيوب)** وسأقوم بتحميله 📥\n"
        "• أو أرسل **اسم أغنية** لتحميلها صوت أو فيديو 🎶"
    )

@app.on_message(filters.text & ~filters.command("start"))
async def handle_incoming_text(client, message):
    text = message.text.strip()
    chat_id = message.chat.id
    
    # محاولة سحب الصورة المباشرة لأي رابط
    if any(domain in text for domain in ["pin.it", "pinterest.com", "instagram.com", "facebook.com", "fb.watch"]):
        msg = await message.reply_text("⏳ جاري فحص الرابط واستخراج المحتوى...")
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
            r = requests.get(text, headers=headers, allow_redirects=True, timeout=8)
            soup = BeautifulSoup(r.text, 'html.parser')
            
            img_tag = soup.find("meta", property="og:image")
            if img_tag and img_tag.get("content"):
                img_url = img_tag["content"]
                # التأكد إن الرابط حقيقي ومش مجرد صورة بروفایل عامة
                if "http" in img_url:
                    await client.send_photo(chat_id, photo=img_url, caption="📥 تم جلب الصورة بنجاح!")
                    await msg.delete()
                    return
        except Exception:
            pass

        # لو رابط انستجرام وطلع بوست صور (مش ريلز/فيديو)، نبلغ المستخدم بذوق بدل إيرور yt-dlp المرعب
        if "instagram.com" in text and ("/p/" in text or "/tv/" in text):
            await msg.edit_text("⚠️ هذا الرابط عبارة عن **منشور صور** من انستجرام. إنستجرام يحظر تحميل صور المنشورات الثابتة بروابط مباشرة حالياً. يجدر الإرسال لو كان (Reels/فيديو) أو اسم شخصية للبحث عنه!")
            return

    # البحث عن الشخصيات أو الأسماء
    if not text.startswith("http"):
        msg = await message.reply_text(f"🔍 جاري البحث عن صور لـ ({text})...")
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
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
            query = f"ytsearch1:{text} 4K wallpaper"
        except:
            query = f"ytsearch1:{text} HD"
    else:
        query = text

    user_queries[chat_id] = query
    msg = await message.reply_text("🔍 جاري التحضير للتحميل...")
    
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
        await msg.edit_text("❌ عذراً، هذا الرابط إما أنه صورة فقط أو غير مدعوم للفيديوهات حالياً.")

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
        await callback_query.message.edit_text(f"❌ خطأ أثناء التحميل: تأكد من صحة الرابط.")

if __name__ == "__main__":
    app.run()
