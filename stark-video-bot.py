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
        "• أرسل لي **رابط** (إنستجرام، فيسبوك، أو يوتيوب)\n"
        "• أو أرسل لي **اسم أو كلمات الأغنية** وسأبحث عنها وأقوم بتحميلها لك فوراً 🎶🚀"
    )

@app.on_message(filters.text & ~filters.command(["start"]))
async def handle_incoming_text(client, message):
    text = message.text.strip()
    chat_id = message.chat.id
    
    # لو النص عبارة عن رابط
    if text.startswith("http"):
        query = text
        source_type = "url"
    else:
        # لو النص عبارة عن اسم أغنية أو كلمات بحث، بنخليه يبحث عنها في يوتيوب تلقائياً
        query = f"ytsearch1:{text}"
        source_type = "search"
        
    user_queries[chat_id] = query
    
    msg = await message.reply_text("🔍 جاري البحث والتحضير...")
    
    try:
        ydl_opts = {
            'cookiefile': 'cookies.txt',
            'quiet': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(query, download=False)
            
            # لو البحث جاب قائمة نتائج (معناها بحث نصي)
            if 'entries' in info:
                info = info['entries'][0]
                
            title = info.get('title', 'Audio/Video')
            duration = info.get('duration_string', '')
            
        # لو الرابط صورة من إنستجرام
        ext = info.get('ext')
        formats = info.get('formats', [])
        if not formats and ext in ['jpg', 'png', 'jpeg']:
            await msg.edit_text("⏳ جاري تحميل الصورة...")
            ydl_opts = {'cookiefile': 'cookies.txt', 'outtmpl': 'downloads/%(id)s.%(ext)s'}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                res_info = ydl.extract_info(query, download=True)
                filename = ydl.prepare_filename(res_info)
                if os.path.exists(filename):
                    await client.send_photo(chat_id, photo=filename)
                    os.remove(filename)
                    await msg.delete()
            return

        # لو اللي تم طلبه بحث عن أغنية أو فيديو، نعرض أزرار التحميل (صوت MP3 أو فيديو)
        keyboard = [
            [InlineKeyboardButton("🎵 تحميل صوت (MP3)", callback_data="dl_audio")],
            [InlineKeyboardButton("🎬 تحميل فيديو (MP4)", callback_data="dl_video")]
        ]
        
        await msg.edit_text(
            f"🎵 **تم العثور على النتيجة:**\n`{title}`\n⏱ المدة: {duration}\n\nاختر صيغة التحميل المطلوبة:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        
    except Exception as e:
        await msg.edit_text(f"❌ لم يتم العثور على نتائج مطابقة أو حدث خطأ:\n`{str(e)}`")

@app.on_callback_query()
async def download_callback(client, callback_query):
    data = callback_query.data
    chat_id = callback_query.message.chat.id
    
    query = user_queries.get(chat_id)
    if not query:
        await callback_query.message.edit_text("❌ انتهت صلاحية الجلسة، أرسل اسم الأغنية أو الرابط مرة أخرى.")
        return

    await callback_query.message.edit_text("⏳ جاري التحميل والمعالجة، يُرجى الانتظار...")
    
    try:
        os.makedirs("downloads", exist_ok=True)
        
        if data == "dl_audio":
            # تحميل الصوت بصيغة مريحة
            ydl_opts = {
                'cookiefile': 'cookies.txt',
                'outtmpl': 'downloads/%(title)s.%(ext)s',
                'format': 'bestaudio/best',
            }
        else:
            # تحميل الفيديو بأفضل جودة آمنة
            ydl_opts = {
                'cookiefile': 'cookies.txt',
                'outtmpl': 'downloads/%(title)s.%(ext)s',
                'format': 'best[height<=720]/best',
            }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(query, download=True)
            if 'entries' in info:
                info = info['entries'][0]
            filename = ydl.prepare_filename(info)
            
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
