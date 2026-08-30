import os
from pyrogram import Client, filters
import yt_dlp
import google.generativeai as genai

# إعداد مفتاح جيميناي من متغيرات البيئة في Railway
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
ai_model = genai.GenerativeModel("gemini-1.5-flash")

# إعدادات البوت باستخدام متغيرات البيئة الحساسة
API_ID = os.environ.get("API_ID")
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
        "👋 أهلاً بك في بوت Stark Video الذكي!\n\n"
        "🎬 أرسل رابط الفيديو الآن، وسأقوم بفحصه فوراً لتعرض لك الجودات المتاحة مع المساحات الدقيقة لاختيار ما يناسبك.\n"
        "🤖 ويمكنك أيضاً التحدث معي في أي وقت كذكاء اصطناعي!"
    )

# دالة الرد بالذكاء الاصطناعي لأي رسالة نصية لا تبدأ برابط أو أمر
@app.on_message(filters.text & ~filters.command(["start", "help"]) & ~filters.regex(r"https?://"))
async def chat_with_ai(client, message):
    try:
        sent_message = await message.reply_text("🤖 جاري التفكير...")
        
        # استدعاء نموذج Gemini للرد
        response = ai_model.generate_content(message.text)
        
        await sent_message.edit_text(response.text)
    except Exception as e:
        await sent_message.edit_text(f"حدث خطأ أثناء الاتصال بالذكاء الاصطناعي: {str(e)}")

if __name__ == "__main__":
    print("🤖 Stark Bot is running...")
    app.run()
