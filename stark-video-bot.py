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
        "👋 أهلاً بك في بوت Stark Video لتحميل الميديا!\n\n"
        "📥 أرسل رابط المنشور (فيديو أو صورة) الآن، وسأقوم بتحميله وإرساله لك فوراً."
    )

# دالة استقبال الروابط وتحميل الملفات
@app.on_message(filters.text & ~filters.command(["start", "help"]))
async def download_media(client, message):
    url = message.text
    if "http" in url:
        sent_message = await message.reply_text("📥 جاري فحص وتحميل الملف...")
        try:
            ydl_opts = {
                'outtmpl': 'downloaded_media',
                'noplaylist': True,
                'skip_download': False,
                # السماح بتحميل الصور والفيديوهات وعدم تقييد الاستخراج
                'extract_flat': False,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                
                # لو البوست عبارة عن مجموعة صور (Album/Carousel)
                if 'entries' in info:
                    for entry in info['entries']:
                        filename = ydl.prepare_filename(entry)
                        if os.path.exists(filename):
                            if filename.endswith(('.jpg', '.jpeg', '.png', '.webp')):
                                await message.reply_photo(filename)
                            else:
                                await message.reply_video(filename)
                            os.remove(filename)
                    await sent_message.delete()
                    return

                filename = ydl.prepare_filename(info)
            
            # التأكد من مسار الملف وإرساله بالصيغة المناسبة
            if os.path.exists(filename):
                if filename.endswith(('.jpg', '.jpeg', '.png', '.webp')):
                    await message.reply_photo(filename, caption="✅ تم تحميل الصورة بنجاح!")
                else:
                    await message.reply_video(filename, caption="✅ تم تحميل الفيديو بنجاح!")
                os.remove(filename)
            else:
                # محاولة البحث عن أي ملف تم تنزيله بنفس الاسم الأساسي
                found = False
                for file in os.listdir('.'):
                    if file.startswith('downloaded_media'):
                        found = True
                        if file.endswith(('.jpg', '.jpeg', '.png', '.webp')):
                            await message.reply_photo(file, caption="✅ تم تحميل الصورة بنجاح!")
                        else:
                            await message.reply_video(file, caption="✅ تم تحميل الملف بنجاح!")
                        os.remove(file)
                        break
                if not found:
                    raise Exception("لم يتم العثور على ملف قابل للتحميل في هذا الرابط.")
                
            await sent_message.delete()
                
        except Exception as e:
            await sent_message.edit_text(f"❌ حدث خطأ أثناء التحميل: {str(e)}")
    else:
        await message.reply_text("⚠️ أهلاً بك! يرجى إرسال رابط صحيح.")

if __name__ == "__main__":
    print("🤖 Stark Video Bot is running...")
    app.run()
