import os
import time
import subprocess
import threading
import pytchat

# आपके चैनल का हैंडल और कूलडाउन समय (3600 सेकंड = 1 घंटा)
CHANNEL_HANDLE = "@Talkto-urs"
COOLDOWN_SECONDS = 3600  

last_welcomed = {}

def set_welcome_text(msg):
    with open("welcome.txt", "w", encoding="utf-8") as f:
        f.write(msg)

def get_live_video_id():
    try:
        cmd = [
            "yt-dlp", "--get-id", "--playlist-items", "1",
            f"https://youtube.com{CHANNEL_HANDLE}/live"
        ]
        res = subprocess.check_output(cmd, stderr=subprocess.STDOUT).decode().strip().splitlines()
        for line in res:
            if len(line.strip()) == 11:
                return line.strip()
    except Exception as e:
        print(f"Video ID खोजने में समस्या: {e}")
    return None

def chat_listener():
    # सबसे पहले 15 सेकंड तक टेस्ट एनिमेशन दिखाएगा ताकि आप कन्फर्म कर सकें
    set_welcome_text("Welcome to Live Stream!")
    time.sleep(15)
    set_welcome_text("")

    while True:
        try:
            vid_id = get_live_video_id()
            if not vid_id:
                print("⏳ लाइव स्ट्रीम ID का इंतज़ार हो रहा है (10 सेकंड)...")
                time.sleep(10)
                continue

            print(f"✅ लाइव चैट से जुड़ गया! Video ID: {vid_id}")
            chat = pytchat.create(video_id=vid_id)
            
            # शुरू के पुराने चैट बफर को खाली करना ताकि पुराने मैसेज पर एनिमेशन न आए
            time.sleep(3)
            if chat.is_alive():
                chat.get()

            while chat.is_alive():
                for c in chat.get().sync_items():
                    user = c.author.name
                    now = time.time()
                    prev_time = last_welcomed.get(user, 0)
                    
                    print(f"💬 चैट मैसेज: {user}: {c.message}")
                    
                    # यदि यूजर नया है या 1 घंटे (3600 सेकंड) बाद वापस आया है
                    if (now - prev_time) >= COOLDOWN_SECONDS:
                        last_welcomed[user] = now
                        label = f"Welcome {user}!" if prev_time == 0 else f"Welcome Back {user}!"
                        print(f"🎉 स्क्रीन पर एनिमेशन दिखाया जा रहा है: {label}")
                        set_welcome_text(label)
                        time.sleep(8)
                        set_welcome_text("")
                time.sleep(1)
        except Exception as e:
            print(f"⚠️ चैट लिसनर रीकनेक्ट हो रहा है: {e}")
            time.sleep(5)

def start_direct_challenge_live():
    video_file = "love_video.mp4"
    audio_file = "love_audio.mp3"
    
    STREAM_URL = "rtmp://a.rtmp.youtube.com/live2"
    STREAM_KEY = "qska-ybs8-9p8v-7umw-08g0"
    rtmp_url = f"{STREAM_URL}/{STREAM_KEY}"

    set_welcome_text("")
    threading.Thread(target=chat_listener, daemon=True).start()

    # स्लाइडिंग एनिमेशन फ़िल्टर
    vf_filter = (
        "scale=1280:720,format=yuv420p,"
        "drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:"
        "textfile=welcome.txt:reload=1:fontcolor=yellow:fontsize=40:"
        "box=1:boxcolor=black@0.8:boxborderw=15:"
        "x=w-mod(t*190\\,w+tw):y=h-90"
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
    
    print("⚡ 24/7 लाइव स्ट्रीम + वेलकम एनिमेशन शुरू...")
    
    while True:
        try:
            subprocess.run(command, check=True)
        except Exception as e:
            print(f"कनेक्शन रीसेट हुआ: {e}। 3 सेकंड में दोबारा रीस्टार्ट...")
            time.sleep(3)

if __name__ == "__main__":
    start_direct_challenge_live()
