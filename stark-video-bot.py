import os
from pyrogram import Client, filters
import yt_dlp

# إعدادات البوت باستخدام متغيرات البيئة
API_ID = int(os.environ.get("API_ID")) if os.environ.get("API_ID") else None
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")

app = Client(
    "stark_video_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

@app.on_message(filters.command("start"))
async def start_command(client, message):
    await message.reply_text(
        "👋 أهلاً بك في بوت Stark Video لتحميل الفيديوهات والصور!\n\n"
        "📥 أرسل رابط المنشور (فيديو أو صورة) الآن، وسأقوم بتحميله وإرساله لك فوراً."
    )

# دالة استقبال الروابط وتحميل الملفات (صور أو فيديوهات)
@app.on_message(filters.text & ~filters.command(["start", "help"]))
async def download_media(client, message):
    url = message.text
    if "http" in url:
        sent_message = await message.reply_text("📥 جاري فحص وتحميل الملف...")
        try:
            ydl_opts = {
                'format': 'best/bestvideo+bestaudio',
                'outtmpl': 'downloaded_media.%(ext)s',
                'max_filesize': 50 * 1024 * 1024, # حد أقصى 50 ميجا عشان تيليجرام
                'noplaylist': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
            
            # التأكد من صيغة الملف لإرساله بالطريقة الصحيحة (صورة أو فيديو)
            if filename.endswith(('.jpg', '.jpeg', '.png', '.webp')):
                await message.reply_photo(filename, caption="✅ تم تحميل الصورة بنجاح بواسطة Stark Bot!")
            else:
                await message.reply_video(filename, caption="✅ تم تحميل الفيديو بنجاح بواسطة Stark Bot!")
                
            await sent_message.delete()
            
            # حذف الملف المؤقت بعد الإرسال
            if os.path.exists(filename):
                os.remove(filename)
                
        except Exception as e:
            await sent_message.edit_text(f"❌ حدث خطأ أثناء التحميل: {str(e)}")
    else:
        await message.reply_text("⚠️ أهلاً بك! يرجى إرسال رابط صحيح (فيديو أو صورة).")

if __name__ == "__main__":
    print("🤖 Stark Video Bot is running...")
    app.run()
