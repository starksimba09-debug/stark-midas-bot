import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
import yt_dlp

API_ID = 37361961
API_HASH = "36eca100c1861a8dc32ccec4fd284c24"
BOT_TOKEN = "8528693331:AAHhUHbnOKVgrEpAl5mbGLUft9Wzzlw3sVE"

app = Client("stark_video_bot_session", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# تخزين مؤقت للروابط عشان الأزرار
user_links = {}

@app.on_message(filters.command("start"))
async def start_command(client, message):
    await message.reply_text("أهلاً بك في بوت Stark Video! ابعث لي رابط أي فيديو من انستجرام، فيسبوك، أو يوتيوب، وسأعرض عليك الجودات والمساحات المتاحة لتختار منها.")

@app.on_message(filters.regex(r"https?://[^\s]+") & filters.private)
async def get_video_qualities(client, message):
    url = message.text
    sent_msg = await message.reply_text("🔍 جاري فحص الرابط وجلب الجودات المتاحة...")
    
    ydl_opts = {
        'socket_timeout': 30,
        'skip_download': True,
    }
    
    try:
        def extract():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                return ydl.extract_info(url, download=False)
                
        info = await asyncio.get_event_loop().run_in_executor(None, extract)
        formats = info.get('formats', [])
        
        buttons = []
        seen_resolutions = set()
        
        for f in formats:
            # فلترة الصيغ اللي فيها فيديو وصوت أو فيديو بس وبجودة واضحة
            if f.get('vcodec') != 'none' and f.get('height'):
                height = f.get('height')
                ext = f.get('ext', 'mp4')
                filesize = f.get('filesize') or f.get('filesize_approx')
                
                # تجميع الجودات المتشابهة عشان متتكرش
                res_key = f"{height}p"
                if res_key in seen_resolutions:
                    continue
                seen_resolutions.add(res_key)
                
                # حساب المساحة بالميجابايت
                if filesize:
                    size_mb = round(filesize / (1024 * 1024), 1)
                    size_str = f" (~{size_mb} MB)"
                else:
                    size_str = " (مساحة غير متوفرة)"
                
                format_id = f.get('format_id')
                button_text = f"{height}p ({ext.upper()}){size_str}"
                
                buttons.append([
                    InlineKeyboardButton(button_text, callback_data=f"dl_{format_id}")
                ])
        
        if not buttons:
            await sent_msg.edit("عذراً، لم أتمكن من العثور على جودات متاحة لهذا الرابط.")
            return
            
        # حفظ الرابط في الذاكرة المؤقتة للمستخدم
        user_links[message.from_user.id] = url
        
        # تحديد عدد الأزرار (أقصى حد 5 جودات عشان الشكل العام)
        buttons = buttons[:6]
        keyboard = InlineKeyboardMarkup(buttons)
        
        await sent_msg.edit("🔽 **اختر الجودة المناسبة للتحميل:**", reply_markup=keyboard)
        
    except Exception as e:
        await sent_msg.edit("❌ حدث خطأ أثناء فحص الرابط. تأكد أنه عام وصحيح.")

@app.on_callback_query(filters.regex(r"^dl_"))
async def download_selected_quality(client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    if user_id not in user_links:
        await callback_query.answer("انتهت صلاحية الطلب، أرسل الرابط مرة أخرى.", show_alert=True)
        return
        
    url = user_links[user_id]
    format_id = callback_query.data.split("_")[1]
    
    await callback_query.message.edit_text("⏳ جاري تحميل الفيديو بالجودة المحددة، سأرسله قريباً...")
    
    output_template = f"video_{user_id}.%(ext)s"
    
    ydl_opts = {
        'format': f"{format_id}+bestaudio/best",
        'outtmpl': output_template,
        'merge_output_format': 'mp4',
        'socket_timeout': 30,
    }
    
    try:
        def download_file():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                return ydl.prepare_filename(info)
                
        filename = await asyncio.get_event_loop().run_in_executor(None, download_file)
        
        # تصحيح الامتداد لو حصل دمج لـ mp4
        if not os.path.exists(filename) and os.path.exists(filename.rsplit('.', 1)[0] + '.mp4'):
            filename = filename.rsplit('.', 1)[0] + '.mp4'
            
        if os.path.exists(filename):
            await client.send_video(
                chat_id=callback_query.message.chat.id,
                video=filename,
                caption="تم التحميل بواسطة Stark Bot 📥"
            )
            os.remove(filename)
            await callback_query.message.delete()
        else:
            await callback_query.message.edit("❌ عذراً، حدث خطأ أثناء معالجة الملف.")
            
    except Exception as e:
        await callback_query.message.edit("❌ حدث خطأ أثناء التحميل. قد يكون الرابط محميًا أو غير مدعوم.")

if __name__ == "__main__":
    print("البوت يعمل الآن مع ميزة اختيار الجودة والمساحة...")
    app.run()
