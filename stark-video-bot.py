import os
import asyncio
from pyrogram import Client, filters
import yt_dlp

API_ID = 37361961
API_HASH = "36eca100c1861a8dc32ccec4fd284c24"
BOT_TOKEN = "8528693331:AAHhUHbnOKVgrEpAl5mbGLUft9Wzzlw3sVE"

app = Client("stark_video_bot_session", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.command("start"))
async def start_command(client, message):
    await message.reply_text("أهلاً بك في بوت Stark Video السريع! ابعث لي رابط أي فيديو أو ريلز وسأرسله لك فوراً.")

@app.on_message(filters.regex(r"https?://[^\s]+") & filters.private)
async def download_media(client, message):
    url = message.text
    sent_msg = await message.reply_text("⏳ جاري التحميل بأقصى سرعة...")
    
    output_template = f"media_{message.from_user.id}"
    
    ydl_opts = {
        'outtmpl': output_template + '.%(ext)s',
        'format': 'best',
        'socket_timeout': 30,
        'extractor_args': {
            'instagram': {
                'api_version': 'v1'
            }
        },
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
            await client.send_video(
                chat_id=message.chat.id,
                video=filename,
                caption="تم التحميل بواسطة Stark Bot 📥"
            )
            os.remove(filename)
            await sent_msg.delete()
        else:
            await sent_msg.edit("عذراً، لم أتمكن من تحميل الملف. تأكد من صحة الرابط.")
            
    except Exception as e:
        await sent_msg.edit("حدث خطأ أثناء التحميل. تأكد أن الرابط متاح للعامة.")

if __name__ == "__main__":
    print("البوت السريع يعمل الآن...")
    app.run()
