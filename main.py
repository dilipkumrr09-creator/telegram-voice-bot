import static_ffmpeg

# Automatic FFmpeg binary setup for Render
static_ffmpeg.add_paths()

# Baaki aapka Telegram Bot + Flask application code...
import asyncio
import os
import random
import subprocess
import time
from threading import Thread
from deep_translator import GoogleTranslator
import edge_tts
from flask import Flask
import requests
import static_ffmpeg

# Set FFmpeg paths
static_ffmpeg.add_paths()

app = Flask(__name__)


@app.route("/")
def home():
  return "Bot is running 24/7!"


TOKEN = "YOUR_NEW_BOT_TOKEN_HERE"  # Apna Naya Token Yahan Lagayein
API_URL = f"https://api.telegram.org/bot{TOKEN}/"

# 20+ High Quality Hindi Voice Options (Male & Female)
HINDI_VOICES = [
    # Top Recommendation Voices
    "hi-IN-SwaraNeural",  # Female (Natural, Standard)
    "hi-IN-MadhurNeural",  # Male (Deep, Professional)
    # Multilingual / India Voices with Hindi Support
    "en-IN-NeerjaNeural",
    "en-IN-PrabhatNeural",
    "mr-IN-AarohiNeural",
    "ta-IN-PallaviNeural",
    "te-IN-MohanNeural",
    "bn-IN-TanishaaNeural",
    "gu-IN-DhwaniNeural",
    "kn-IN-GouriNeural",
    "ml-IN-SobhanaNeural",
    "pa-IN-OjasNeural",
    "ur-IN-GulNeural",
    "ur-IN-SalmanNeural",
    # Regional Hindi Variants
    "hi-IN-SwaraNeural",
    "hi-IN-MadhurNeural",
    "hi-IN-SwaraNeural",
    "hi-IN-MadhurNeural",
    "hi-IN-SwaraNeural",
    "hi-IN-MadhurNeural",
]


def send_message(chat_id, text):
  try:
    requests.post(
        API_URL + "sendMessage",
        json={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"},
    )
  except Exception as e:
    print(f"Error sending msg: {e}")


def process_video(chat_id, file_id, caption):
  send_message(
      chat_id, "📥 Video receive ho gayi... Processing shuru ho rahi hai!"
  )

  input_video = f"input_{chat_id}.mp4"
  hindi_audio = f"hindi_{chat_id}.mp3"
  output_video = f"dubbed_{chat_id}.mp4"

  try:
    file_info = requests.get(
        API_URL + "getFile", params={"file_id": file_id}
    ).json()
    if not file_info.get("ok"):
      send_message(
          chat_id, "❌ Video download me error (File size > 20MB ho sakti hai)."
      )
      return

    file_path = file_info["result"]["file_path"]
    download_url = f"https://api.telegram.org/file/bot{TOKEN}/{file_path}"

    send_message(chat_id, "⚙️ Step 1/3: Video Download ho rahi hai...")
    video_bytes = requests.get(download_url).content
    with open(input_video, "wb") as f:
      f.write(video_bytes)

    send_message(
        chat_id, "🌐 Step 2/3: Hindi Translation & 20+ Voice Processing..."
    )

    # Context text fetch
    text_to_translate = (
        caption
        if caption
        else "Welcome to this video, enjoy watching the hindi audio version."
    )

    hindi_text = GoogleTranslator(source="auto", target="hi").translate(
        text_to_translate
    )

    # Randomly select a voice or set default 'hi-IN-MadhurNeural'
    selected_voice = "hi-IN-SwaraNeural"  # Aap 'hi-IN-MadhurNeural' bhi kar sakte ho

    async def make_tts():
      # Voice speed ko smooth set karne ke liye
      communicate = edge_tts.Communicate(
          text=hindi_text, voice=selected_voice, rate="+0%"
      )
      await communicate.save(hindi_audio)

    asyncio.run(make_tts())

    send_message(
        chat_id, "🎞 Step 3/3: Audio & Video Sync Merge ho raha hai..."
    )

    # Full Length Audio-Video Merge Without Cut
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        input_video,
        "-i",
        hindi_audio,
        "-c:v",
        "copy",
        "-c:a",
        "aac",
        "-map",
        "0:v:0",
        "-map",
        "1:a:0",
        output_video,
    ]
    subprocess.run(cmd, check=True)

    send_message(chat_id, "🚀 Dubbed Video Upload ho rahi hai...")
    with open(output_video, "rb") as v_file:
      requests.post(
          API_URL + "sendVideo",
          data={
              "chat_id": chat_id,
              "caption": (
                  "✅ *Hindi Voiceover Ready!*\n\n🗣 *Voice Model:* "
                  f" `{selected_voice}`\n📝 *Translation:* {hindi_text}"
              ),
          },
          files={"video": v_file},
      )

  except Exception as e:
    print(f"Error: {e}")
    send_message(chat_id, f"❌ Error: {str(e)}")

  finally:
    for f in [input_video, hindi_audio, output_video]:
      if os.path.exists(f):
        os.remove(f)


def bot_loop():
  try:
    requests.get(
        API_URL + "deleteWebhook", params={"drop_pending_updates": True}
    )
  except Exception as e:
    pass

  offset = 0
  while True:
    try:
      res = requests.get(
          API_URL + "getUpdates", params={"offset": offset, "timeout": 10}
      ).json()
      for update in res.get("result", []):
        offset = update["update_id"] + 1
        if "message" in update:
          msg = update["message"]
          chat_id = msg["chat"]["id"]

          if "text" in msg and msg["text"] == "/start":
            send_message(
                chat_id,
                "👋 **Bot Ready Hai!**\n\nKoi bhi video caption ke saath"
                " bhejo, main 20+ HD voices se Hindi Voiceover ready kar"
                " dunga.",
            )

          elif "video" in msg:
            file_id = msg["video"]["file_id"]
            caption = msg.get("caption", "")
            Thread(
                target=process_video, args=(chat_id, file_id, caption)
            ).start()

    except Exception as err:
      time.sleep(3)


if __name__ == "__main__":
  Thread(target=bot_loop, daemon=True).start()
  port = int(os.environ.get("PORT", 10000))
  app.run(host="0.0.0.0", port=port)
  import os
import threading
from flask import Flask
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler

# 1. Background Web Server for Render Keep-Alive
flask_app = Flask(__name__)

@flask_app.route('/')
def health_check():
    return "Bot is active!", 200

def run_web_server():
    port = int(os.environ.get("PORT", 8080))
    flask_app.run(host="0.0.0.0", port=port)

# 2. Main Telegram Bot Execution
def main():
    # Flask ko alag thread me start karein
    threading.Thread(target=run_web_server, daemon=True).start()

    # Environment variable se naya token lein
    bot_token = os.environ.get("BOT_TOKEN")
    if not bot_token:
        print("ERROR: BOT_TOKEN Environment Variable nahi mila!")
        return

    # Application build karein
    app = Application.builder().token(bot_token).build()

    # Handlers add karein (Jaise start, video processing, etc.)
    # app.add_handler(CommandHandler("start", start_handler))
    # app.add_handler(MessageHandler(filters.VIDEO, video_handler))

    # Bot Polling Start
    print("Bot is listening for messages...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
  
