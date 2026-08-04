import static_ffmpeg
static_ffmpeg.add_paths()
import os
import time
import subprocess
import requests
import asyncio
from threading import Thread
from flask import Flask
from deep_translator import GoogleTranslator
import edge_tts

# Dummy Web Server (Render Free Tier port binding ke liye)
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running 24/7!"

# Telegram Bot Token
TOKEN = "8966768712:AAGPEtTSXQJqjcffWal6GjtiwfmjuY6uAo"
API_URL = f"https://api.telegram.org/bot{TOKEN}/"

def send_message(chat_id, text):
    requests.post(API_URL + "sendMessage", json={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"})

def process_video(chat_id, file_id, caption):
    send_message(chat_id, "📥 Video receive ho gayi... Processing shuru ho rahi hai!")
    
    file_info = requests.get(API_URL + "getFile", params={"file_id": file_id}).json()
    file_path = file_info["result"]["file_path"]
    download_url = f"https://api.telegram.org/file/bot{TOKEN}/{file_path}"
    
    input_video = f"input_{chat_id}.mp4"
    hindi_audio = f"hindi_{chat_id}.mp3"
    output_video = f"dubbed_{chat_id}.mp4"

    try:
        send_message(chat_id, "⚙️ Step 1/3: Video Download ho rahi hai...")
        video_bytes = requests.get(download_url).content
        with open(input_video, "wb") as f:
            f.write(video_bytes)

        send_message(chat_id, "🌐 Step 2/3: Hindi Translation & Voice generate ho rahi hai...")
        text_to_translate = caption if caption else "Hello, welcome to this video!"
        
        hindi_text = GoogleTranslator(source='auto', target='hi').translate(text_to_translate)

        async def make_tts():
            communicate = edge_tts.Communicate(text=hindi_text, voice="hi-IN-SwaraNeural")
            await communicate.save(hindi_audio)
        asyncio.run(make_tts())

        send_message(chat_id, "🎞 Step 3/3: Video aur Hindi Audio Merge ho rahe hain...")
        cmd = [
            "ffmpeg", "-y",
            "-i", input_video,
            "-i", hindi_audio,
            "-c:v", "copy",
            "-map", "0:v:0",
            "-map", "1:a:0",
            "-shortest", output_video
        ]
        subprocess.run(cmd, check=True)

        send_message(chat_id, "🚀 Uploading Dubbed Video...")
        with open(output_video, 'rb') as v_file:
            requests.post(
                API_URL + "sendVideo",
                data={"chat_id": chat_id, "caption": f"✅ *Hindi Dubbed Video Ready!*\n\n📝 *Hindi Translation:* {hindi_text}"},
                files={"video": v_file}
            )

    except Exception as e:
        send_message(chat_id, f"❌ Error: {str(e)}")

    finally:
        for f in [input_video, hindi_audio, output_video]:
            if os.path.exists(f):
                os.remove(f)

def bot_loop():
    print("Bot loop active...")
    offset = 0
    while True:
        try:
            res = requests.get(API_URL + "getUpdates", params={"offset": offset, "timeout": 20}).json()
            for update in res.get("result", []):
                offset = update["update_id"] + 1
                if "message" in update and "video" in update["message"]:
                    chat_id = update["message"]["chat"]["id"]
                    file_id = update["message"]["video"]["file_id"]
                    caption = update["message"].get("caption", "")
                    process_video(chat_id, file_id, caption)
        except Exception as err:
            print(f"Error: {err}")
            time.sleep(3)

if __name__ == "__main__":
    # Bot loop ko alag thread me start karenge
    Thread(target=bot_loop, daemon=True).start()
    
    # Main thread par Flask server chalega taaki Render port detect kar sake
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
    
