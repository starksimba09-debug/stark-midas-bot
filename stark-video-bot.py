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
        "👋 أهلاً بك في بوت Stark Video لتحميل الفيديوهات!\n\n"
        "🎬 أرسل رابط الفيديو الآن، وسأقوم بتحميله وإرساله لك فوراً."
    )

# دالة استقبال الروابط وتحميلها
@app.on_message(filters.text & ~filters.command(["start", "help"]))
async def download_video(client, message):
    url = message.text
    if "http" in url:
        sent_message = await message.reply_text("📥 جاري فحص وتحميل الفيديو...")
        try:
            ydl_opts = {
                'format': 'best',
                'outtmpl': 'video.mp4',
                'max_filesize': 50 * 1024 * 1024, # حد أقصى 50 ميجا عشان تيليجرام
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
            
            await message.reply_video(filename, caption="✅ تم التحميل بنجاح بواسطة Stark Bot!")
            await sent_message.delete()
            
            # حذف الملف بعد الإرسال لتوفير المساحة
            if os.path.exists(filename):
                os.remove(filename)
                
        except Exception as e:
            await sent_message.edit_text(f"❌ حدث خطأ أثناء التحميل: {str(e)}")
    else:
        await message.reply_text("⚠️ أهلاً بك! يرجى إرسال رابط فيديو صحيح للتحميل.")

if __name__ == "__main__":
    print("🤖 Stark Video Bot is running...")
    app.run()
