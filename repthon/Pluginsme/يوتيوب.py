# ᯓ 𝙑𝙚𝙣𝙤𝙢 𝗨𝘀𝗲𝗿𝗯𝗼𝘁 - اوامــــر الـبـحــــث والـتـحـمـيــــل
# Copyright (C) 2026 Abdullah (Venom). All Rights Reserved.
# Modern Telethon 2026 & Zero-Latency API | Anti-Interference Regex

import asyncio
import re
from pathlib import Path
from typing import Any

import yt_dlp
from telethon import Button, events
from telethon.tl.types import DocumentAttributeAudio
from urlextract import URLExtract

from repthon import zq_lo
from repthon.core.managers import edit_delete, edit_or_reply
from repthon.helpers.utils import reply_id
from repthon.sql_helper.globals import addgvar, gvarstatus, delgvar

# ==========================================
# 0. الإعدادات وتخطي الحماية
# ==========================================
plugin_category = "utils"
extractor = URLExtract()

TEMP_DIR = Path("temp")
TEMP_DIR.mkdir(parents=True, exist_ok=True)

# المسار المطلق لملف الكوكيز (لضمان تخطي حماية يوتيوب)
COOKIES_PATH = Path("/root/repthon/repthon/plugins/cookies.txt")

# ذاكرة تخزين مؤقتة للإنلاين
YT_DL_CACHE: dict[str, str] = {}


# ==========================================
# 1. المحرك الأساسي (محمي ضد التعليق Timeouts)
# ==========================================

async def search_yt(query: str, limit: int = 1) -> Any | None:
    """بحث يوتيوب متطور"""
    url = urls[0] if (urls := extractor.find_urls(query)) else None
    
    opts = {
        "quiet": True, 
        "noplaylist": True, 
        "no_warnings": True,
        "extract_flat": limit > 1,
        "socket_timeout": 30, # منع تعليق البوت نهائياً
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
        print(f"Search Error: {e}")
        return None

async def venom_download(url: str, mode: str) -> tuple[Path | None, Path | None, dict | None]:
    """المحرك الشامل للتحميل من جميع المنصات"""
    is_ultra = bool(gvarstatus("VENOM_ULTRA_HQ"))
    
    if mode == "audio":
        fmt = "ba[ext=m4a]/bestaudio/best"
        ext = "m4a"
    else:
        fmt = "bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]/best" if is_ultra else "bv*[height<=720][ext=mp4]+ba[ext=m4a]/b[ext=mp4]/best"
        ext = "mp4"

    opts = {
        "format": fmt,
        "outtmpl": f"temp/%(id)s_%(title)s_{mode}.%(ext)s",
        "quiet": True, 
        "no_warnings": True,
        "writethumbnail": True, 
        "noplaylist": True,
        "socket_timeout": 60, # منع التعليق أثناء التحميل
        "force_ipv4": True,
        "source_address": "0.0.0.0",
        "js_runtimes": {"node": {}},
        "remote_components": ["ejs:github"],
        "extractor_args": {"youtube": {"player_client": ["web"]}},
        "cookiefile": str(COOKIES_PATH) if COOKIES_PATH.exists() else None,
        "merge_output_format": "mp4" if mode == "video" else None,
    }

    def _dl():
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            if not info: return None, None, None
            
            base_name = Path(ydl.prepare_filename(info)).with_suffix('')
            thumb_path = next((base_name.with_suffix(img_ext) for img_ext in [".jpg", ".webp", ".png"] 
                               if base_name.with_suffix(img_ext).exists()), None)
            
            final_path = base_name.with_suffix(f".{ext}")
            actual_path = final_path if final_path.exists() else Path(ydl.prepare_filename(info))
            
            return actual_path, thumb_path, info

    try:
        return await asyncio.to_thread(_dl)
    except Exception as e:
        print(f"Download Error: {e}")
        return None, None, None

async def inline_search_send(event, bot_username, query, error_msg):
    """جلب الصور والمتحركات عبر إنلاين تيليجرام"""
    zed = await edit_or_reply(event, "**⪼ جاري البحث ... 🔍**")
    try:
        results = await event.client.inline_query(bot_username, query)
        if results:
            await results[0].click(event.chat_id, reply_to=await reply_id(event))
            await zed.delete()
        else:
            await zed.edit(error_msg)
    except Exception:
        await zed.edit("**⤶ حدث خطأ أثناء الاتصال بالبوت المساعد.**")


# ==========================================
# 2. الأوامر المستقلة (بدون تداخل)
# ==========================================

# 1. بحث + اسم الاغنية
@zq_lo.rep_cmd(pattern="بحث(?:\s+|$)(.*)")
async def yt_search_audio(event):
    """تحميل الاغاني من يوتيوب بدقة خفيفة (صوت)"""
    query = event.pattern_match.group(1).strip()
    if not query: return await edit_delete(event, "**⤶ يرجى كتابة اسم الأغنية**")
    
    zed = await edit_or_reply(event, "**⪼ جاري البحث وتحميل الصوت (m4a) ... 🎧**")
    if not (data := await search_yt(query, limit=1)):
        return await zed.edit("**⤶ فشل العثور على الأغنية.**")
    
    path, thumb, info = await venom_download(data['webpage_url'], "audio")
    if path and path.exists():
        await zed.edit("**⪼ جاري الرفع ... 🚀**")
        attr = DocumentAttributeAudio(duration=int(info.get('duration', 0)), title=info.get('title', 'صوت'), performer="𝙑𝙚𝙣𝙤𝙢")
        await event.client.send_file(event.chat_id, file=str(path), thumb=str(thumb) if thumb else None, attributes=[attr], reply_to=await reply_id(event))
        await zed.delete()
        path.unlink(missing_ok=True); (thumb.unlink(missing_ok=True) if thumb else None)
    else: await zed.edit("**⤶ حدث خطأ أثناء التحميل.**")

# 2. يوت + كلمة (نفي كلمة يوتيوب لمنع التداخل)
@zq_lo.rep_cmd(pattern="يوت(?:\s+|$)(?!يوب)(.*)")
async def yt_inline_dl(event):
    """تحميل الصوت والفيديو بواسطة انلاين"""
    reply = await event.get_reply_message()
    query = event.pattern_match.group(1).strip() or (reply.text if reply else "")
    if not query: return await edit_delete(event, "**⤶ يرجى إدراج المقطع أو الرابط**")
        
    if not (data := await search_yt(query, limit=1)):
        return await edit_delete(event, "**⤶ فشل العثور على المقطع.**")
    
    url = data.get('webpage_url') or data.get('url')
    title = data.get('title', 'مقطع يوتيوب')
    buttons = [[Button.inline("صوت 🎧", data=b"ytdl_audio"), Button.inline("فيديو 🎬", data=b"ytdl_video")]]
    
    try:
        msg = await zq_lo.tgbot.send_message(event.chat_id, f"**╮ اختر الجودة المطلوبة ╰**\n**• المقطع ↶** `{title}`", buttons=buttons)
        YT_DL_CACHE[f"{msg.chat_id}_{msg.id}"] = url
        await event.delete()
    except Exception:
        await edit_or_reply(event, "**⤶ يرجى إضافة البوت المساعد للمجموعة.**")

# 3. فيديو + اسم المقطع
@zq_lo.rep_cmd(pattern="فيديو(?:\s+|$)(.*)")
async def yt_search_video(event):
    """تحميل مقاطع الفيديو"""
    query = event.pattern_match.group(1).strip()
    if not query: return await edit_delete(event, "**⤶ يرجى كتابة اسم المقطع**")
    
    zed = await edit_or_reply(event, "**⪼ جاري البحث وتحميل الفيديو ... 🎬**")
    if not (data := await search_yt(query, limit=1)):
        return await zed.edit("**⤶ فشل العثور على الفيديو.**")
    
    path, thumb, info = await venom_download(data['webpage_url'], "video")
    if path and path.exists():
        await zed.edit("**⪼ جاري الرفع ... 🚀**")
        await event.client.send_file(event.chat_id, file=str(path), thumb=str(thumb) if thumb else None, supports_streaming=True, reply_to=await reply_id(event))
        await zed.delete()
        path.unlink(missing_ok=True); (thumb.unlink(missing_ok=True) if thumb else None)
    else: await zed.edit("**⤶ حدث خطأ أثناء التحميل.**")

# 4. تحميل صوت + رابط
@zq_lo.rep_cmd(pattern="تحميل صوت(?:\s+|$)(.*)")
async def yt_link_audio(event):
    """تحميل المقاطع الصوتية عبر الرابط"""
    url = event.pattern_match.group(1).strip()
    if not url: return await edit_delete(event, "**⤶ يرجى وضع الرابط**")
    
    zed = await edit_or_reply(event, "**⪼ جاري تحميل الصوت ... 🎧**")
    path, thumb, info = await venom_download(url, "audio")
    if path and path.exists():
        await zed.edit("**⪼ جاري الرفع ... 🚀**")
        attr = DocumentAttributeAudio(duration=int(info.get('duration', 0)), title=info.get('title', 'صوت'), performer="𝙑𝙚𝙣𝙤𝙢")
        await event.client.send_file(event.chat_id, file=str(path), thumb=str(thumb) if thumb else None, attributes=[attr], reply_to=await reply_id(event))
        await zed.delete()
        path.unlink(missing_ok=True); (thumb.unlink(missing_ok=True) if thumb else None)
    else: await zed.edit("**⤶ الرابط غير صالح أو محمي.**")

# 5. تحميل فيديو + رابط
@zq_lo.rep_cmd(pattern="تحميل فيديو(?:\s+|$)(.*)")
async def yt_link_video(event):
    """تحميل مقاطع الفيديو عبر الرابط"""
    url = event.pattern_match.group(1).strip()
    if not url: return await edit_delete(event, "**⤶ يرجى وضع الرابط**")
    
    zed = await edit_or_reply(event, "**⪼ جاري تحميل الفيديو ... 🎬**")
    path, thumb, info = await venom_download(url, "video")
    if path and path.exists():
        await zed.edit("**⪼ جاري الرفع ... 🚀**")
        await event.client.send_file(event.chat_id, file=str(path), thumb=str(thumb) if thumb else None, supports_streaming=True, reply_to=await reply_id(event))
        await zed.delete()
        path.unlink(missing_ok=True); (thumb.unlink(missing_ok=True) if thumb else None)
    else: await zed.edit("**⤶ الرابط غير صالح أو محمي.**")

# 6. يوتيوب + كلمة (مستقل تماماً الآن)
@zq_lo.rep_cmd(pattern="يوتيوب(?:\s+|$)(.*)")
async def yt_search_links(event):
    """البحث عن روابط ع يوتيوب"""
    query = event.pattern_match.group(1).strip()
    if not query: return await edit_delete(event, "**⤶ يرجى كتابة كلمة للبحث**")
    
    zed = await edit_or_reply(event, "**⪼ جاري استخراج الروابط ... 🔍**")
    if not (res := await search_yt(query, limit=10)):
        return await zed.edit("**⤶ لم يتم العثور على نتائج.**")
    
    text = f"**• نتائج البحث في يوتيوب لـ ↶** `{query}`\n\n"
    for i, entry in enumerate(res, 1):
        url = entry.get('url') or entry.get('webpage_url')
        text += f"**{i}.** [{entry.get('title')}]({url})\n"
    await zed.edit(text, link_preview=False)

# ==========================================
# 3. محملات المنصات الأخرى
# ==========================================

@zq_lo.rep_cmd(pattern="(انستا|تيك|لايكي|فيس|تويتر|بنترست|سناب|ساوند)(?:\s+|$)(.*)")
async def all_social_dl(event):
    """محرك موحد لتحميل جميع منصات التواصل"""
    platform = event.pattern_match.group(1)
    url = event.pattern_match.group(2).strip()
    if not url: return await edit_delete(event, f"**⤶ يرجى وضع رابط {platform}**")
    
    zed = await edit_or_reply(event, f"**⪼ جاري التحميل من {platform} ... 📥**")
    mode = "audio" if platform == "ساوند" else "video"
    path, thumb, info = await venom_download(url, mode)
    
    if path and path.exists():
        if mode == "audio":
            attr = DocumentAttributeAudio(duration=int(info.get('duration', 0)), title=info.get('title', platform), performer="𝙑𝙚𝙣𝙤𝙢")
            await event.client.send_file(event.chat_id, file=str(path), thumb=str(thumb) if thumb else None, attributes=[attr], reply_to=await reply_id(event))
        else:
            await event.client.send_file(event.chat_id, file=str(path), supports_streaming=True, reply_to=await reply_id(event))
        await zed.delete()
        path.unlink(missing_ok=True)
    else: await zed.edit(f"**⤶ فشل التحميل من {platform}.**")

@zq_lo.rep_cmd(pattern="صور(?:\s+|$)(.*)")
async def search_pic(event):
    query = event.pattern_match.group(1).strip()
    if not query: return await edit_delete(event, "**⤶ اكتب ما تريد البحث عنه**")
    await inline_search_send(event, "pic", query, "**⤶ لم أجد صوراً لهذا البحث.**")

@zq_lo.rep_cmd(pattern="متحركه(?:\s+|$)(.*)")
async def search_gif(event):
    query = event.pattern_match.group(1).strip()
    if not query: return await edit_delete(event, "**⤶ اكتب ما تريد البحث عنه**")
    await inline_search_send(event, "gif", query, "**⤶ لم أجد متحركات لهذا البحث.**")


# ==========================================
# 4. رد الأزرار وقائمة المساعدة
# ==========================================

@zq_lo.tgbot.on(events.CallbackQuery(data=re.compile(b"ytdl_(audio|video)")))
async def on_ytdl_cb(event):
    if event.sender_id != zq_lo.uid:
        return await event.answer("هذا الأمر للمالك فقط! ❌", alert=True)
        
    action = event.data_match.group(1).decode()
    cache_key = f"{event.chat_id}_{event.message_id}"
    
    if not (url := YT_DL_CACHE.get(cache_key)):
        return await event.answer("انتهت صلاحية هذا الزر ❌", alert=True)
        
    await event.edit("**⪼ جاري المعالجة والتحميل ... ⚡**")
    path, thumb, info = await venom_download(url, action)
    
    if not path or not path.exists():
        return await event.edit("**⤶ حدث خطأ أثناء التحميل، المقطع محظور أو غير متاح.**")
        
    attr = [DocumentAttributeAudio(duration=int(info.get('duration',0)), title=info.get('title', 'صوت'), performer="𝙑𝙚𝙣𝙤𝙢")] if action == "audio" else []
    await zq_lo.send_file(
        event.chat_id, file=str(path), thumb=str(thumb) if thumb else None,
        attributes=attr, supports_streaming=(action == "video")
    )
    
    await event.delete()
    path.unlink(missing_ok=True); (thumb.unlink(missing_ok=True) if thumb else None)

@zq_lo.rep_cmd(pattern="اوامر التحميل$")
async def help_menu(event):
    menu = """ᯓ 𝙑𝙚𝙣𝙤𝙢 𝗨𝘀𝗲𝗿𝗯𝗼𝘁 - اوامــــر الـبـحــــث والـتـحـمـيــــل .
⋆┄─┄─┄─┄┄─┄─┄─┄─┄┄⋆
⎞𝟏⎝ `.بحث` + اســــم الاغـنـيــــة
⎞𝟐⎝ `.يوت` + كـلـمــــة او بـالــــرد
⎞𝟑⎝ `.فيديو` + اســــم الـمـقـطــــع
⎞𝟒⎝ `.تحميل صوت` + رابــــط
⎞𝟓⎝ `.تحميل فيديو` + رابــــط
⎞𝟔⎝ `.يوتيوب` + كـلـمــــة
⎞𝟕⎝ `.انستا` + رابــــط
⎞𝟖⎝ `.صور` + كـلـمــــة
⎞𝟗⎝ `.متحركه` + كـلـمــــة
⎞𝟏𝟎⎝ `.تيك` + رابــــط
⎞𝟏𝟏⎝ `.لايكي` + رابــــط
⎞𝟏𝟐⎝ `.فيس` + رابــــط
⎞𝟏𝟑⎝ `.تويتر` + رابــــط
⎞𝟏𝟒⎝ `.بنترست` + رابــــط
⎞𝟏𝟓⎝ `.سناب` + رابــــط
⎞𝟏𝟔⎝ `.ساوند` + رابــــط

 𓆩 𝙑𝙚𝙣𝙤𝙢 𝗨𝘀𝗲𝗿𝗯𝗼𝘁 𓆪"""
    await edit_or_reply(event, menu)
