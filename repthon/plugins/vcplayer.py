# Venom Userbot
# Copyright (C) 2026 Abdullah (Venom). All Rights Reserved
# الـمـالـك: @S_G0C7
# أوامــر الـمـكـالـمـات والـتـشـغـيـل

import asyncio
from repthon import zq_lo
from ..core.managers import edit_delete, edit_or_reply
from ..helpers.utils import reply_id

# اسـتـدعـاء مـحـرك الـمـكـالـمـات
from ..HSL.call_engine import CallEngine

plugin_category = "الـمـكـالـمـات"

# تـهـيـئـة الـمـحـرك
VC = CallEngine(zq_lo)
zq_lo.loop.create_task(VC.start())


@zq_lo.rep_cmd(pattern="شغل(?: |$)(.*)")
async def play_audio_cmd(event):
    """تـشـغـيـل صـوتـي فـي الـمـكـالـمـة"""
    input_str = event.pattern_match.group(1)
    if not input_str and not event.reply_to_msg_id:
        return await edit_delete(event, "**⤶ يـرجـى إدراج رابـط أو الـرد عـلـى مـقـطـع لـلـتـشـغـيـل**")
    
    # إذا كـان الـرد عـلـى مـلـف صـوتـي بـدون رابـط (سـنـضـيـف دعـم الـتـحـمـيـل الـمـحـلـي لـاحـقـاً)
    if not input_str:
        return await edit_delete(event, "**⤶ حـالـيـاً يـدعـم الـتـشـغـيـل بـالـروابـط، يـرجـى إرفـاق رابـط.**")

    zed = await edit_or_reply(event, "**⪼ جـارِ مـعـالـجـة الـطـلـب وبـدء الـتـشـغـيـل ...**")
    res = await VC.play_or_queue(event.chat_id, input_str, "مـقـطـع صـوتـي", is_video=False)
    await zed.edit(f"{res}\n**• الـمـالـك ↶ @S_G0C7**")


@zq_lo.rep_cmd(pattern="فيد(?: |$)(.*)")
async def play_video_cmd(event):
    """تـشـغـيـل فـيـديـو فـي الـمـكـالـمـة"""
    input_str = event.pattern_match.group(1)
    if not input_str:
        return await edit_delete(event, "**⤶ يـرجـى إدراج رابـط لـتـشـغـيـل الـفـيـديـو**")
    
    zed = await edit_or_reply(event, "**⪼ جـارِ تـجـهـيـز بـث الـفـيـديـو بـأعـلـى جـودة ...**")
    res = await VC.play_or_queue(event.chat_id, input_str, "بـث مـرئـي", is_video=True)
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
