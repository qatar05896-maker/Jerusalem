# Venom
# Copyright (C) 2026 Abdullah (Venom). All Rights Reserved
# كود حديث 2026 - تحميل شامل وسريع بـ 8 خطوط مع دعم IPv4 و Node.js المتقدم

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
plugin_category = "البحث"
extractor = URLExtract()

# مسار مجلد التحميل المؤقت
TEMP_DIR = os.path.join(os.getcwd(), "repthon", "temp_downloads")
os.makedirs(TEMP_DIR, exist_ok=True)

# مسار ملف الكوكيز (يقوم بالبحث عنه في نفس مجلد الملف الحالي plugins)
COOKIES_PATH = os.path.join(os.path.dirname(__file__), "cookies.txt")

def get_ytdlp_options(is_audio=False):
    """إعدادات yt-dlp الحديثة مع الإضافات الاحترافية لتخطي حظر السيرفرات"""
    opts = {
        "format": "bestaudio/best" if is_audio else "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "outtmpl": os.path.join(TEMP_DIR, "%(title)s.%(ext)s"),
        "geo_bypass": True,
        "nocheckcertificate": True,
        "quiet": True,
        "no_warnings": True,
        "restrictfilenames": True,
        "windowsfilenames": True,
        
        # 1. إجبار السيرفر على استخدام IPv4 لتخطي حظر يوتيوب لشبكات IPv6
        "force_ipv4": True,
        "source_address": "0.0.0.0",
        
        # 2. تحديد بيئة Node.js الحديثة لفك تشفير جافاسكريبت يوتيوب
        "js_runtimes": {"node": {}},
        
        # 3. الاعتماد على المكونات الخارجية لتخطي التحديثات المفاجئة
        "remote_components": ["ejs:github"],
        
        # 4. استخدام عميل الويب (لتخطي حماية يوتيوب)
        "extractor_args": {
            "youtube": ["player_client=web,default"]
        },
        
        # 5. سحب 8 خطوط في نفس الوقت للتحميل الصاروخي المدمج بدون aria2
        "concurrent_fragment_downloads": 8,
        "http_chunk_size": 10485760, # تقسيم الملف 10 ميجا لكل خط
    }
    
    if is_audio:
        opts["postprocessors"] = [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "320",
        }]
    
    # 6. استخدام ملف الكوكيز من نفس الفولدر
    if os.path.exists(COOKIES_PATH):
        opts["cookiefile"] = COOKIES_PATH
    else:
        LOGS.warning(f"ملف الكوكيز (cookies.txt) غير موجود في المسار: {COOKIES_PATH}!")
        
    return opts

async def run_ytdlp(url, is_audio=False):
    """دالة لتشغيل التحميل في الخلفية لتجنب تجميد البوت"""
    def _download():
        with yt_dlp.YoutubeDL(get_ytdlp_options(is_audio)) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            if is_audio:
                filename = filename.rsplit(".", 1)[0] + ".mp3"
            return filename, info

    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _download)


# =========================================================
# دمج جميع أوامر الفيديو في كود واحد ذكي (يوتيوب، فيس، تيك توك، انستا، الخ)
# =========================================================
@zq_lo.rep_cmd(
    pattern="(تحميل فيديو|فيس|انستا|سناب|تيك|بنترست|فيسبوك)(?:\s|$)([\s\S]*)",
    command=("تحميل فيديو", plugin_category)
)
async def universal_video_downloader(event):
    """تحميل الفيديو مباشرة من أي موقع باستخدام yt-dlp المتطور"""
    msg = event.pattern_match.group(2)
    rmsg = await event.get_reply_message()
    if not msg and rmsg:
        msg = rmsg.text
        
    urls = extractor.find_urls(msg)
    if not urls:
        return await edit_or_reply(event, "**⎉╎قـم بإدخـال رابط أو الرد على رابط ليتم التحميل 🔗**")
        
    url = urls[0]
    zed = await edit_or_reply(event, "**╮ ❐ جـارِ جلب البيانات والتحميل (8 خطوط)... يرجى الانتظار 𓅫╰**")
    
    try:
        file_path, info = await run_ytdlp(url, is_audio=False)
        title = info.get("title", "فيديو بدون عنوان")
        
        await zed.edit(f"**╮ ❐ جـارِ الرفع للسيرفر... 𓅫╰**\n**المقطع:** `{title}`")
        
        await event.client.send_file(
            event.chat_id,
            file=file_path,
            caption=f"**⎉╎تـم التحميـل بنجاح ✅**\n**⎉╎العنوان:** `{title}`",
            reply_to=event.reply_to_msg_id or event.id,
            supports_streaming=True
        )
        await zed.delete()
        os.remove(file_path) # تنظيف السيرفر
        
    except yt_dlp.utils.DownloadError as e:
        error_msg = str(e)
        if "Sign in" in error_msg or "verify" in error_msg.lower():
            await zed.edit("**⎉╎يوتيوب يطلب تسجيل الدخول. يرجى التأكد من تحديث وصلاحية ملف `cookies.txt` ⚠️**")
        else:
            await zed.edit(f"**⎉╎حدث خطأ أثناء التحميل:**\n`{error_msg[:150]}...`")
    except Exception as e:
        await zed.edit(f"**⎉╎حدث خطأ غير متوقع:**\n`{e}`")


# =========================================================
# دمج أوامر الصوت
# =========================================================
@zq_lo.rep_cmd(
    pattern="(تحميل صوت|ساوند)(?:\s|$)([\s\S]*)",
    command=("تحميل صوت", plugin_category)
)
async def universal_audio_downloader(event):
    """تحميل الصوتيات كـ MP3 من أي موقع"""
    msg = event.pattern_match.group(2)
    rmsg = await event.get_reply_message()
    if not msg and rmsg:
        msg = rmsg.text
        
    urls = extractor.find_urls(msg)
    if not urls:
        return await edit_or_reply(event, "**⎉╎قـم بإدخـال رابط أو الرد على رابط ليتم التحميل 🔗**")
        
    url = urls[0]
    zed = await edit_or_reply(event, "**╮ ❐ جـارِ استخراج الصوت وتحميله... 𓅫╰**")
    
    try:
        file_path, info = await run_ytdlp(url, is_audio=True)
        title = info.get("title", "مقطع صوتي")
        uploader = info.get("uploader", "Venom")
        duration = info.get("duration", 0)
        
        await zed.edit(f"**╮ ❐ جـارِ الرفع للسيرفر... 𓅫╰**\n**المقطع:** `{title}`")
        
        # إرسال كملف صوتي منظم
        audio_attr = types.DocumentAttributeAudio(
            duration=duration,
            title=title,
            performer=uploader
        )
        
        await event.client.send_file(
            event.chat_id,
            file=file_path,
            attributes=[audio_attr],
            caption=f"**⎉╎تـم التحميـل بنجاح 🎧**\n**⎉╎العنوان:** `{title}`",
            reply_to=event.reply_to_msg_id or event.id,
        )
        await zed.delete()
        os.remove(file_path)
        
    except Exception as e:
        await zed.edit(f"**⎉╎حدث خطأ أثناء التحميل:**\n`{str(e)[:150]}...`")


# =========================================================
# أداة البحث المباشر في يوتيوب
# =========================================================
@zq_lo.rep_cmd(
    pattern="يوتيوب(?: |$)(\d*)? ?([\s\S]*)",
    command=("يوتيوب", plugin_category)
)
async def yt_search(event):
    """البحث المباشر واستخراج الروابط"""
    if event.is_reply and not event.pattern_match.group(2):
        query = (await event.get_reply_message()).text
    else:
        query = event.pattern_match.group(2)
        
    if not query:
        return await edit_or_reply(event, "**╮ بالـرد ﮼؏ كلمـٓھہ للبحث أو ضعها مـع الأمـر ... 𓅫╰**")
        
    limit = int(event.pattern_match.group(1)) if event.pattern_match.group(1) else 5
    if limit <= 0: limit = 5
    
    zed = await edit_or_reply(event, "**╮ جـارِ البحث في يوتيوب ▬▭... ╰**")
    
    def _search():
        opts = {"extract_flat": True, "force_generic_extractor": True, "quiet": True}
        
        # الإضافات هنا أيضاً للبحث بسلاسة أكبر
        opts["force_ipv4"] = True
        opts["source_address"] = "0.0.0.0"
        
        if os.path.exists(COOKIES_PATH): 
            opts["cookiefile"] = COOKIES_PATH
        
        with yt_dlp.YoutubeDL(opts) as ydl:
            return ydl.extract_info(f"ytsearch{limit}:{query}", download=False)
            
    try:
        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(None, _search)
        
        if not results or "entries" not in results or not results["entries"]:
            return await zed.edit("**⎉╎لم يتم العثور على نتائج لهذه الكلمة ⚠️**")
            
        reply_text = f"**⎉╎نتائج البحث عن:** `{query}`\n\n"
        for i, entry in enumerate(results["entries"], 1):
            title = entry.get("title", "بدون عنوان")
            url = entry.get("url") or entry.get("webpage_url", "")
            reply_text += f"**{i}-** [{title}]({url})\n"
            
        await zed.edit(reply_text, link_preview=False)
        
    except Exception as e:
        await zed.edit(f"**⎉╎حدث خطأ أثناء البحث:**\n`{e}`")
