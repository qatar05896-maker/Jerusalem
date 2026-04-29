# Venom Userbot
# Copyright (C) 2026 Abdullah (Venom). All Rights Reserved
# الـمـالـك: @S_G0C7
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
    # لـو الـمـسـتـخـدم بـعـت رابـط مـبـاشـرة
    urls = extractor.find_urls(query)
    if urls:
        return urls[0]
    
    # لـو بـعـت كـلـمـة بـحـث، هـنـجـيـب أول نـتـيـجـة
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


@zq_lo.rep_cmd(pattern="(بحث|تحميل صوت|ساوند)(?: |$)(.*)")
async def dl_audio_cmd(event):
    """الـبـحـث عـن الـصـوتـيـات وتـحـمـيـلـهـا"""
    msg = event.pattern_match.group(2)
    rmsg = await event.get_reply_message()
    if not msg and rmsg:
        msg = rmsg.text
        
    if not msg:
        return await edit_or_reply(event, "**⤶ يـرجـى كـتـابـة اسـم الـأغـنـيـة أو إدراج رابـط 🔗**")

    zed = await edit_or_reply(event, "**⪼ جـارِ الـبـحـث والـتـحـمـيـل (صـوت) ... 🎧**")
    
    url = await get_yt_url_from_query(msg)
    if not url:
        return await zed.edit(f"**⤶ لـم أسـتـطـع إيـجـاد:** `{msg}`")

    file_path, info = await YouTube.download(url, is_video=False)
    
    if file_path:
        await zed.edit("**⪼ جـارِ رفـع الـمـلـف ...**")
        audio_attr = types.DocumentAttributeAudio(
            duration=int(info.get('duration', 0)),
            title=info.get('title'),
            performer="Venom"
        )
        await event.client.send_file(
            event.chat_id,
            file=file_path,
            attributes=[audio_attr],
            caption=f"**• تـم الـتـحـمـيـل بـنـجـاح 🎧**\n**• الـعـنـوان ↶** `{info.get('title')}`\n**• الـمـالـك ↶ @S_G0C7**",
            reply_to=await reply_id(event)
        )
        await zed.delete()
        if os.path.exists(file_path): os.remove(file_path)
    else:
        await zed.edit("**⤶ فـشـل الـتـحـمـيـل، يـرجـى الـتـأكـد مـن صـلاحـيـة الـرابـط.**")


@zq_lo.rep_cmd(pattern="(فيديو|تحميل فيديو|فيس|انستا|سناب|تيك)(?: |$)(.*)")
async def dl_video_cmd(event):
    """الـبـحـث عـن مـقـاطـع الـفـيـديـو وتـحـمـيـلـهـا"""
    msg = event.pattern_match.group(2)
    rmsg = await event.get_reply_message()
    if not msg and rmsg:
        msg = rmsg.text
        
    if not msg:
        return await edit_or_reply(event, "**⤶ يـرجـى كـتـابـة اسـم الـفـيـديـو أو إدراج رابـط 🔗**")

    zed = await edit_or_reply(event, "**⪼ جـارِ الـبـحـث والـتـحـمـيـل (فـيـديـو) ... 🎬**")
    
    url = await get_yt_url_from_query(msg)
    if not url:
        return await zed.edit(f"**⤶ لـم أسـتـطـع إيـجـاد:** `{msg}`")

    file_path, info = await YouTube.download(url, is_video=True)
    
    if file_path:
        await zed.edit("**⪼ جـارِ رفـع الـمـلـف بـنـظـام الـخـطـوط الـ 8 ...**")
        await event.client.send_file(
            event.chat_id,
            file=file_path,
            caption=f"**• تـم الـتـحـمـيـل بـنـجـاح ✅**\n**• الـعـنـوان ↶** `{info.get('title')}`\n**• الـمـالـك ↶ @S_G0C7**",
            supports_streaming=True,
            reply_to=await reply_id(event)
        )
        await zed.delete()
        if os.path.exists(file_path): os.remove(file_path)
    else:
        await zed.edit("**⤶ فـشـل الـتـحـمـيـل، يـرجـى الـتـأكـد مـن صـلاحـيـة الـرابـط أو الـكـوكـيـز.**")


@zq_lo.rep_cmd(pattern="يوتيوب(?: |$)(\d*)? ?([\s\S]*)")
async def yt_search_cmd(event):
    """الـبـحـث فـي يـوتـيـوب واسـتـخـراج الـروابـط فـقـط"""
    query = event.pattern_match.group(2)
    if not query and event.reply_to_msg_id:
        query = (await event.get_reply_message()).text
        
    if not query:
        return await edit_or_reply(event, "**⤶ يـرجـى كـتـابـة كـلـمـة لـلـبـحـث أو الـرد عـلـى نـص**")
        
    limit = int(event.pattern_match.group(1)) if event.pattern_match.group(1) else 5
    if limit <= 0: limit = 5
    
    zed = await edit_or_reply(event, "**⪼ جـارِ الـبـحـث فـي يـوتـيـوب ...**")
    
    import yt_dlp
    from ..HSL.yt_api import COOKIES_PATH
    
    def _search():
        opts = {
            "extract_flat": True, "quiet": True, "force_ipv4": True, "source_address": "0.0.0.0"
        }
        if os.path.exists(COOKIES_PATH): opts["cookiefile"] = COOKIES_PATH
        with yt_dlp.YoutubeDL(opts) as ydl:
            return ydl.extract_info(f"ytsearch{limit}:{query}", download=False)
            
    try:
        results = await asyncio.get_event_loop().run_in_executor(None, _search)
        if not results or not results.get("entries"):
            return await zed.edit("**⤶ لـم يـتـم الـعـثـور عـلـى نـتـائـج ⚠️**")
            
        reply_text = f"**• نـتـائـج الـبـحـث عـن ↶** `{query}`\n\n"
        for i, entry in enumerate(results["entries"], 1):
            url = entry.get("url") or entry.get("webpage_url", "")
            reply_text += f"**{i}-** [{entry.get('title')}]({url})\n"
            
        await zed.edit(reply_text, link_preview=False)
        
    except Exception as e:
        await zed.edit(f"**⤶ حـدث خـطـأ أثـنـاء الـبـحـث ↶**\n`{e}`")
