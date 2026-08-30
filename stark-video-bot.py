import os
from pyrogram import Client, filters
import yt_dlp

API_ID = 37361961
API_HASH = "36eca100c1861a8dc32ccec4fd284c24"
BOT_TOKEN = "8528693331:AAHhUHbnOKVgrEpAl5mbGLUft9Wzzlw3sVE"

app = Client("stark_video_bot_session", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.command("start"))
def start_command(client, message):
    message.reply_text("أهلاً بك في بوت Stark Video السريع! ابعث لي رابط أي فيديو أو ريلز من انستجرام أو فيسبوك وسأرسله لك فوراً.")

@app.on_message(filters.regex(r"https?://[^\s]+") & filters.private)
def download_media(client, message):
    url = message.text
    sent_msg = message.reply_text("⏳ جاري التحميل بأقصى سرعة...")
    
    output_template = f"media_{message.from_user.id}"
    
    ydl_opts = {
        'outtmpl': output_template + '.%(ext)s',
        'format': 'best',
        'socket_timeout': 30,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        }
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            
        if os.path.exists(filename):
            client.send_video(
                chat_id=message.chat.id,
                video=filename,
                caption="تم التحميل بواسطة Stark Bot 📥"
            )
            os.remove(filename)
            sent_msg.delete()
        else:
            sent_msg.edit("عذراً، لم أتمكن من تحميل الملف. تأكد من صحة الرابط.")
            
    except Exception as e:
        sent_msg.edit("حدث خطأ أثناء التحميل. تأكد أن الرابط متاح للعامة.")

if __name__ == "__main__":
    print("البوت السريع يعمل الآن...")
    app.run()
