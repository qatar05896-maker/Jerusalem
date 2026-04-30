# Venom Userbot - @S_G0C7
# محرك يوتيوب الشامل (إصدار المجلد المخصص Pluginsme) | Modern Python 2026 Standards

import asyncio
import re
from pathlib import Path
from typing import Any

import yt_dlp
from telethon import Button, events
from telethon.tl.types import DocumentAttributeAudio
from urlextract import URLExtract

from repthon import zq_lo
# === الاستدعاءات المباشرة لضمان العمل من داخل Pluginsme ===
from repthon.core.managers import edit_delete, edit_or_reply
from repthon.helpers.utils import reply_id
from repthon.sql_helper.globals import addgvar, gvarstatus, delgvar

# ==========================================
# 0. الإعدادات الحديثة والتخطي (Modern Configs & Bypass)
# ==========================================
plugin_category = "utils"
extractor = URLExtract()

TEMP_DIR = Path("temp")
TEMP_DIR.mkdir(parents=True, exist_ok=True)

# المسار المطلق الصحيح الذي نجح في الكونسول لتخطي حماية يوتيوب
COOKIES_PATH = Path("/root/repthon/repthon/plugins/cookies.txt")

# ذاكرة تخزين مؤقتة سريعة للروابط للتعامل مع الأزرار
YT_DL_CACHE: dict[str, str] = {}


# ==========================================
# 1. دوال البحث والتحميل (Modern Async & Bypass Configs)
# ==========================================

async def search_yt(query: str, limit: int = 1) -> Any | None:
    """بحث يوتيوب متطور لتخطي حماية الروبوتات باستخدام asyncio.to_thread"""
    url = urls[0] if (urls := extractor.find_urls(query)) else None
    
    opts = {
        "quiet": True, 
        "noplaylist": True, 
        "no_warnings": True,
        "extract_flat": limit > 1,
        # === خلطة تخطي الحظر ===
        "force_ipv4": True,
        "source_address": "0.0.0.0",
        "js_runtimes": {"node": {}},
        "remote_components": ["ejs:github"],
        "extractor_args": {"youtube": {"player_client": ["web"]}},
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
        return await asyncio.to_thread(_fetch)
    except Exception as e:
        print(f"YouTube Search Error: {e}")
        return None


async def venom_yt_download(url: str, mode: str, size_mb: float = 0.0) -> tuple[Path | None, Path | None, dict | None]:
    """
    محرك التحميل الذكي يختار الجودة تلقائياً.
    تم تنسيق الجودات (Fallback Formats) لتجنب أخطاء الأزرار تماماً.
    """
    is_ultra = bool(gvarstatus("VENOM_ULTRA_HQ"))
    
    # هندسة الجودات لضمان عدم حدوث خطأ Format not available
    match mode:
        case "audio":
            # جودة صوتية فقط (يسحب m4a أو أفضل صوت متاح)
            fmt = "ba[ext=m4a]/bestaudio/best"
            ext = "m4a"
        case "video" if is_ultra:
            # دمج أفضل فيديو مع أفضل صوت بصيغة mp4 أو سحب أفضل ملف متاح
            fmt = "bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]/best"
            ext = "mp4"
        case "video" if size_mb <= 50:
            # فيديو 720p كحد أقصى ليتناسب مع رفع تيليجرام
            fmt = "bv*[height<=720][ext=mp4]+ba[ext=m4a]/b[ext=mp4]/best"
            ext = "mp4"
        case _:
            # فيديو 480p كحد أقصى للأحجام الكبيرة
            fmt = "bv*[height<=480][ext=mp4]+ba[ext=m4a]/b[ext=mp4]/best"
            ext = "mp4"

    opts = {
        "format": fmt,
        "outtmpl": f"temp/%(id)s_%(title)s_{mode}.%(ext)s",
        "quiet": True, 
        "no_warnings": True,
        "writethumbnail": True,
        "noplaylist": True,
        # === خلطة تخطي الحظر والسرعة ===
        "force_ipv4": True,
        "source_address": "0.0.0.0",
        "js_runtimes": {"node": {}},
        "remote_components": ["ejs:github"],
        "extractor_args": {"youtube": {"player_client": ["web"]}},
        "cookiefile": str(COOKIES_PATH) if COOKIES_PATH.exists() else None,
        # دمج الفيديو في صيغة MP4 إذا كان طلب فيديو ليدعمه تيليجرام كبث
        "merge_output_format": "mp4" if mode == "video" else None,
    }

    def _dl():
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            if not info: return None, None, None
            
            base_name = Path(ydl.prepare_filename(info)).with_suffix('')
            thumb_path = next((base_name.with_suffix(img_ext) for img_ext in [".jpg", ".webp", ".png"] 
                               if base_name.with_suffix(img_ext).exists()), None)
            
            # التأكد من المسار النهائي
            final_path = base_name.with_suffix(f".{ext}")
            actual_path = final_path if final_path.exists() else Path(ydl.prepare_filename(info))
            
            return actual_path, thumb_path, info

    try:
        return await asyncio.to_thread(_dl)
    except Exception as e:
        print(f"YouTube Download Error: {e}")
        return None, None, None


# ==========================================
# 2. الأوامر المباشرة
# ==========================================

@zq_lo.rep_cmd(pattern="ارفع الجودة")
async def toggle_hq(event):
    """التحكم في جودة التحميل (Ultra / Smart)"""
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
        return await zed.edit("**⤶ لم يتم العثور على نتائج، أو حدث حظر من يوتيوب.**")
    
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
    
    if path and path.exists():
        await zed.edit("**⪼ جاري الرفع ... 🚀**")
        quality_msg = "Ultra HQ" if gvarstatus("VENOM_ULTRA_HQ") else ("720p" if size_mb <= 50 else "480p")
        
        await event.client.send_file(
            event.chat_id, file=str(path), thumb=str(thumb) if thumb else None,
            supports_streaming=True, reply_to=await reply_id(event),
            caption=f"**• تم التحميل ✅**\n**• العنوان ↶** `{info.get('title', 'فيديو')}`\n**• الجودة ↶** `{quality_msg}`"
        )
        await zed.delete()
        path.unlink(missing_ok=True)
        if thumb and thumb.exists(): thumb.unlink(missing_ok=True)
    else:
        await zed.edit("**⤶ حدث خطأ أثناء التحميل.**")


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
    
    if path and path.exists():
        await zed.edit("**⪼ جاري الرفع ... 🚀**")
        attr = DocumentAttributeAudio(duration=int(info.get('duration', 0)), title=info.get('title', 'صوت'), performer="Venom")
        await event.client.send_file(
            event.chat_id, file=str(path), thumb=str(thumb) if thumb else None,
            attributes=[attr], reply_to=await reply_id(event),
            caption=f"**• تم التنزيل ✅**\n**• العنوان ↶** `{info.get('title', 'مقطع صوتي')}`"
        )
        await zed.delete()
        path.unlink(missing_ok=True)
        if thumb and thumb.exists(): thumb.unlink(missing_ok=True)
    else:
        await zed.edit("**⤶ حدث خطأ أثناء التحميل.**")


@zq_lo.rep_cmd(pattern="(تنزيل فيديو|تنزيل فيد|يوت فيديو)(?: |$)(.*)")
async def yt_video_dl(event):
    """تنزيل ملف فيديو مباشر"""
    reply = await event.get_reply_message()
    query = event.pattern_match.group(2).strip() or (reply.text if reply else "")
    
    if not query: return await edit_delete(event, "**⤶ يرجى إدراج نص أو رابط**")
    
    zed = await edit_or_reply(event, "**⪼ جاري تحميل الفيديو ... 🎬**")
    
    if not (data := await search_yt(query, limit=1)):
        return await zed.edit("**⤶ فشل العثور على المقطع.**")
    
    size_mb = (data.get('filesize') or data.get('filesize_approx') or 0) / (1024*1024)
    path, thumb, info = await venom_yt_download(data['webpage_url'], "video", size_mb)
    
    if path and path.exists():
        await zed.edit("**⪼ جاري الرفع ... 🚀**")
        await event.client.send_file(
            event.chat_id, file=str(path), thumb=str(thumb) if thumb else None,
            supports_streaming=True, reply_to=await reply_id(event),
            caption=f"**• تم التحميل ✅**\n**• العنوان ↶** `{info.get('title', 'فيديو')}`"
        )
        await zed.delete()
        path.unlink(missing_ok=True)
        if thumb and thumb.exists(): thumb.unlink(missing_ok=True)
    else:
        await zed.edit("**⤶ حدث خطأ أثناء التحميل.**")


# ==========================================
# 3. واجهة الأزرار (Inline Callbacks) المحمية
# ==========================================

@zq_lo.rep_cmd(pattern="(يوتيوب|تنزيل)(?: |$)(.*)")
async def yt_inline_btn(event):
    """عرض قائمة الخيارات باستخدام الأزرار لتجنب الأخطاء"""
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
    """رد الزر الآمن والمتوافق مع الجودات"""
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
    
    if not path or not path.exists():
        return await event.edit("**⤶ حدث خطأ أثناء التحميل، المقطع قد يكون محظوراً أو بحجم كبير جداً.**")
        
    attr = [DocumentAttributeAudio(duration=int(info.get('duration',0)), title=info.get('title', 'صوت'), performer="Venom")] if action == "audio" else []
    
    await zq_lo.send_file(
        event.chat_id, file=str(path), thumb=str(thumb) if thumb else None,
        attributes=attr, supports_streaming=(action == "video"),
        caption=f"**• تم التحميل ✅**\n**• العنوان ↶** `{info.get('title', 'مقطع')}`"
    )
    
    await event.delete()
    path.unlink(missing_ok=True)
    if thumb and thumb.exists(): thumb.unlink(missing_ok=True)
