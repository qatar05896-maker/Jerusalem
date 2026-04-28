import re
import os
try:
    import enum
except ModuleNotFoundError:
    os.system("pip3 install enum")
    import enum
from enum import Enum

from requests.exceptions import MissingSchema
from requests.models import PreparedRequest
from ..utils import runcmd
from yt_dlp import YoutubeDL

class Stream(Enum):
    audio = 1
    video = 2

yt_regex_str = r"^((?:https?:)?\/\/)?((?:www|m)\.)?((?:youtube(-nocookie)?\.com|youtu.be))(\/(?:[\w\-]+\?v=|embed\/|v\/)?)([\w\-]+)(\S+)?$"
yt_regex = re.compile(yt_regex_str)

# مسار الكوكيز المطلق لتفادي الحظر
COOKIES_PATH = "/root/repthon/repthon/plugins/cookies.txt"

def check_url(url):
    prepared_request = PreparedRequest()
    try:
        prepared_request.prepare_url(url, None)
        return prepared_request.url
    except MissingSchema:
        return False

async def get_yt_stream_link(url, audio_only=False):
    # إضافة أوامر التخطي المتقدمة (العميل ويب + نود + الكوكيز)
    bypass_args = f'--extractor-args "youtube:player_client=web" --js-runtime node --remote-components "ejs:github" --force-ipv4'
    if os.path.exists(COOKIES_PATH):
        bypass_args = f'--cookies "{COOKIES_PATH}" {bypass_args}'
        
    if audio_only:
        return (
            await runcmd(f"yt-dlp {bypass_args} --no-warnings --geo-bypass -f bestaudio -g {url}")
        )[0]
    return (await runcmd(f"yt-dlp {bypass_args} --no-warnings --geo-bypass -f best -g {url}"))[0]

async def video_dl(url, title):
    path = f"temp/{title.replace(' ', '_')}.mp4"
    video_opts = {
        "format": "best",
        "addmetadata": True,
        "key": "FFmpegMetadata",
        "writethumbnail": False,
        "prefer_ffmpeg": True,
        "geo_bypass": True,
        "nocheckcertificate": True,
        "postprocessors": [
            {"key": "FFmpegVideoConvertor", "preferedformat": "mp4"},
            {"key": "FFmpegMetadata"},
        ],
        "outtmpl": path,
        "logtostderr": False,
        "quiet": True,
        # الإعدادات الذهبية المضافة لتخطي الحظر أثناء تحميل الفيديو
        "force_ipv4": True,
        "source_address": "0.0.0.0",
        "extractor_args": {"youtube": {"player_client": ["web"]}},
        "js_runtime": "node",
        "remote_components": "ejs:github",
    }
    
    if os.path.exists(COOKIES_PATH):
        video_opts["cookiefile"] = COOKIES_PATH

    with YoutubeDL(video_opts) as ytdl:
        ytdl.extract_info(url)
    return path
