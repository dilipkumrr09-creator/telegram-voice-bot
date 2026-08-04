import asyncio
import os
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


TOKEN = "8966768712:AAHQE61_ogS6D2m9JHwC46Iv0HEx6qrwTqU"
API_URL = f"https://api.telegram.org/bot{TOKEN}/"


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
    # Get File path from Telegram
    file_info = requests.get(
        API_URL + "getFile", params={"file_id": file_id}
    ).json()
    if not file_info.get("ok"):
      send_message(
          chat_id,
          "❌ Telegram API ne video fetch karne se mana kar diya (File size"
          " limit > 20MB ho sakti hai).",
      )
      return

    file_path = file_info["result"]["file_path"]
    download_url = f"https://api.telegram.org/file/bot{TOKEN}/{file_path}"

    send_message(chat_id, "⚙️ Step 1/3: Video Download ho rahi hai...")
    video_bytes = requests.get(download_url).content
    with open(input_video, "wb") as f:
      f.write(video_bytes)

    send_message(
        chat_id, "🌐 Step 2/3: Hindi Translation & Voice generate ho rahi hai..."
    )
    text_to_translate = (
        caption if caption else "Hello, welcome to this video!"
    )

    hindi_text = GoogleTranslator(source="auto", target="hi").translate(
        text_to_translate
    )

    async def make_tts():
      communicate = edge_tts.Communicate(
          text=hindi_text, voice="hi-IN-SwaraNeural"
      )
      await communicate.save(hindi_audio)

    asyncio.run(make_tts())

    send_message(
        chat_id, "🎞 Step 3/3: Video aur Hindi Audio Merge ho rahe hain..."
    )
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        input_video,
        "-i",
        hindi_audio,
        "-c:v",
        "copy",
        "-map",
        "0:v:0",
        "-map",
        "1:a:0",
        "-shortest",
        output_video,
    ]
    subprocess.run(cmd, check=True)

    send_message(chat_id, "🚀 Uploading Dubbed Video...")
    with open(output_video, "rb") as v_file:
      requests.post(
          API_URL + "sendVideo",
          data={
              "chat_id": chat_id,
              "caption": (
                  "✅ *Hindi Dubbed Video Ready!*\n\n📝 *Hindi"
                  f" Translation:* {hindi_text}"
              ),
          },
          files={"video": v_file},
      )

  except Exception as e:
    print(f"Error in processing: {e}")
    send_message(chat_id, f"❌ Error: {str(e)}")

  finally:
    for f in [input_video, hindi_audio, output_video]:
      if os.path.exists(f):
        os.remove(f)


def bot_loop():
  print("Bot loop active...")

  # Clean webhook if active previously
  try:
    requests.get(API_URL + "deleteWebhook", params={"drop_pending_updates": True})
    print("Old webhooks cleared.")
  except Exception as e:
    print(f"Webhook error: {e}")

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

          # Handle /start text message
          if "text" in msg and msg["text"] == "/start":
            send_message(
                chat_id,
                "👋 Hello! Mujhe **Caption ke saath video** bhejo, main use Hindi"
                " me dub karke dunga.",
            )

          # Handle Video
          elif "video" in msg:
            file_id = msg["video"]["file_id"]
            caption = msg.get("caption", "")

            # Run video processing in a SEPARATE thread so it doesn't freeze the loop
            Thread(
                target=process_video, args=(chat_id, file_id, caption)
            ).start()

    except Exception as err:
      print(f"Loop Error: {err}")
      time.sleep(3)


if __name__ == "__main__":
  # Start Bot Thread
  Thread(target=bot_loop, daemon=True).start()

  # Start Flask
  port = int(os.environ.get("PORT", 10000))
  app.run(host="0.0.0.0", port=port)
          
