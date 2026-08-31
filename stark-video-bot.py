import os
import yt_dlp
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# بيانات البوت (حط بياناتك هنا لو مش معارِفها في ملف تانٍ أو متغيرات بيئة)
API_ID = 1234567  # استبدلها بـ API ID الخاص بك
API_HASH = "your_api_hash"
BOT_TOKEN = "your_bot_token"

app = Client(
    "stark_video_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# دالة لجلب الجودات المتاحة وحساب الحجم التقديري
def get_video_formats(url):
    ydl_opts = {
        'cookiefile': 'cookies.txt',
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        formats = info.get('formats', [])
        
        available_res = {}
        target_resolutions = ['360p', '480p', '720p', '1080p']
        
        for f in formats:
            height = f.get('height')
            if height:
                res_str = f"{height}p"
                if res_str in target_resolutions and res_str not in available_res:
                    filesize = f.get('filesize') or f.get('filesize_approx')
                    size_mb = f"{round(filesize / (1024 * 1024), 1)} MB" if filesize else "غير معروف"
                    available_res[res_str] = {
                        'format_id': f['format_id'],
                        'size': size_mb
                    }
                    
        return available_res, info.get('title', 'video')

# إرسال قائمة الأزرار للمستخدم
@app.on_message(filters.text & ~filters.command(["start"]))
async def send_qualities(client, message):
    url = message.text
    if not url.startswith("http"):
        return
        
    msg = await message.reply_text("⏳ جاري فحص الجودات المتاحة للفيلم...")
    
    try:
        available_res, title = get_video_formats(url)
        target_resolutions = ['360p', '480p', '720p', '1080p']
        
        keyboard = []
        for res in target_resolutions:
            if res in available_res:
                text = f"{res} ({available_res[res]['size']})"
                cb_data = f"dl_{res}_{url}"
                keyboard.append([InlineKeyboardButton(text, callback_data=cb_data)])
            else:
                keyboard.append([InlineKeyboardButton(text=f"{res} (توليد تلقائي ⚙️)", callback_data=f"gen_{res}_{url}")])
                
        await msg.edit_text(f"اختر الجودة المطلوبة للفيلم:\n**{title}**", reply_markup=InlineKeyboardMarkup(keyboard))
    except Exception as e:
        await msg.edit_text(f"❌ حدث خطأ أثناء جلب البيانات: {str(e)}")

# معالجة الضغط على الأزرار والتحميل أو التحويل بـ ffmpeg
@app.on_callback_query()
async def download_callback(client, callback_query):
    data = callback_query.data
    parts = data.split("_", 2)
    action = parts[0]
    res = parts[1]
    url = parts[2]
    
    target_height = res.replace("p", "")
    
    if action == "dl":
        await callback_query.message.edit_text(f"⏳ جاري تحميل جودة {res}...")
        ydl_opts = {
            'cookiefile': 'cookies.txt',
            'outtmpl': 'downloads/%(title)s.%(ext)s',
            'format': f'bestvideo[height<={target_height}]+bestaudio/best[height<={target_height}]',
        }
    elif action == "gen":
        await callback_query.message.edit_text(f"⚙️ الجودة غير متوفرة مباشرة، جاري تحميل أعلى جودة ومعالجتها لـ {res} عبر FFmpeg...")
        ydl_opts = {
            'cookiefile': 'cookies.txt',
            'outtmpl': 'downloads/%(title)s.%(ext)s',
            'format': 'bestvideo+bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4',
            }],
            'postprocessor_args': [
                '-vf', f'scale=-2:{target_height}'
            ]
        }

    try:
        os.makedirs("downloads", exist_ok=True)
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            
        await callback_query.message.edit_text("📤 جاري رفع الفيلم إليك...")
        await client.send_video(callback_query.message.chat.id, video=filename)
        os.remove(filename)
    except Exception as e:
        await callback_query.message.edit_text(f"❌ حدث خطأ أثناء المعالجة أو التحميل: {str(e)}")

# تشغيل البوت
if __name__ == "__main__":
    app.run()
