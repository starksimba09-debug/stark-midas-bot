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
        'format': 'best/bestvideo+bestaudio',
        'socket_timeout': 30,
        'extractor_args': {
            'instagram': {
                'max_comments': [0],
            }
        },
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Sec-Fetch-Mode': 'navigate',
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
