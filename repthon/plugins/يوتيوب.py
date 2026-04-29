# Venom Userbot - @S_G0C7
# أوامــر الـبـحـث والـتـحـمـيـل (الـنـسـخـة الـشـامـلـة - 2026)

import os
import asyncio
from telethon.tl import types
from urlextract import URLExtract
from repthon import zq_lo
from ..core.managers import edit_delete, edit_or_reply
from ..helpers.utils import reply_id

# اسـتـدعـاء مـحـرك الـتـحـمـيـل الـخـلـفـي
from ..HSL.yt_api import YouTube

plugin_category = "utils"
extractor = URLExtract()

async def get_yt_url_from_query(query: str):
    """دالـة مـسـاعـدة لـتـحـويـل كـلـمـات الـبـحـث لـرابـط مـبـاشـر"""
    urls = extractor.find_urls(query)
    if urls:
        return urls[0]
    
    import yt_dlp
    from ..HSL.yt_api import COOKIES_PATH
    opts = {"extract_flat": True, "quiet": True, "noplaylist": True}
    if os.path.exists(COOKIES_PATH): opts["cookiefile"] = COOKIES_PATH
    
    def _search():
        with yt_dlp.YoutubeDL(opts) as ydl:
            return ydl.extract_info(f"ytsearch1:{query}", download=False)
            
    try:
        results = await asyncio.get_event_loop().run_in_executor(None, _search)
        if results and results.get("entries"):
            return results["entries"][0].get("url")
    except Exception:
        pass
    return None

@zq_lo.rep_cmd(
    pattern="(بحث|تحميل صوت|ساوند)(?: |$)(.*)",
    command=("بحث", plugin_category)
)
async def dl_audio_cmd(event):
    """الـبـحـث عـن الـصـوتـيـات وتـحـمـيـلـهـا"""
    msg = event.pattern_match.group(2)
    rmsg = await event.get_reply_message()
    if not msg and rmsg: msg = rmsg.text
    if not msg: return await edit_or_reply(event, "**⤶ يـرجـى كـتـابـة اسـم الـأغـنـيـة أو إدراج رابـط 🔗**")

    zed = await edit_or_reply(event, "**⪼ جـارِ الـبـحـث والـتـحـمـيـل (صـوت) ... 🎧**")
    url = await get_yt_url_from_query(msg)
    if not url: return await zed.edit(f"**⤶ لـم أسـتـطـع إيـجـاد:** `{msg}`")

    file_path, info = await YouTube.download(url, is_video=False)
    if file_path:
        await zed.edit("**⪼ جـارِ رفـع الـمـلـف ...**")
        audio_attr = types.DocumentAttributeAudio(
            duration=int(info.get('duration', 0)),
            title=info.get('title'),
            performer="Venom"
        )
        await event.client.send_file(
            event.chat_id, file=file_path, attributes=[audio_attr],
            caption=f"**• تـم الـتـحـمـيـل بـنـجـاح ✅**\n**• الـعـنـوان ↶** `{info.get('title')}`",
            reply_to=await reply_id(event)
        )
        await zed.delete()
        if os.path.exists(file_path): os.remove(file_path)
    else:
        await zed.edit("**⤶ فـشـل الـتـحـمـيـل، يـرجـى الـتـأكـد مـن صـلاحـيـة الـرابـط.**")

@zq_lo.rep_cmd(
    pattern="(فيديو|تحميل فيديو|فيس|انستا|تيك)(?: |$)(.*)",
    command=("فيديو", plugin_category)
)
async def dl_video_cmd(event):
    """الـبـحـث عـن مـقـاطـع الـفـيـديـو وتـحـمـيـلـهـا"""
    msg = event.pattern_match.group(2)
    rmsg = await event.get_reply_message()
    if not msg and rmsg: msg = rmsg.text
    if not msg: return await edit_or_reply(event, "**⤶ يـرجـى كـتـابـة اسـم الـفـيـديـو أو إدراج رابـط 🔗**")

    zed = await edit_or_reply(event, "**⪼ جـارِ الـبـحـث والـتـحـمـيـل (فـيـديـو) ... 🎬**")
    url = await get_yt_url_from_query(msg)
    if not url: return await zed.edit(f"**⤶ لـم أسـتـطـع إيـجـاد:** `{msg}`")

    file_path, info = await YouTube.download(url, is_video=True)
    if file_path:
        await zed.edit("**⪼ جـارِ رفـع الـمـلـف بـنـظـام الـخـطـوط الـ 8 ...**")
        await event.client.send_file(
            event.chat_id, file=file_path, supports_streaming=True,
            caption=f"**• تـم الـتـحـمـيـل بـنـجـاح ✅**\n**• الـعـنـوان ↶** `{info.get('title')}`",
            reply_to=await reply_id(event)
        )
        await zed.delete()
        if os.path.exists(file_path): os.remove(file_path)
    else:
        await zed.edit("**⤶ فـشـل الـتـحـمـيـل، تـأكـد مـن الـرابـط.**")
