# Venom Userbot
# Copyright (C) 2026 Abdullah (Venom). All Rights Reserved
# الـمـالـك: @S_G0C7
# أوامــر الـمـكـالـمـات والـتـشـغـيـل (مـحـدث 2026 - بـحـث ذكـي)

import asyncio
import os
from urlextract import URLExtract
from repthon import zq_lo
from ..core.managers import edit_delete, edit_or_reply
from ..helpers.utils import reply_id

# اسـتـدعـاء مـحـرك الـمـكـالـمـات
from ..HSL.call_engine import CallEngine

plugin_category = "utils" # تـم الـتـعـديـل لـيـعـمـل بـدون كـراش
extractor = URLExtract()

# تـهـيـئـة الـمـحـرك
VC = CallEngine(zq_lo)
zq_lo.loop.create_task(VC.start())

async def get_stream_info(query: str):
    """دالـة ذكـيـة لـتـحـويـل نـص الـبـحـث إلـى رابـط وعـنـوان حـقـيـقـي"""
    urls = extractor.find_urls(query)
    if urls:
        return urls[0], "مـقـطـع مـن رابـط"
    
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
            entry = results["entries"][0]
            return entry.get("url"), entry.get("title")
    except Exception:
        pass
    return None, None


@zq_lo.rep_cmd(pattern="شغل(?: |$)(.*)")
async def play_audio_cmd(event):
    """تـشـغـيـل صـوتـي فـي الـمـكـالـمـة"""
    query = event.pattern_match.group(1)
    if not query and not event.reply_to_msg_id:
        return await edit_delete(event, "**⤶ يـرجـى كـتـابـة اسـم الـأغـنـيـة أو إدراج رابـط لـلـتـشـغـيـل**")
    
    if not query and event.reply_to_msg_id:
        query = (await event.get_reply_message()).text
        if not query:
            return await edit_delete(event, "**⤶ يـرجـى الـرد عـلـى نـص أو إدراج رابـط يـوتـيـوب.**")

    zed = await edit_or_reply(event, "**⪼ جـارِ الـبـحـث وتـجـهـيـز الـتـشـغـيـل ... 🎧**")
    
    url, title = await get_stream_info(query)
    if not url:
        return await zed.edit(f"**⤶ لـم أسـتـطـع إيـجـاد:** `{query}`")

    res = await VC.play_or_queue(event.chat_id, url, title, is_video=False)
    await zed.edit(f"{res}\n**• الـمـالـك ↶ @S_G0C7**")


@zq_lo.rep_cmd(pattern="فيد(?: |$)(.*)")
async def play_video_cmd(event):
    """تـشـغـيـل فـيـديـو فـي الـمـكـالـمـة"""
    query = event.pattern_match.group(1)
    if not query and not event.reply_to_msg_id:
        return await edit_delete(event, "**⤶ يـرجـى كـتـابـة اسـم الـفـيـديـو أو إدراج رابـط لـتـشـغـيـلـه**")
    
    if not query and event.reply_to_msg_id:
        query = (await event.get_reply_message()).text
        if not query:
            return await edit_delete(event, "**⤶ يـرجـى الـرد عـلـى نـص أو إدراج رابـط يـوتـيـوب.**")

    zed = await edit_or_reply(event, "**⪼ جـارِ الـبـحـث وتـجـهـيـز بـث الـفـيـديـو بـأعـلـى جـودة ... 🎬**")
    
    url, title = await get_stream_info(query)
    if not url:
        return await zed.edit(f"**⤶ لـم أسـتـطـع إيـجـاد:** `{query}`")

    res = await VC.play_or_queue(event.chat_id, url, title, is_video=True)
    await zed.edit(f"{res}\n**• الـمـالـك ↶ @S_G0C7**")


@zq_lo.rep_cmd(pattern="توقف(?: |$)(.*)")
async def pause_cmd(event):
    await VC.pause(event.chat_id)
    await edit_delete(event, "**⤶ تـم إيـقـاف الـتـشـغـيـل مـؤقـتـاً ⏸**")


@zq_lo.rep_cmd(pattern="كمل(?: |$)(.*)")
async def resume_cmd(event):
    await VC.resume(event.chat_id)
    await edit_delete(event, "**⤶ تـم اسـتـئـنـاف الـتـشـغـيـل ▶️**")


@zq_lo.rep_cmd(pattern="تخطي(?: |$)(.*)")
async def skip_cmd(event):
    zed = await edit_or_reply(event, "**⪼ جـارِ تـخـطـي الـمـقـطـع الـحـالـي ...**")
    res = await VC.skip(event.chat_id)
    await zed.edit(res)


@zq_lo.rep_cmd(pattern="خروج(?: |$)(.*)")
async def leave_cmd(event):
    await VC.stop(event.chat_id)
    await edit_delete(event, "**⤶ تـم إيـقـاف الـبـث ومـغـادرة الـمـكـالـمـة بـنـجـاح 🚪**")


@zq_lo.rep_cmd(pattern="قائمة(?: |$)(.*)")
async def list_cmd(event):
    playlist = VC.get_playlist(event.chat_id)
    if not playlist:
        return await edit_delete(event, "**⤶ الـطـابـور فـارغ حـالـيـاً 📭**")
    
    msg = "**• قـائـمـة الـتـشـغـيـل الـحـالـيـة ↶**\n\n"
    for i, track in enumerate(playlist, 1):
        status = "يـعـمـل الـآن 🔊" if i == 1 else "فـي الـانـتـظـار ⏳"
        msg += f"**{i}-** `{track['title']}` - ({status})\n"
    
    await edit_or_reply(event, msg)
