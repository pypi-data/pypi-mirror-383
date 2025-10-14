import subprocess
import sys
import threading
import itertools
import time
import os
import importlib.util

def spinner(msg):
    for c in itertools.cycle('|/-\\'):
        if done:
            break
        sys.stdout.write(f'\r{msg} {c}')
        sys.stdout.flush()
        time.sleep(0.1)
    sys.stdout.write('\r' + ' ' * (len(msg) + 2) + '\r')

def install_dependencies():
    global done
    done = False
    t = threading.Thread(target=spinner, args=('📦 Installing dependencies...',))
    t.start()
    try:
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "-U", "yt-dlp", "tqdm", "colorama"], check=True)
        except subprocess.CalledProcessError:
            subprocess.run([sys.executable, "-m", "pip", "install", "-U", "git+https://github.com/yt-dlp/yt-dlp.git"], check=True)
    finally:
        done = True
        t.join()
    print("✅ Dependencies ready.\n")

def check_imports():
    for pkg in ["yt_dlp", "tqdm", "colorama"]:
        if importlib.util.find_spec(pkg) is None:
            install_dependencies()
            break

check_imports()

from yt_dlp import YoutubeDL
from colorama import Fore, Style
from tqdm import tqdm
import datetime

print(Fore.CYAN + "🎬 bjtube - YouTube Downloader by Babar Ali Jamali")
print("-" * 50 + Style.RESET_ALL)

url = input("📺 Enter YouTube video URL: ").strip()
if not url:
    sys.exit("❌ No URL provided!")

opts = {
    'outtmpl': '%(title)s - %(release_date>%Y%m%d)s.%(ext)s',
    'progress_hooks': [lambda d: tqdm.write(f"{d['_percent_str']} {d['_eta_str']}") if d['status'] == 'downloading' else None],
}

with YoutubeDL(opts) as ydl:
    ydl.download([url])

print(Fore.GREEN + "\n✅ Download complete!" + Style.RESET_ALL)
