import os
import yt_dlp
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

API_ID = 37361961
API_HASH = "36eca100c1861a8dc32ccec4fd284c24"
BOT_TOKEN = "8528693331:AAHhUHbnOKVgrEpAl5mbGLUft9Wzzlw3sVE"

app = Client(
    "stark_video_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

user_urls = {}

# الرد على أمر start
@app.on_message(filters.command("start"))
async def start_command(client, message):
    await message.reply_text(
        "👋 أهلاً بك في بوت التحميل (Stark Video Bot)!\n\n"
        "أرسل لي الآن أي رابط فيديو أو صورة من **إنستجرام** أو **فيسبوك** وسأقوم بتحميله لك فوراً 🚀"
    )

def get_media_info(url):
    ydl_opts = {
        'cookiefile': 'cookies.txt',
        'quiet': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        return info

@app.on_message(filters.text & ~filters.command(["start"]))
async def handle_incoming_link(client, message):
    url = message.text
    if not url.startswith("http"):
        return
        
    chat_id = message.chat.id
    user_urls[chat_id] = url
    
    platform = "منصة أخرى"
    if "instagram.com" in url:
        platform = "إنستجرام 📸"
    elif "facebook.com" in url or "fb.watch" in url:
        platform = "فيسبوك 📘"
        
    msg = await message.reply_text(f"🔍 تم التعرف على الرابط ({platform}). جاري فحص الملف...")
    
    try:
        info = get_media_info(url)
        title = info.get('title', 'Media')
        ext = info.get('ext')
        formats = info.get('formats')
        
        # تحميل الصور من إنستجرام
        if not formats and (ext in ['jpg', 'png', 'jpeg'] or '_type' in info and info['_type'] == 'playlist'):
            await msg.edit_text("⏳ جاري تحميل الصور...")
            ydl_opts = {'cookiefile': 'cookies.txt', 'outtmpl': 'downloads/%(id)s.%(ext)s'}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                res_info = ydl.extract_info(url, download=True)
                if 'entries' in res_info:
                    for entry in res_info['entries']:
                        filename = ydl.prepare_filename(entry)
                        if os.path.exists(filename):
                            await client.send_photo(chat_id, photo=filename)
                            os.remove(filename)
                    await msg.delete()
                else:
                    filename = ydl.prepare_filename(res_info)
                    if os.path.exists(filename):
                        await client.send_photo(chat_id, photo=filename)
                        os.remove(filename)
                        await msg.delete()
            return

        # فحص الجودات المتاحة بدون الحاجة لـ FFmpeg
        available_res = {}
        target_resolutions = ['360p', '480p', '720p', '1080p']
        
        if formats:
            for f in formats:
                height = f.get('height')
                if height:
                    res_str = f"{height}p"
                    if res_str in target_resolutions and res_str not in available_res:
                        filesize = f.get('filesize') or f.get('filesize_approx')
                        size_mb = f"{round(filesize / (1024 * 1024), 1)} MB" if filesize else "غير معروف"
                        available_res[res_str] = {
                            'size': size_mb
                        }
        
        # لو مفيش جودات متعددة (فيديو قصير/ريل)، حمله مباشرة
        if not available_res:
            await msg.edit_text("⏳ جاري تحميل الفيديو مباشرة...")
            ydl_opts = {
                'cookiefile': 'cookies.txt',
                'outtmpl': 'downloads/%(title)s.%(ext)s',
                'format': 'best'
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                r_info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(r_info)
            await client.send_video(chat_id, video=filename)
            os.remove(filename)
            await msg.delete()
            return

        # عرض الأزرار الأربعة المتاحة
        keyboard = []
        for res in target_resolutions:
            if res in available_res:
                text = f"{res} ({available_res[res]['size']})"
                keyboard.append([InlineKeyboardButton(text, callback_data=f"dl_{res}")])
            else:
                # لو الجودة مش موجودة، البوت هيختار أفضل جودة قريبة متاحة تلقائياً
                keyboard.append([InlineKeyboardButton(text=f"{res} (أقرب جودة متاحة ⚡)", callback_data=f"dl_{res}")])
                
        await msg.edit_text(f"🎬 **{title}**\n\nاختر الجودة المطلوبة:", reply_markup=InlineKeyboardMarkup(keyboard))
        
    except Exception as e:
        await msg.edit_text(f"❌ حدث خطأ أثناء فحص الرابط: {str(e)}")

@app.on_callback_query()
async def download_callback(client, callback_query):
    data = callback_query.data
    chat_id = callback_query.message.chat.id
    
    url = user_urls.get(chat_id)
    if not url:
        await callback_query.message.edit_text("❌ انتهت صلاحية الجلسة، أرسل الرابط مرة أخرى.")
        return

    parts = data.split("_")
    res = parts[1]
    target_height = res.replace("p", "")
    
    await callback_query.message.edit_text(f"⏳ جاري تحميل جودة {res}...")
    
    # استخدام تنسيق آمن لا يتطلب وجود FFmpeg
    ydl_opts = {
        'cookiefile': 'cookies.txt',
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'format': f'best[height<={target_height}]/best',
    }

    try:
        os.makedirs("downloads", exist_ok=True)
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            
        await callback_query.message.edit_text("📤 جاري رفع الملف إليك...")
        await client.send_video(chat_id, video=filename)
        os.remove(filename)
    except Exception as e:
        await callback_query.message.edit_text(f"❌ حدث خطأ أثناء التحميل: {str(e)}")

if __name__ == "__main__":
    app.run()
