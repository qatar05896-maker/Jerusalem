# Venom Userbot - Call Controller (Web Client - Fixed 2026)
import asyncio
import os
from pathlib import Path
from typing import Optional, Tuple

import yt_dlp
from urlextract import URLExtract

from repthon import zq_lo
from repthon.core.managers import edit_delete, edit_or_reply
from repthon.helpers.utils import reply_id
from repthon.HSL.call_engine import CallEngine

# ==========================================
# 0. الإعدادات
# ==========================================
plugin_category = "utils"
extractor = URLExtract()

COOKIES_PATH = Path("/root/repthon/repthon/plugins/cookies.txt")
TEMP_DIR = Path("temp")
TEMP_DIR.mkdir(parents=True, exist_ok=True)

VC = CallEngine(zq_lo)
zq_lo.loop.create_task(VC.start())

# ==========================================
# 1. دالة جلب رابط البث (معدلة – عميل ويب نقي)
# ==========================================
async def get_stream_info(query: str, is_video: bool = False) -> Tuple[Optional[str], Optional[str]]:
    """ترجع (direct_url, title) من يوتيوب باستخدام عميل web فقط"""
    if urls := extractor.find_urls(query):
        search_query = urls[0]
    else:
        search_query = f"ytsearch1:{query}"

    # ✅ الصيغ نفس اللي في الملف الشغال: ba/b للصوت، b للفيديو
    fmt = "b" if is_video else "ba/b"

    opts = {
        "format": fmt,
        "quiet": True,
        "noplaylist": True,
        "no_warnings": True,
        "force_ipv4": True,
        "source_address": "0.0.0.0",
        "extractor_args": {"youtube": {"player_client": ["web"]}},
        "cookiefile": str(COOKIES_PATH) if COOKIES_PATH.exists() else None,
    }

    def _search():
        with yt_dlp.YoutubeDL(opts) as ydl:
            res = ydl.extract_info(search_query, download=False)
            if res:
                if 'entries' in res and res['entries']:
                    entry = res['entries'][0]
                else:
                    entry = res
                return entry.get("url"), entry.get("title")
            return None, None

    try:
        return await asyncio.to_thread(_search)
    except Exception as e:
        print(f"Stream Info Error: {e}")
        return None, None


# ==========================================
# 2. أوامر التشغيل
# ==========================================
@zq_lo.rep_cmd(pattern="شغل(?: |$)(.*)")
async def play_audio_cmd(event):
    """تشغيل صوت في المكالمة"""
    reply = await event.get_reply_message()
    query = event.pattern_match.group(1).strip()

    zed = await edit_or_reply(event, "**⪼ جارِ المعالجة والتشغيل ... 🎧**")

    # ملف صوتي في الرد
    if reply and reply.media and hasattr(reply.media, 'document'):
        if "audio" in reply.file.mime_type or "ogg" in reply.file.mime_type:
            await zed.edit("**⪼ جارِ تنزيل الملف الصوتي ... ⏳**")
            file_path = await reply.download_media(str(TEMP_DIR))
            title = reply.file.name or "مقطع صوتي (ملف)"
            res = await VC.play_or_queue(event.chat_id, file_path, title, is_video=False)
            return await zed.edit(f"{res}\n**• المالك ↶ @S_G0C7**")

    # بحث نصي
    query = query or (reply.text if reply else "")
    if not query:
        return await zed.edit("**⤶ يرجى كتابة اسم الأغنية، رابط، أو الرد على ملف صوتي.**")

    url, title = await get_stream_info(query, is_video=False)
    if not url:
        return await zed.edit(f"**⤶ لم أستطع العثور على: ** `{query}`")

    res = await VC.play_or_queue(event.chat_id, url, title, is_video=False)
    await zed.edit(f"{res}\n**• المالك ↶ @S_G0C7**")


@zq_lo.rep_cmd(pattern="فيد(?: |$)(.*)")
async def play_video_cmd(event):
    """تشغيل فيديو في المكالمة"""
    reply = await event.get_reply_message()
    query = event.pattern_match.group(1).strip()

    zed = await edit_or_reply(event, "**⪼ جارِ تجهيز بث الفيديو ... 🎬**")

    # ملف فيديو في الرد
    if reply and reply.media and hasattr(reply.media, 'document'):
        if "video" in reply.file.mime_type:
            await zed.edit("**⪼ جارِ تنزيل الفيديو ... ⏳**")
            file_path = await reply.download_media(str(TEMP_DIR))
            title = reply.file.name or "مقطع فيديو (ملف)"
            res = await VC.play_or_queue(event.chat_id, file_path, title, is_video=True)
            return await zed.edit(f"{res}\n**• المالك ↶ @S_G0C7**")

    # بحث نصي
    query = query or (reply.text if reply else "")
    if not query:
        return await zed.edit("**⤶ يرجى كتابة اسم الفيديو، رابط، أو الرد على ملف فيديو.**")

    url, title = await get_stream_info(query, is_video=True)
    if not url:
        return await zed.edit(f"**⤶ لم أستطع العثور على: ** `{query}`")

    res = await VC.play_or_queue(event.chat_id, url, title, is_video=True)
    await zed.edit(f"{res}\n**• المالك ↶ @S_G0C7**")


# ==========================================
# 3. أوامر التحكم
# ==========================================
@zq_lo.rep_cmd(pattern="توقف(?: |$)(.*)")
async def pause_cmd(event):
    await VC.pause(event.chat_id)
    await edit_delete(event, "**⤶ تم إيقاف التشغيل مؤقتاً ⏸**")

@zq_lo.rep_cmd(pattern="كمل(?: |$)(.*)")
async def resume_cmd(event):
    await VC.resume(event.chat_id)
    await edit_delete(event, "**⤶ تم استئناف التشغيل ▶️**")

@zq_lo.rep_cmd(pattern="تخطي(?: |$)(.*)")
async def skip_cmd(event):
    res = await VC.skip(event.chat_id)
    await edit_or_reply(event, res)

@zq_lo.rep_cmd(pattern="خروج(?: |$)(.*)")
async def leave_cmd(event):
    await VC.stop(event.chat_id)
    await edit_delete(event, "**⤶ تم إيقاف البث ومغادرة المكالمة 🚪**")

@zq_lo.rep_cmd(pattern="قائمة(?: |$)(.*)")
async def list_cmd(event):
    playlist = VC.get_playlist(event.chat_id)
    if not playlist:
        return await edit_delete(event, "**⤶ الطابور فارغ حالياً 📭**")

    msg = "**• قائمة التشغيل الحالية ↶**\n\n"
    msg += "".join(
        f"**{i}-** `{track['title']}` - ({'يعمل الآن 🔊' if i == 1 else 'في الانتظار ⏳'})\n"
        for i, track in enumerate(playlist, 1)
    )
    await edit_or_reply(event, msg)
