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

user_queries = {}

@app.on_message(filters.command("start"))
async def start_command(client, message):
    await message.reply_text(
        "👋 أهلاً بك في بوت التحميل (Stark Video Bot)!\n\n"
        "• أرسل لي **رابط** (إنستجرام، فيسبوك، بينتريست، يوتيوب)\n"
        "• أو أرسل لي **اسم أو كلمات الأغنية** وسأبحث عنها وأقوم بتحميلها لك فوراً 🎶🚀"
    )

@app.on_message(filters.text & ~filters.command(["start"]))
async def handle_incoming_text(client, message):
    text = message.text.strip()
    chat_id = message.chat.id
    
    # تحديد ما إذا كان رابطاً أو نص بحث
    if text.startswith("http"):
        query = text
    else:
        query = f"ytsearch1:{text}"
        
    user_queries[chat_id] = query
    
    msg = await message.reply_text("🔍 جاري البحث والتحضير...")
    
    try:
        ydl_opts = {
            'cookiefile': 'cookies.txt',
            'quiet': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(query, download=False)
            
            # معالجة نتائج البحث النصي بأمان
            if 'entries' in info:
                entries = info.get('entries')
                if not entries:
                    await msg.edit_text("❌ عذراً، لم يتم العثور على أي نتائج مطابقة لبحثك.")
                    return
                info = entries[0]
                
            title = info.get('title', 'Media File')
            duration = info.get('duration_string', '')
            ext = info.get('ext')
            formats = info.get('formats', [])
            
        # التحقق مما إذا كانت الملفات عبارة عن صورة مباشرة (مثل بينتريست أو صور إنستجرام)
        if not formats or ext in ['jpg', 'png', 'jpeg'] or 'pinterest' in query.lower():
            await msg.edit_text("⏳ جاري تحميل الصورة بدقة عالية...")
            
            # استخدام إعدادات مخصصة لتحميل الصور وتجنب خطأ صيغ الفيديو
            img_opts = {
                'cookiefile': 'cookies.txt',
                'outtmpl': 'downloads/%(id)s.%(ext)s',
                'format': 'best'
            }
            
            with yt_dlp.YoutubeDL(img_opts) as ydl:
                res_info = ydl.extract_info(query, download=True)
                if 'entries' in res_info and res_info['entries']:
                    res_info = res_info['entries'][0]
                
                filename = ydl.prepare_filename(res_info)
                
                # التأكد من امتداد الصورة لو الـ ydl غيره لـ webp أو حاجة تانية
                if not os.path.exists(filename):
                    # البحث عن أي ملف بنفس المعرف في مجلد التحميلات
                    for f in os.listdir("downloads"):
                        if f.startswith(str(res_info.get('id', ''))):
                            filename = os.path.join("downloads", f)
                            break
                            
                if os.path.exists(filename):
                    await client.send_photo(chat_id, photo=filename, caption=f"📌 {title}")
                    os.remove(filename)
                    await msg.delete()
                    return
                else:
                    raise Exception("فشل العثور على ملف الصورة المحملة.")

        # لو النتيجة فيديو أو أغنية، اعرض أزرار الاختيار
        keyboard = [
            [InlineKeyboardButton("🎵 تحميل صوت (MP3)", callback_data="dl_audio")],
            [InlineKeyboardButton("🎬 تحميل فيديو (MP4)", callback_data="dl_video")]
        ]
        
        await msg.edit_text(
            f"🎵 **تم العثور على النتيجة:**\n`{title}`\n⏱ المدة: {duration}\n\nاختر صيغة التحميل المطلوبة:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        
    except Exception as e:
        await msg.edit_text(f"❌ حدث خطأ أثناء المعالجة:\n`{str(e)}`")

@app.on_callback_query()
async def download_callback(client, callback_query):
    data = callback_query.data
    chat_id = callback_query.message.chat.id
    
    query = user_queries.get(chat_id)
    if not query:
        await callback_query.message.edit_text("❌ انتهت صلاحية الجلسة، أرسل الرابط مرة أخرى.")
        return

    await callback_query.message.edit_text("⏳ جاري التحميل والمعالجة، يُرجى الانتظار...")
    
    try:
        os.makedirs("downloads", exist_ok=True)
        
        if data == "dl_audio":
            ydl_opts = {
                'cookiefile': 'cookies.txt',
                'outtmpl': 'downloads/%(title)s.%(ext)s',
                'format': 'bestaudio/best',
            }
        else:
            ydl_opts = {
                'cookiefile': 'cookies.txt',
                'outtmpl': 'downloads/%(title)s.%(ext)s',
                'format': 'best[height<=720]/best',
            }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = yt_dlp.YoutubeDL({'cookiefile': 'cookies.txt', 'quiet': True}).extract_info(query, download=False)
            if 'entries' in info and info['entries']:
                info = info['entries'][0]
                
            res_info = ydl.extract_info(query, download=True)
            if 'entries' in res_info and res_info['entries']:
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
        await callback_query.message.edit_text(f"❌ حدث خطأ أثناء التحميل: {str(e)}")

if __name__ == "__main__":
    app.run()
