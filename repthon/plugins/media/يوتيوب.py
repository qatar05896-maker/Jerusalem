# Venom Userbot - @S_G0C7
# محرك يوتيوب الشامل | Modern Python 3.11+ Architecture

import asyncio
import re
from pathlib import Path
from typing import Optional, Tuple, Any

import yt_dlp
from telethon import Button, events
from telethon.tl.types import DocumentAttributeAudio
from urlextract import URLExtract

from repthon import zq_lo
# تم تحويل الاستدعاءات إلى مباشرة (Absolute Imports) لتجنب أخطاء المسارات
from repthon.core.managers import edit_delete, edit_or_reply
from repthon.helpers.utils import reply_id
from repthon.sql_helper.globals import addgvar, gvarstatus, delgvar

# ==========================================
# 0. الإعدادات الحديثة (Modern Configs)
# ==========================================
plugin_category = "utils"
extractor = URLExtract()

# استخدام Pathlib بدلاً من os الكلاسيكية
TEMP_DIR = Path("temp")
TEMP_DIR.mkdir(parents=True, exist_ok=True)
COOKIES_PATH = Path("repthon/plugins/cookies.txt")

# كاش زراير الانلاين
YT_DL_CACHE: dict[str, str] = {}


# ==========================================
# 1. دوال الذكاء الاصطناعي (Modern Async)
# ==========================================

async def search_yt(query: str, limit: int = 1) -> Any | None:
    """بحث يوتيوب باستخدام asyncio.to_thread الحديثة"""
    url = urls[0] if (urls := extractor.find_urls(query)) else None
    
    opts = {
        "quiet": True, 
        "noplaylist": True, 
        "no_warnings": True,
        "extract_flat": limit > 1,
        "cookiefile": str(COOKIES_PATH) if COOKIES_PATH.exists() else None
    }
    
    def _fetch():
        with yt_dlp.YoutubeDL(opts) as ydl:
            if url and limit == 1:
                return ydl.extract_info(url, download=False)
            
            res = ydl.extract_info(f"ytsearch{limit}:{query}", download=False)
            if limit == 1:
                return res['entries'][0] if res and res.get('entries') else None
            return res['entries'] if res else []
            
    try:
        # استخدام الطريقة العصرية لعمل المهام في الخلفية
        return await asyncio.to_thread(_fetch)
    except Exception:
        return None


async def venom_yt_download(url: str, mode: str, size_mb: float = 0.0) -> Tuple[Path | None, Path | None, dict | None]:
    """محرك التحميل الذكي يختار الجودة تلقائياً"""
    is_ultra = bool(gvarstatus("VENOM_ULTRA_HQ"))
    
    # استخدام Pattern Matching الجديد (Python 3.10+) 
    match mode:
        case "audio":
            fmt = "bestaudio[ext=m4a]/bestaudio"
            ext = "m4a"
        case "video" if is_ultra:
            fmt = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"
            ext = "mp4"
        case "video" if size_mb <= 50:
            fmt = "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]"
            ext = "mp4"
        case _:
            fmt = "bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]"
            ext = "mp4"

    opts = {
        "format": fmt,
        "outtmpl": f"temp/%(id)s_%(title)s_{mode}.%(ext)s",
        "quiet": True, 
        "no_warnings": True,
        "writethumbnail": True,
        "cookiefile": str(COOKIES_PATH) if COOKIES_PATH.exists() else None
    }

    def _dl():
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            base_name = Path(ydl.prepare_filename(info)).with_suffix('')
            
            # جلب الغلاف بطريقة عصرية
            thumb_path = next((base_name.with_suffix(ext) for ext in [".jpg", ".webp", ".png"] 
                               if base_name.with_suffix(ext).exists()), None)
            
            final_path = base_name.with_suffix(f".{ext}")
            return final_path if final_path.exists() else Path(ydl.prepare_filename(info)), thumb_path, info

    try:
        return await asyncio.to_thread(_dl)
    except Exception:
        return None, None, None


# ==========================================
# 2. الأوامر المباشرة (Decorators & Walrus)
# ==========================================

@zq_lo.rep_cmd(pattern="ارفع الجودة")
async def toggle_hq(event):
    """التحكم في جودة التحميل"""
    if gvarstatus("VENOM_ULTRA_HQ"):
        delgvar("VENOM_ULTRA_HQ")
        return await edit_or_reply(event, "**⤶ تم العودة لوضع التحميل الذكي (Smart DL) ⚡**")
    
    addgvar("VENOM_ULTRA_HQ", "True")
    await edit_or_reply(event, "**⤶ تم تفعيل الجودة الفائقة (Ultra HQ) 🚀**")


@zq_lo.rep_cmd(pattern="بحث(?: |$)(.*)")
async def yt_search_10(event):
    """بحث يوتيوب للحصول على 10 نتائج"""
    if not (query := event.pattern_match.group(1).strip()):
        return await edit_delete(event, "**⤶ يرجى كتابة كلمة للبحث**")
    
    zed = await edit_or_reply(event, "**⪼ جاري البحث في يوتيوب ... 🔍**")
    
    if not (res := await search_yt(query, limit=10)):
        return await zed.edit("**⤶ لم يتم العثور على نتائج.**")
    
    text = f"**• أفضل 10 نتائج لـ ↶** `{query}`\n\n"
    for i, entry in enumerate(res, 1):
        url = entry.get('url') or entry.get('webpage_url')
        text += f"**{i}.** [{entry.get('title')}]({url})\n"
        
    await zed.edit(text, link_preview=False)


@zq_lo.rep_cmd(pattern="يوت(?: |$)(?!فيديو)(.*)")
async def yt_smart_dl(event):
    """التحميل الذكي (صوت + فيديو)"""
    reply = await event.get_reply_message()
    query = event.pattern_match.group(1).strip() or (reply.text if reply else "")
    
    if not query: return await edit_delete(event, "**⤶ يرجى إدراج نص أو رابط**")
    
    zed = await edit_or_reply(event, "**⪼ جاري التحميل الذكي ... ⚡**")
    
    if not (data := await search_yt(query, limit=1)):
        return await zed.edit("**⤶ فشل العثور على المقطع.**")
    
    size_mb = (data.get('filesize') or data.get('filesize_approx') or 0) / (1024*1024)
    path, thumb, info = await venom_yt_download(data['webpage_url'], "video", size_mb)
    
    if path:
        await zed.edit("**⪼ جاري الرفع ... 🚀**")
        quality_msg = "Ultra HQ" if gvarstatus("VENOM_ULTRA_HQ") else ("720p" if size_mb <= 50 else "480p")
        
        await event.client.send_file(
            event.chat_id, file=str(path), thumb=str(thumb) if thumb else None,
            supports_streaming=True, reply_to=await reply_id(event),
            caption=f"**• تم التحميل ✅**\n**• العنوان ↶** `{info['title']}`\n**• الجودة ↶** `{quality_msg}`"
        )
        await zed.delete()
        path.unlink(missing_ok=True)
        if thumb: thumb.unlink(missing_ok=True)


@zq_lo.rep_cmd(pattern="(تنزيل صوت|صوت)(?: |$)(.*)")
async def yt_audio_dl(event):
    """تنزيل ملف صوتي M4A مع الغلاف"""
    reply = await event.get_reply_message()
    query = event.pattern_match.group(2).strip() or (reply.text if reply else "")
    
    if not query: return await edit_delete(event, "**⤶ يرجى إدراج نص أو رابط**")
    
    zed = await edit_or_reply(event, "**⪼ جاري استخراج الصوت (m4a) ... 🎧**")
    
    if not (data := await search_yt(query, limit=1)):
        return await zed.edit("**⤶ فشل العثور على المقطع.**")
    
    path, thumb, info = await venom_yt_download(data['webpage_url'], "audio")
    
    if path:
        await zed.edit("**⪼ جاري الرفع ... 🚀**")
        attr = DocumentAttributeAudio(duration=int(info.get('duration', 0)), title=info.get('title'), performer="Venom")
        await event.client.send_file(
            event.chat_id, file=str(path), thumb=str(thumb) if thumb else None,
            attributes=[attr], reply_to=await reply_id(event),
            caption=f"**• تم التنزيل ✅**\n**• العنوان ↶** `{info['title']}`"
        )
        await zed.delete()
        path.unlink(missing_ok=True)
        if thumb: thumb.unlink(missing_ok=True)


@zq_lo.rep_cmd(pattern="(تنزيل فيديو|تنزيل فيد|يوت فيديو)(?: |$)(.*)")
async def yt_video_dl(event):
    """تنزيل ملف فيديو"""
    reply = await event.get_reply_message()
    query = event.pattern_match.group(2).strip() or (reply.text if reply else "")
    
    if not query: return await edit_delete(event, "**⤶ يرجى إدراج نص أو رابط**")
    
    zed = await edit_or_reply(event, "**⪼ جاري تحميل الفيديو ... 🎬**")
    
    if not (data := await search_yt(query, limit=1)):
        return await zed.edit("**⤶ فشل العثور على المقطع.**")
    
    size_mb = (data.get('filesize') or data.get('filesize_approx') or 0) / (1024*1024)
    path, thumb, info = await venom_yt_download(data['webpage_url'], "video", size_mb)
    
    if path:
        await zed.edit("**⪼ جاري الرفع ... 🚀**")
        await event.client.send_file(
            event.chat_id, file=str(path), thumb=str(thumb) if thumb else None,
            supports_streaming=True, reply_to=await reply_id(event),
            caption=f"**• تم التحميل ✅**\n**• العنوان ↶** `{info['title']}`"
        )
        await zed.delete()
        path.unlink(missing_ok=True)
        if thumb: thumb.unlink(missing_ok=True)


# ==========================================
# 3. واجهة الأزرار (Inline Callbacks)
# ==========================================

@zq_lo.rep_cmd(pattern="(يوتيوب|تنزيل)(?: |$)(.*)")
async def yt_inline_btn(event):
    """عرض قائمة الخيارات باستخدام الأزرار"""
    reply = await event.get_reply_message()
    query = event.pattern_match.group(2).strip() or (reply.text if reply else "")
    
    if not query: return await edit_delete(event, "**⤶ يرجى إدراج المقطع أو الرابط**")
        
    if not (data := await search_yt(query, limit=1)):
        return await edit_delete(event, "**⤶ فشل العثور على نتائج.**")
    
    url = data.get('webpage_url') or data.get('url')
    title = data.get('title', 'مقطع يوتيوب')
    
    buttons = [
        [Button.inline("صوت 🎧", data=b"ytdl_audio"), Button.inline("فيديو 🎬", data=b"ytdl_video")]
    ]
    
    try:
        msg = await zq_lo.tgbot.send_message(
            event.chat_id, 
            f"**╮ اختر الجودة المطلوبة ╰**\n**• المقطع ↶** `{title}`", 
            buttons=buttons
        )
        YT_DL_CACHE[f"{msg.chat_id}_{msg.id}"] = url
        await event.delete()
    except Exception:
        await edit_or_reply(event, "**⤶ يرجى إضافة البوت المساعد للمجموعة لاستخدام الأزرار، أو استخدم `.صوت` / `.فيديو`**")


@zq_lo.tgbot.on(events.CallbackQuery(data=re.compile(b"ytdl_(audio|video)")))
async def on_ytdl_cb(event):
    """استقبال ضغطات الأزرار (باستخدام Python 3.10 Match-Case)"""
    if event.sender_id != zq_lo.uid:
        return await event.answer("هذا الأمر للمالك فقط! ❌", alert=True)
        
    action = event.data_match.group(1).decode()
    cache_key = f"{event.chat_id}_{event.message_id}"
    
    if not (url := YT_DL_CACHE.get(cache_key)):
        return await event.answer("انتهت صلاحية هذا الزر ❌", alert=True)
        
    await event.edit("**⪼ جاري المعالجة والتحميل ... ⚡**")
    
    data = await search_yt(url, limit=1)
    size_mb = (data.get('filesize') or data.get('filesize_approx') or 0) / (1024*1024) if data else 0
    
    path, thumb, info = await venom_yt_download(url, action, size_mb)
    
    if not path:
        return await event.edit("**⤶ حدث خطأ أثناء التحميل أو الملف كبير جداً.**")
        
    attr = [DocumentAttributeAudio(duration=int(info.get('duration',0)), title=info.get('title'), performer="Venom")] if action == "audio" else []
    
    await zq_lo.send_file(
        event.chat_id, file=str(path), thumb=str(thumb) if thumb else None,
        attributes=attr, supports_streaming=(action == "video"),
        caption=f"**• تم التحميل ✅**\n**• العنوان ↶** `{info['title']}`"
    )
    
    await event.delete()
    path.unlink(missing_ok=True)
    if thumb: thumb.unlink(missing_ok=True)
