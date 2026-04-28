# Venom Userbot
# Copyright (C) 2026 Abdullah (Venom). All Rights Reserved
# الـمـالـك: @S_G0C7
# مـلـف الـتـشـغـيـل والـتـحـمـيـل الـمـوحد - إصـدار 2026

import os
import asyncio
from telethon.tl import types
from repthon import zq_lo
from ..core.managers import edit_delete, edit_or_reply
from ..helpers.utils import reply_id

# اسـتـدعـاء الـمـحـركـات الـخـلـفـيـة مـن مـجـلـد HSL
from ..HSL.yt_api import YouTube
from ..HSL.call_engine import CallEngine

plugin_category = "الـتـشـغـيـل"

# تـهـيـئـة مـحـرك الـمـكـالـمـات بـاسـتـخـدام عـمـيـل الـبـوت
VC = CallEngine(zq_lo)

# تـشـغـيـل الـمـحـرك عـنـد إقـلاع الـبـوت
asyncio.get_event_loop().create_task(VC.start())

# ==========================================
# أوامــر الـمـكـالـمـات الـصـوتـيـة والـمـرئـيـة
# ==========================================

@zq_lo.rep_cmd(pattern="شغل(?:\s|$)([\s\S]*)")
async def play_audio(event):
    """تـشـغـيـل صـوتـي فـي الـمـكـالـمـة"""
    input_str = event.pattern_match.group(1)
    if not input_str and not event.reply_to_msg_id:
        return await edit_delete(event, "**⤶ يـرجـى إدراج رابـط أو الـرد عـلـى مـقـطـع لـلـتـشـغـيـل**")
    
    zed = await edit_or_reply(event, "**⪼ جـارِ مـعـالـجـة الـطـلـب وبـدء الـتـشـغـيـل ...**")
    
    # الـتـعـامـل مـع الـروابـط أو الـبـحث
    title = "مـقـطـع صـوتـي"
    res = await VC.play_or_queue(event.chat_id, input_str, title, is_video=False)
    await zed.edit(f"{res}\n**• الـمـالـك ↶ @S_G0C7**")

@zq_lo.rep_cmd(pattern="فيد(?:\s|$)([\s\S]*)")
async def play_video(event):
    """تـشـغـيـل فـيـديـو فـي الـمـكـالـمـة"""
    input_str = event.pattern_match.group(1)
    if not input_str:
        return await edit_delete(event, "**⤶ يـرجـى إدراج رابـط لـتـشـغـيـل الـفـيـديـو**")
    
    zed = await edit_or_reply(event, "**⪼ جـارِ تـجـهـيـز بـث الـفـيـديـو بـأعـلـى جـودة ...**")
    title = "بـث مـرئـي"
    res = await VC.play_or_queue(event.chat_id, input_str, title, is_video=True)
    await zed.edit(f"{res}\n**• الـمـالـك ↶ @S_G0C7**")

@zq_lo.rep_cmd(pattern="توقف$")
async def pause_cmd(event):
    await VC.pause(event.chat_id)
    await edit_delete(event, "**⤶ تـم إيـقـاف الـتـشـغـيـل مـؤقـتـاً ⏸**")

@zq_lo.rep_cmd(pattern="كمل$")
async def resume_cmd(event):
    await VC.resume(event.chat_id)
    await edit_delete(event, "**⤶ تـم اسـتـئـنـاف الـتـشـغـيـل ▶️**")

@zq_lo.rep_cmd(pattern="تخطي$")
async def skip_cmd(event):
    zed = await edit_or_reply(event, "**⪼ جـارِ تـخـطـي الـمـقـطـع الـحـالـي ...**")
    res = await VC.skip(event.chat_id)
    await zed.edit(res)

@zq_lo.rep_cmd(pattern="خروج$")
async def leave_cmd(event):
    await VC.stop(event.chat_id)
    await edit_delete(event, "**⤶ تـم إيـقـاف الـبـث ومـغـادرة الـمـكـالـمـة بـنـجـاح 🚪**")

@zq_lo.rep_cmd(pattern="قائمة$")
async def list_cmd(event):
    playlist = VC.get_playlist(event.chat_id)
    if not playlist:
        return await edit_delete(event, "**⤶ الـطـابـور فـارغ حـالـيـاً 📭**")
    
    msg = "**• قـائـمـة الـتـشـغـيـل الـحـالـيـة ↶**\n\n"
    for i, track in enumerate(playlist, 1):
        status = "يـعـمـل الـآن 🔊" if i == 1 else "فـي الـانـتـظـار ⏳"
        msg += f"**{i}-** `{track['title']}` - ({status})\n"
    
    await edit_or_reply(event, msg)

# ==========================================
# أوامــر الـتـحـمـيـل الـمـبـاشـر لـلـتـيـلـيـجـرام
# ==========================================

@zq_lo.rep_cmd(pattern="تحميل فيديو(?:\s|$)([\s\S]*)")
async def dl_video(event):
    input_str = event.pattern_match.group(1) or (await event.get_reply_message() and (await event.get_reply_message()).text)
    if not input_str:
        return await edit_delete(event, "**⤶ يـرجـى إدراج رابـط لـلـتـحـمـيـل**")

    zed = await edit_or_reply(event, "**⪼ جـارِ تـحـمـيـل الـفـيـديـو بـنـظـام الـخـطـوط الـ 8 ...**")
    file_path, info = await YouTube.download(input_str, is_video=True)
    
    if file_path:
        await zed.edit("**⪼ جـارِ رفـع الـمـلـف إلـى سـيـرفـرات الـتـيـلـيـجـرام ...**")
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
        await zed.edit("**⤶ فـشـل الـتـحـمـيـل، يـرجـى الـتأكـد مـن الـرابـط أو الـكـوكـيـز.**")

@zq_lo.rep_cmd(pattern="تحميل صوت(?:\s|$)([\s\S]*)")
async def dl_audio(event):
    input_str = event.pattern_match.group(1) or (await event.get_reply_message() and (await event.get_reply_message()).text)
    if not input_str:
        return await edit_delete(event, "**⤶ يـرجـى إدراج رابـط لـلـتـحـمـيـل**")

    zed = await edit_or_reply(event, "**⪼ جـارِ اسـتـخـراج الـصـوت وتـحـمـيـلـه ...**")
    file_path, info = await YouTube.download(input_str, is_video=False)
    
    if file_path:
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
        await zed.edit("**⤶ فـشـل الـتـحـمـيـل، يـرجـى الـتـأكـد مـن الـرابـط.**")
