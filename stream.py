import os
import time
import subprocess
import threading
import json

# आपके चैनल का हैंडल और कूलडाउन समय (3600 सेकंड = 1 घंटा)
CHANNEL_HANDLE = "@Talkto-urs"
COOLDOWN_SECONDS = 3600  

last_welcomed = {}  # यूजर का आखिरी वेलकम टाइम सेव करने के लिए
start_timestamp = time.time()  # स्क्रिप्ट शुरू होने का समय

def clear_welcome_text():
    with open("welcome.txt", "w", encoding="utf-8") as f:
        f.write("")

def get_live_video_id():
    try:
        cmd = [
            "yt-dlp", "--get-id", "--playlist-items", "1",
            f"https://youtube.com{CHANNEL_HANDLE}/live"
        ]
        res = subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode().strip()
        if len(res) == 11:
            return res
    except Exception:
        pass
    return None

def chat_listener():
    clear_welcome_text()
    while True:
        try:
            vid_id = get_live_video_id()
            if not vid_id:
                time.sleep(10)
                continue

            print(f"✅ लाइव चैट से जुड़ गया (ID: {vid_id})")
            chat_file = "chat_temp.live_chat.json"
            if os.path.exists(chat_file):
                os.remove(chat_file)

            chat_cmd = [
                "yt-dlp", "--skip-download", "--write-subs", "--sub-langs", "live_chat",
                "--output", "chat_temp", f"https://youtube.comwatch?v={vid_id}"
            ]
            proc = subprocess.Popen(chat_cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
            
            last_pos = 0
            initial_skip_done = False

            while proc.poll() is None:
                if os.path.exists(chat_file):
                    with open(chat_file, "r", encoding="utf-8") as f:
                        f.seek(last_pos)
                        lines = f.readlines()
                        last_pos = f.tell()

                        # शुरू के 5 सेकंड में पुराने लोड हुए चैट मैसेज को स्किप करना
                        if not initial_skip_done and (time.time() - start_timestamp) < 8:
                            continue
                        initial_skip_done = True

                        for line in lines:
                            try:
                                data = json.loads(line)
                                actions = data.get("replayChatItemAction", {}).get("actions", [{}])
                                msg = actions[0].get("addChatItemAction", {}).get("item", {}).get("liveChatTextMessageRenderer", {})
                                user = msg.get("authorName", {}).get("simpleText")
                                
                                if user:
                                    now = time.time()
                                    prev_time = last_welcomed.get(user, 0)
                                    
                                    # यदि यूजर नया है या 1 घंटे (3600 सेकंड) बाद वापस आया है
                                    if (now - prev_time) >= COOLDOWN_SECONDS:
                                        last_welcomed[user] = now
                                        label = f"Welcome {user}!" if prev_time == 0 else f"Welcome Back {user}!"
                                        print(f"🎉 एनिमेशन चालू: {label}")
                                        with open("welcome.txt", "w", encoding="utf-8") as wf:
                                            wf.write(label)
                                        time.sleep(8)  # 8 सेकंड तक स्क्रीन पर एनिमेशन दिखेगा
                                        clear_welcome_text()
                            except Exception:
                                continue
                time.sleep(1)
        except Exception as e:
            print(f"चैट रीकनेक्ट हो रही है: {e}")
            time.sleep(5)

def start_direct_challenge_live():
    video_file = "love_video.mp4"
    audio_file = "love_audio.mp3"
    
    STREAM_URL = "rtmp://a.rtmp.youtube.com/live2"
    STREAM_KEY = "qska-ybs8-9p8v-7umw-08g0"
    rtmp_url = f"{STREAM_URL}/{STREAM_KEY}"

    # स्टार्ट होते ही 6 सेकंड का टेस्ट मैसेज दिखाएगा ताकि आप कन्फर्म कर सकें
    with open("welcome.txt", "w", encoding="utf-8") as f:
        f.write("Live Chat Ready!")

    threading.Thread(target=chat_listener, daemon=True).start()

    # स्लाइडिंग एनिमेशन फ़िल्टर (नीचे की तरफ सुनहरे अक्षर और काला बॉक्स)
    vf_filter = (
        "scale=1280:720,format=yuv420p,"
        "drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:"
        "textfile=welcome.txt:reload=1:fontcolor=yellow:fontsize=38:"
        "box=1:boxcolor=black@0.8:boxborderw=14:"
        "x=w-mod(t*190\\,w+tw):y=h-85"
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
    
    print("⚡ 24/7 लाइव स्ट्रीम + 1-घंटा कूलडाउन वेलकम एनिमेशन शुरू...")
    
    while True:
        try:
            subprocess.run(command, check=True)
        except Exception as e:
            print(f"कनेक्शन रीसेट हुआ: {e}। 3 सेकंड में दोबारा रीस्टार्ट...")
            time.sleep(3)

if __name__ == "__main__":
    start_direct_challenge_live()
