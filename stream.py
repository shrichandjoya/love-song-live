import os
import time
import subprocess
import threading
import pytchat

# अपनी चलती हुई YouTube Live Stream के लिंक की 11 अक्षरों वाली Video ID यहाँ डालें
# उदाहरण: https://youtube.com में "dQw4w9WgXcQ" Video ID है
VIDEO_ID = "qska-ybs8-9p8v-7umw-08g0"

seen_users = set()

def clear_welcome_text():
    with open("welcome.txt", "w", encoding="utf-8") as f:
        f.write("")

def chat_listener():
    clear_welcome_text()
    while True:
        try:
            if VIDEO_ID == "YOUR_VIDEO_ID" or not VIDEO_ID:
                time.sleep(10)
                continue
            chat = pytchat.create(video_id=VIDEO_ID)
            while chat.is_alive():
                for c in chat.get().sync_items():
                    user = c.author.name
                    if user not in seen_users:
                        seen_users.add(user)
                        print(f"🎉 नया दर्शक जुड़ा: {user}")
                        with open("welcome.txt", "w", encoding="utf-8") as f:
                            f.write(f"Welcome {user}!")
                        time.sleep(8)  # 8 सेकंड तक स्क्रीन पर एनिमेशन दिखेगा
                        clear_welcome_text()
                time.sleep(1)
        except Exception as e:
            print(f"चैट लिसनर रीकनेक्ट हो रहा है: {e}")
            time.sleep(5)

def start_direct_challenge_live():
    video_file = "love_video.mp4"
    audio_file = "love_audio.mp3"
    
    STREAM_URL = "rtmp://a.rtmp.youtube.com/live2"
    STREAM_KEY = "qska-ybs8-9p8v-7umw-08g0"
    rtmp_url = f"{STREAM_URL}/{STREAM_KEY}"

    # बैकग्राउंड में चैट लिसनर शुरू करना
    threading.Thread(target=chat_listener, daemon=True).start()

    # वीडियो स्केलिंग और एनिमेटेड वेलकम ओवरले फ़िल्टर
    vf_filter = (
        "scale=1280:720,format=yuv420p,"
        "drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:"
        "textfile=welcome.txt:reload=1:fontcolor=yellow:fontsize=36:"
        "box=1:boxcolor=black@0.75:boxborderw=14:"
        "x=w-mod(t*180\\,w+tw):y=h-85"
    )

    command = [
        "ffmpeg", "-re",
        "-stream_loop", "-1", "-i", video_file,
        "-stream_loop", "-1", "-i", audio_file,
        "-vf", vf_filter,
        "-c:v", "libx264", "-preset", "ultrafast", "-b:v", "1500k",
        "-maxrate", "1500k", "-bufsize", "3000k", "-pix_fmt", "yuv420p",
        "-g", "48", "-c:a", "aac", "-b:a", "96k", "-ar", "44100",
        "-map", "0:v:0", "-map", "1:a:0",
        "-f", "flv", rtmp_url
    ]
    
    print("⚡ डायरेक्ट की बाईपास + चैट वेलकम एनिमेशन एक्टिव...")
    
    while True:
        try:
            subprocess.run(command, check=True)
        except Exception as e:
            print(f"कनेक्शन रीसेट हुआ: {e}। 3 सेकंड में दोबारा रीस्टार्ट...")
            time.sleep(3)

if __name__ == "__main__":
    start_direct_challenge_live()
