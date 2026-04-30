# Venom Userbot
# Copyright (C) 2026 Abdullah (Venom). All Rights Reserved
# الـمـالـك: @S_G0C7
# محرك المكالمات والتشغيل (إصدار المجلد المخصص Pluginsme) | Modern Python 3.11+

import asyncio
import os
from pathlib import Path
from typing import Optional, Tuple

import yt_dlp
from urlextract import URLExtract

from repthon import zq_lo
# === الاستدعاءات المباشرة لضمان العمل من داخل Pluginsme ===
from repthon.core.managers import edit_delete, edit_or_reply
from repthon.helpers.utils import reply_id
from repthon.HSL.call_engine import CallEngine

# ==========================================
# 0. الإعدادات الحديثة
# ==========================================
plugin_category = "utils"
extractor = URLExtract()

# مسارات الملفات
COOKIES_PATH = Path("repthon/plugins/cookies.txt")
TEMP_DIR = Path("temp")
TEMP_DIR.mkdir(parents=True, exist_ok=True)

# تـهـيـئـة الـمـحـرك
VC = CallEngine(zq_lo)
zq_lo.loop.create_task(VC.start())

# ==========================================
# 1. دوال البحث والذكاء الاصطناعي
# ==========================================

async def get_stream_info(query: str) -> Tuple[Optional[str], Optional[str]]:
    """دالة ذكية لجلب روابط البث باستخدام asyncio.to_thread الحديثة"""
    if urls := extractor.find_urls(query):
        return urls[0], "مـقـطـع مـن رابـط مـبـاشـر"
    
    opts = {
        "extract_flat": True, 
        "quiet": True, 
        "noplaylist": True,
        "cookiefile": str(COOKIES_PATH) if COOKIES_PATH.exists() else None
    }
    
    def _search():
        with yt_dlp.YoutubeDL(opts) as ydl:
            return ydl.extract_info(f"ytsearch1:{query}", download=False)
            
    try:
        results = await asyncio.to_thread(_search)
        if results and (entries := results.get("entries")):
            return entries[0].get("url"), entries[0].get("title")
    except Exception:
        pass
    return None, None

# ==========================================
# 2. أوامر التشغيل المباشرة (تدعم الملفات)
# ==========================================

@zq_lo.rep_cmd(pattern="شغل(?: |$)(.*)")
async def play_audio_cmd(event):
    """تـشـغـيـل صـوتـي فـي الـمـكـالـمـة مـن بـحـث يـوتـيـوب أو مـلـف مـحـلـي"""
    reply = await event.get_reply_message()
    query = event.pattern_match.group(1).strip()
    
    zed = await edit_or_reply(event, "**⪼ جـارِ الـمـعـالـجـة والـتـشـغـيـل ... 🎧**")
    
    # 1. التحقق من وجود ملف صوتي في الرد
    if reply and reply.media and hasattr(reply.media, 'document'):
        if "audio" in reply.file.mime_type or "ogg" in reply.file.mime_type:
            await zed.edit("**⪼ جـارِ تـنـزيـل الـمـلـف الـصـوتـي لـرفـعـه لـلـمـكـالـمـة ... ⏳**")
            file_path = await reply.download_media(str(TEMP_DIR))
            title = reply.file.name or "مـقـطـع صـوتـي (مـلـف)"
            res = await VC.play_or_queue(event.chat_id, file_path, title, is_video=False)
            return await zed.edit(f"{res}\n**• الـمـالـك ↶ @S_G0C7**")

    # 2. إذا لم يكن ملفاً، يتم البحث كنص
    query = query or (reply.text if reply else "")
    if not query:
        return await zed.edit("**⤶ يـرجـى كـتـابـة اسـم الـأغـنـيـة، إدراج رابـط، أو الـرد عـلـى مـلـف صـوتـي 𓆰.**")

    url, title = await get_stream_info(query)
    if not url:
        return await zed.edit(f"**⤶ لـم أسـتـطـع إيـجـاد:** `{query}`")

    res = await VC.play_or_queue(event.chat_id, url, title, is_video=False)
    await zed.edit(f"{res}\n**• الـمـالـك ↶ @S_G0C7**")


@zq_lo.rep_cmd(pattern="فيد(?: |$)(.*)")
async def play_video_cmd(event):
    """تـشـغـيـل فـيـديـو فـي الـمـكـالـمـة مـن بـحـث يـوتـيـوب أو مـلـف مـحـلـي"""
    reply = await event.get_reply_message()
    query = event.pattern_match.group(1).strip()

    zed = await edit_or_reply(event, "**⪼ جـارِ تـجـهـيـز بـث الـفـيـديـو ... 🎬**")
    
    # 1. التحقق من وجود فيديو في الرد
    if reply and reply.media and hasattr(reply.media, 'document'):
        if "video" in reply.file.mime_type:
            await zed.edit("**⪼ جـارِ تـنـزيـل الـفـيـديـو لـرفـعـه لـلـمـكـالـمـة ... ⏳**")
            file_path = await reply.download_media(str(TEMP_DIR))
            title = reply.file.name or "مـقـطـع فـيـديـو (مـلـف)"
            res = await VC.play_or_queue(event.chat_id, file_path, title, is_video=True)
            return await zed.edit(f"{res}\n**• الـمـالـك ↶ @S_G0C7**")

    # 2. البحث النصي
    query = query or (reply.text if reply else "")
    if not query:
        return await zed.edit("**⤶ يـرجـى كـتـابـة اسـم الـفـيـديـو، إدراج رابـط، أو الـرد عـلـى مـلـف فـيـديـو 𓆰.**")
    
    url, title = await get_stream_info(query)
    if not url:
        return await zed.edit(f"**⤶ لـم أسـتـطـع إيـجـاد:** `{query}`")

    res = await VC.play_or_queue(event.chat_id, url, title, is_video=True)
    await zed.edit(f"{res}\n**• الـمـالـك ↶ @S_G0C7**")

# ==========================================
# 3. أوامر التحكم في المكالمة
# ==========================================

@zq_lo.rep_cmd(pattern="توقف(?: |$)(.*)")
async def pause_cmd(event):
    """إيـقـاف الـبـث مـؤقـتـاً"""
    await VC.pause(event.chat_id)
    await edit_delete(event, "**⤶ تـم إيـقـاف الـتـشـغـيـل مـؤقـتـاً ⏸**")


@zq_lo.rep_cmd(pattern="كمل(?: |$)(.*)")
async def resume_cmd(event):
    """اسـتـئـنـاف الـبـث مـن جـديـد"""
    await VC.resume(event.chat_id)
    await edit_delete(event, "**⤶ تـم اسـتـئـنـاف الـتـشـغـيـل ▶️**")


@zq_lo.rep_cmd(pattern="تخطي(?: |$)(.*)")
async def skip_cmd(event):
    """تـخـطـي الـمـقـطـع الـحـالـي لـلـمـقـطـع الـتـالـي"""
    res = await VC.skip(event.chat_id)
    await edit_or_reply(event, res)


@zq_lo.rep_cmd(pattern="خروج(?: |$)(.*)")
async def leave_cmd(event):
    """إنـهـاء الـمـكـالـمـة والـمـغـادرة"""
    await VC.stop(event.chat_id)
    await edit_delete(event, "**⤶ تـم إيـقـاف الـبـث ومـغـادرة الـمـكـالـمـة بـنـجـاح 🚪**")


@zq_lo.rep_cmd(pattern="قائمة(?: |$)(.*)")
async def list_cmd(event):
    """عـرض قـائـمـة الـمـقـاطـع فـي الانـتـظـار"""
    if not (playlist := VC.get_playlist(event.chat_id)):
        return await edit_delete(event, "**⤶ الـطـابـور فـارغ حـالـيـاً 📭**")
    
    msg = "**• قـائـمـة الـتـشـغـيـل الـحـالـيـة ↶**\n\n"
    msg += "".join(
        f"**{i}-** `{track['title']}` - ({'يـعـمـل الـآن 🔊' if i == 1 else 'فـي الـانـتـظـار ⏳'})\n"
        for i, track in enumerate(playlist, 1)
    )
    
    await edit_or_reply(event, msg)
