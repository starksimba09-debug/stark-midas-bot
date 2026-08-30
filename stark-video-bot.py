import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import yt_dlp

API_ID = 37361961
API_HASH = "36eca100c1861a8dc32ccec4fd284c24"
BOT_TOKEN = "8528693331:AAHhUHbnOKVgrEpAl5mbGLUft9Wzzlw3sVE"

app = Client("stark_video_bot_session", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# تخزين مؤقت لبيانات الفيديوهات لكل مستخدم
user_data_cache = {}

def get_readable_file_size(size_in_bytes):
    """دالة لتحويل الحجم من بايت إلى ميجابايت أو جيجابايت بشكل مقروء"""
    if size_in_bytes is None:
        return "المساحة غير متوفرة"
    for unit in ['بايت', 'كيلوبايت', 'ميجابايت', 'جيجابايت']:
        if size_in_bytes < 1024.0:
            return f"{size_in_bytes:.1f} {unit}"
        size_in_bytes /= 1024.0
    return f"{size_in_bytes:.1f} تيرابايت"

@app.on_message(filters.command("start"))
async def start_command(client, message):
    await message.reply_text(
        "👋 أهلاً بك في بوت Stark Video الذكي!\n\n"
        "🎬 أرسل رابط الفيديو الآن، وسأقوم بفحصه فوراً لتعرض لك الجودات المتاحة مع المساحات الدقيقة لاختيار ما يناسبك."
    )

@app.on_message(filters.regex(r"https?://[^\s]+") & filters.private)
async def check_video_qualities(client, message):
    user_id = message.from_user.id
    url = message.text
    
    sent_msg = await message.reply_text("🔍 جاري فحص الجودات المتاحة وحساب المساحات بدقة...")

    ydl_opts = {
        'cookiefile': 'cookies.txt',
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        }
    }

    try:
        def extract_info():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                return ydl.extract_info(url, download=False)

        info = await asyncio.get_event_loop().run_in_executor(None, extract_info)
        formats = info.get('formats', [])
        
        available_heights = set()
        format_options = {}

        for f in formats:
            height = f.get('height')
            if height and height >= 360:
                available_heights.add(height)
                filesize = f.get('filesize') or f.get('filesize_approx')
                format_options[height] = filesize

        target_qualities = [360, 480, 720, 1080]
        keyboard_buttons = []
        
        user_data_cache[user_id] = {'url': url, 'formats': format_options}

        for q in target_qualities:
            closest_q = min(available_heights, key=lambda x: abs(x - q)) if available_heights else None
            
            if closest_q and abs(closest_q - q) <= 50:
                size_str = get_readable_file_size(format_options.get(closest_q))
                keyboard_buttons.append([
                    InlineKeyboardButton(f"📥 {closest_q}p ({size_str})", callback_data=f"dl_{closest_q}")
                ])

        if not keyboard_buttons:
            await sent_msg.edit("عذراً، لم أتمكن من العثور على جودات مناسبة لهذا الرابط.")
            return

        reply_markup = InlineKeyboardMarkup(keyboard_buttons)
        await sent_msg.edit("🎯 **اختر الجودة المناسبة للتحميل (مع المساحة التقريبية):**", reply_markup=reply_markup)

    except Exception as e:
        await sent_msg.edit(f"❌ حدث خطأ أثناء فحص الرابط: {str(e)[:100]}")

@app.on_callback_query(filters.regex(r"^dl_"))
async def download_selected_quality(client, callback_query):
    user_id = callback_query.from_user.id
    quality = int(callback_query.data.split("_")[1])
    
    user_info = user_data_cache.get(user_id)
    if not user_info:
        await callback_query.answer("انتهت صلاحية الجلسة، أرسل الرابط مرة أخرى.", show_alert=True)
        return

    url = user_info['url']
    await callback_query.message.edit_text(f"⏳ جاري تحميل وتجهيز جودة {quality}p، يرجى الانتظار...")

    output_template = f"media_{user_id}_{quality}"
    
    ydl_opts = {
        'outtmpl': output_template + '.%(ext)s',
        'format': f'bestvideo[height<={quality}]+bestaudio/best[height<={quality}]/best',
        'merge_output_format': 'mp4',
        'socket_timeout': 60,
        'cookiefile': 'cookies.txt',
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        }
    }
    
    try:
        def do_download():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                return ydl.prepare_filename(info)

        filename = await asyncio.get_event_loop().run_in_executor(None, do_download)
            
        if os.path.exists(filename):
            file_size_mb = os.path.getsize(filename) / (1024 * 1024)
            await callback_query.message.edit_text(f"📤 جاري رفع الفيديو الآن (الحجم: {file_size_mb:.1f} ميجابايت)...")
            
            await client.send_video(
                chat_id=callback_query.message.chat.id,
                video=filename,
                caption=f"✅ تم التحميل بجودة {quality}p بنجاح بواسطة Stark Bot 📥"
            )
            os.remove(filename)
            await callback_query.message.delete()
        else:
            await callback_query.message.edit("عذراً، لم أتمكن من تحميل الملف.")
            
    except Exception as e:
        await callback_query.message.edit(f"❌ حدث خطأ أثناء التحميل أو الرفع: {str(e)[:100]}")

if __name__ == "__main__":
    print("البوت الذكي يعمل الآن بكامل طاقته...")
    app.run()
