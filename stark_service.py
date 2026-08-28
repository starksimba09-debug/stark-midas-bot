import os
from threading import Thread
import telebot
from flask import Flask

TOKEN = os.environ.get("API_TOKEN")
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)


@app.route("/")
def home():
  return "Stark Midas Bot is active and running 24/7!"


@bot.message_handler(commands=["start"])
def send_welcome(message):
  bot.reply_to(message, "أهلاً بيك يا بطل، البوت شغال وزي الفل!")


def run_flask():
  port = int(os.environ.get("PORT", 8080))
  app.run(host="0.0.0.0", port=port)


if __name__ == "__main__":
  t = Thread(target=run_flask)
  t.start()
  print("Stark Midas Bot Service Started Successfully.")
  bot.infinity_polling()
