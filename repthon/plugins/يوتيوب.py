# Venom Userbot
# Copyright (C) 2026 Abdullah (Venom). All Rights Reserved
# الـمـالـك: @S_G0C7
# كـود الـتـحـمـيـل الـشـامـل والـمـطـور - إصـدار 2026 الـحـصـري

import asyncio
import os
import time
from telethon.tl import types
import yt_dlp
from urlextract import URLExtract

from ..Config import Config
from ..core.logger import logging
from ..core.managers import edit_delete, edit_or_reply
from . import zq_lo

LOGS = logging.getLogger("𝙑𝙚𝙣𝙤𝙢")
plugin_category = "الـبـحـث"
extractor = URLExtract()

# تـحـديـد مـسـارات الـعـمـل بـشـكـل مـطـلـق لـتـفـادي مـشـاكـل Fly.io
TEMP_DIR = os.path.join(os.getcwd(), "repthon", "temp_downloads")
os.makedirs(TEMP_DIR, exist_ok=True)

# الـمـسـار الـمـطـلـق لـلـكـوكـيـز كـمـا نـجـح فـي الـتـيـرمـنـال بـالـضـبـط
COOKIES_PATH = "/root/repthon/repthon/plugins/cookies.txt"

def get_ytdlp_options(is_audio=False):
    """إعـدادات الـتـحـمـيـل الـقـصـوى بـنـاءً عـلـى تـجـارب الـكـونـسـول الـنـاجـحـة"""
    opts = {
        "format": "bestaudio/best" if is_audio else "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "outtmpl": os.path.join(TEMP_DIR, "%(title)s.%(ext)s"),
        "geo_bypass": True,
        "nocheckcertificate": True,
        "quiet": True,
        "no_warnings": True,
        "restrictfilenames": True,
        "windowsfilenames": True,
        
        # تـخـطـي حـظـر الـسـيـرفـرات (IPv4 حصراً)
        "force_ipv4": True,
        "source_address": "0.0.0.0",
        
        # تـصـحـيـح طـريـقـة إرسـال الـعـمـيـل فـي بـايـثـون لـيـقـرأهـا yt-dlp بـنـجـاح
        "extractor_args": {
            "youtube": {"player_client": ["web"]}
        },
        
        # فـرض اسـتـخـدام نـود لـفـك الـتـشـفـيـر والـتـحـديـات
        "js_runtime": "node",
        "remote_components": "ejs:github",
        
        # الـتـحـمـيـل الـمـتـوازي الـصـاروخـي (8 خـطـوط)
        "concurrent_fragment_downloads": 8,
        "http_chunk_size": 10485760, # 10 مـيـجـا لـكـل خـط لـتـسـريـع الـتـجـمـيـع
    }
    
    if is_audio:
        opts["postprocessors"] = [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "320",
        }]
    
    # قـراءة مـلـف الـكـوكـيـز لـتـخـطـي حـظـر "Sign in"
    if os.path.exists(COOKIES_PATH):
        opts["cookiefile"] = COOKIES_PATH
    else:
        LOGS.warning(f"⚠️ مـلـف الـكـوكـيـز غـيـر مـوجـود فـي: {COOKIES_PATH}")
        
    return opts

async def run_ytdlp(url, is_audio=False):
    """تـنـفـيـذ الـتـحـمـيـل فـي الـخـلـفـيـة لـتـسـريـع اسـتـجـابـة الـبـوت"""
    def _download():
        with yt_dlp.YoutubeDL(get_ytdlp_options(is_audio)) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            if is_audio:
                # تـحـديـد الامـتـداد الـجـديـد بـعـد الـمـعـالـجـة لـلـصـوت
                filename = filename.rsplit(".", 1)[0] + ".mp3"
            return filename, info

    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _download)


# =========================================================
# أوامــر تـحـمـيـل الـفـيـديـو
# =========================================================
@zq_lo.rep_cmd(
    pattern="(تحميل فيديو|فيس|انستا|سناب|تيك|بنترست|فيسبوك)(?:\s|$)([\s\S]*)",
    command=("تـحـمـيـل فـي_ديـو", plugin_category)
)
async def universal_video_downloader(event):
    msg = event.pattern_match.group(2)
    rmsg = await event.get_reply_message()
    if not msg and rmsg:
        msg = rmsg.text
        
    urls = extractor.find_urls(msg)
    if not urls:
        return await edit_or_reply(event, "**⤶ يـرجـى وضـع رابـط صـحـيـح لـلـتـحـمـيـل 🔗**")
        
    url = urls[0]
    zed = await edit_or_reply(event, "**⪼ جـارِ جـلـب الـبـيـانـات والـتـحـمـيـل بـنـظـام 8 خـطـوط ...**")
    
    try:
        file_path, info = await run_ytdlp(url, is_audio=False)
        title = info.get("title", "فـيـديـو")
        
        await zed.edit(f"**⪼ جـارِ رفـع الـمـقـطـع لـلـتـيـلـيـجـرام ...**\n**الـمـقـطـع ↶** `{title}`")
        
        await event.client.send_file(
            event.chat_id,
            file=file_path,
            caption=f"**• تـم الـتـحـمـيـل بـنـجـاح ✅**\n**• الـعـنـوان ↶** `{title}`\n**• الـمـالـك ↶ @S_G0C7**",
            reply_to=event.reply_to_msg_id or event.id,
            supports_streaming=True
        )
        await zed.delete()
        if os.path.exists(file_path): os.remove(file_path)
        
    except Exception as e:
        error_msg = str(e)
        if "Sign in" in error_msg:
            await zed.edit("**⤶ عـذراً، يـوتـيـوب يـطـلـب تـحـديـث مـلـف الـكـوكـيـز ⚠️**")
        else:
            await zed.edit(f"**⤶ حـدث خـطـأ أثـنـاء الـتـحـمـيـل ↶**\n`{error_msg[:150]}`")


# =========================================================
# أوامــر تـحـمـيـل الـصـوت (MP3)
# =========================================================
@zq_lo.rep_cmd(
    pattern="(تحميل صوت|ساوند)(?:\s|$)([\s\S]*)",
    command=("تـحـمـيـل صـوت", plugin_category)
)
async def universal_audio_downloader(event):
    msg = event.pattern_match.group(2)
    rmsg = await event.get_reply_message()
    if not msg and rmsg:
        msg = rmsg.text
        
    urls = extractor.find_urls(msg)
    if not urls:
        return await edit_or_reply(event, "**⤶ يـرجـى وضـع رابـط صـحـيـح لـلـتـحـمـيـل 🔗**")
        
    url = urls[0]
    zed = await edit_or_reply(event, "**⪼ جـارِ اسـتـخـراج الـصـوت والـتـحـمـيـل ...**")
    
    try:
        file_path, info = await run_ytdlp(url, is_audio=True)
        title = info.get("title", "مـقـطـع صـوتـي")
        duration = info.get("duration", 0)
        
        await zed.edit(f"**⪼ جـارِ رفـع الـمـلـف الـصـوتـي ...**\n**الـمـلـف ↶** `{title}`")
        
        audio_attr = types.DocumentAttributeAudio(
            duration=duration,
            title=title,
            performer="Venom"
        )
        
        await event.client.send_file(
            event.chat_id,
            file=file_path,
            attributes=[audio_attr],
            caption=f"**• تـم الـتـحـمـيـل بـنـجـاح 🎧**\n**• الـعـنـوان ↶** `{title}`\n**• الـمـالـك ↶ @S_G0C7**",
            reply_to=event.reply_to_msg_id or event.id,
        )
        await zed.delete()
        if os.path.exists(file_path): os.remove(file_path)
        
    except Exception as e:
        await zed.edit(f"**⤶ حـدث خـطـأ أثـنـاء الـتـحـمـيـل ↶**\n`{str(e)[:150]}`")


# =========================================================
# أداة الـبـحـث فـي يـوتـيـوب
# =========================================================
@zq_lo.rep_cmd(
    pattern="يوتيوب(?: |$)(\d*)? ?([\s\S]*)",
    command=("يـوتـيـوب", plugin_category)
)
async def yt_search(event):
    query = event.pattern_match.group(2) or (await event.get_reply_message() and (await event.get_reply_message()).text)
        
    if not query:
        return await edit_or_reply(event, "**⤶ يـرجـى كـتـابـة كـلـمـة لـلـبـحث أو الـرد عـلـى نـص**")
        
    limit = int(event.pattern_match.group(1)) if event.pattern_match.group(1) else 5
    zed = await edit_or_reply(event, "**⪼ جـارِ الـبـحـث فـي يـوتـيـوب ...**")
    
    def _search():
        opts = {
            "extract_flat": True, "quiet": True, "force_ipv4": True, "source_address": "0.0.0.0"
        }
        if os.path.exists(COOKIES_PATH): opts["cookiefile"] = COOKIES_PATH
        with yt_dlp.YoutubeDL(opts) as ydl:
            return ydl.extract_info(f"ytsearch{limit}:{query}", download=False)
            
    try:
        results = await asyncio.get_event_loop().run_in_executor(None, _search)
        if not results.get("entries"):
            return await zed.edit("**⤶ لـم يـتـم الـعـثـور عـلـى نـتـائـج ⚠️**")
            
        reply_text = f"**• نـتـائـج الـبـحـث عـن ↶** `{query}`\n\n"
        for i, entry in enumerate(results["entries"], 1):
            url = entry.get("url") or entry.get("webpage_url", "")
            reply_text += f"**{i}-** [{entry.get('title')}]( {url} )\n"
            
        await zed.edit(reply_text, link_preview=False)
    except Exception as e:
        await zed.edit(f"**⤶ حـدث خـطـأ أثـنـاء الـبـحـث ↶**\n`{e}`")
