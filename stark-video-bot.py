import os
from pyrogram import Client, filters
import yt_dlp

# البيانات الخاصة بك
API_ID = 37361961
API_HASH = "36eca100c1861a8dc32ccec4fd284c24"
BOT_TOKEN = "8528693331:AAHhUHbnOKVgrEpAl5mbGLUft9Wzzlw3sVE"

app = Client("stark_video_bot_session", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.command("start"))
def start_command(client, message):
    message.reply_text("أهلاً بك في بوت Stark Video! ابعث لي رابط أي فيديو أو صورة من انستجرام، فيسبوك، أو جوجل، وسأقوم بتحميلها وإرسالها لك فوراً.")

@app.on_message(filters.regex(r"https?://[^\s]+") & (filters.private))
def download_media(client, message):
    url = message.text
    sent_msg = message.reply_text("⏳ جاري التحميل، سأرسله لك قريباً...")
    
    output_template = "media_file"
    
    ydl_opts = {
        'outtmpl': output_template + '.%(ext)s',
        'format': 'best',
        'socket_timeout': 30,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            
        if os.path.exists(filename):
            if filename.endswith(('.mp4', '.mkv', '.webm', '.mov', '.avi')):
                client.send_video(
                    chat_id=message.chat.id,
                    video=filename,
                    caption="تم التحميل بواسطة Stark Bot 📥"
                )
            elif filename.endswith(('.jpg', '.jpeg', '.png', '.webp')):
                client.send_photo(
                    chat_id=message.chat.id,
                    photo=filename,
                    caption="تم التحميل بواسطة Stark Bot 📥"
                )
            else:
                client.send_document(
                    chat_id=message.chat.id,
                    document=filename,
                    caption="تم التحميل بواسطة Stark Bot 📥"
                )
                
            os.remove(filename)
            sent_msg.delete()
        else:
            sent_msg.edit("عذراً، لم أتمكن من تحميل المحتوى. تأكد أن الرابط عام وصحيح.")
            
    except Exception as e:
        sent_msg.edit("حدث خطأ أثناء التحميل: تأكد من صحة الرابط أو أن المحتوى متاح للعامة.")

if __name__ == "__main__":
    print("البوت يعمل الآن...")
    app.run()
