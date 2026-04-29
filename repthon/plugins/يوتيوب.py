# Venom Userbot - @S_G0C7
# محرك البحث والتحميل الذكي الشامل (نسخة 2026 - زراير + جودات ذكية)

import os
import asyncio
import re
import yt_dlp
from telethon import Button, events
from telethon.tl import types
from urlextract import URLExtract
from repthon import zq_lo
from ..core.managers import edit_delete, edit_or_reply
from ..helpers.utils import reply_id
from ..sql_helper.globals import addgvar, gvarstatus, delgvar

plugin_category = "utils"
extractor = URLExtract()
COOKIES_PATH = "repthon/HSL/cookies.txt"

# إنشاء مجلد التحميلات لو مش موجود
if not os.path.exists("temp"):
    os.makedirs("temp")

# ذاكرة مؤقتة لزراير الانلاين
YT_DL_CACHE = {}

# ==========================================
# 1. دوال الذكاء الصناعي لجلب المعلومات والتحميل
# ==========================================

async def search_yt(query, limit=1):
    urls = extractor.find_urls(query)
    opts = {
        "quiet": True, "noplaylist": True, "no_warnings": True,
        "extract_flat": True if limit > 1 else False,
    }
    if os.path.exists(COOKIES_PATH): opts["cookiefile"] = COOKIES_PATH
    
    def _fetch():
        with yt_dlp.YoutubeDL(opts) as ydl:
            if urls and limit == 1:
                return ydl.extract_info(urls[0], download=False)
            res = ydl.extract_info(f"ytsearch{limit}:{query}", download=False)
            if limit == 1:
                return res['entries'][0] if res and res.get('entries') else None
            return res['entries'] if res else []
            
    try:
        return await asyncio.get_event_loop().run_in_executor(None, _fetch)
    except Exception as e:
        return None

async def venom_yt_download(url, mode, size_mb=0):
    is_ultra = gvarstatus("VENOM_ULTRA_HQ")
    
    # تحديد صيغة التحميل بذكاء بناءً على طلبك
    if mode == "audio":
        format_str = "bestaudio[ext=m4a]/bestaudio"
    else: # video
        if is_ultra:
            format_str = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"
        else:
            # لو عدى 50 ميجا ينزل لـ 480، غير كده 720
            format_str = "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]" if size_mb <= 50 else "bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]"

    opts = {
        "format": format_str,
        "outtmpl": f"temp/%(id)s_%(title)s_{mode}.%(ext)s",
        "quiet": True, "no_warnings": True,
        "writethumbnail": True, # لجلب صورة الغلاف
    }
    if os.path.exists(COOKIES_PATH): opts["cookiefile"] = COOKIES_PATH

    def _dl():
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            base, _ = os.path.splitext(filename)
            
            # جلب مسار الصورة (الغلاف)
            thumb_path = None
            for t_ext in [".jpg", ".webp", ".png"]:
                if os.path.exists(base + t_ext):
                    thumb_path = base + t_ext
                    break
                    
            # تحديد الملف النهائي
            ext = "m4a" if mode == "audio" else "mp4"
            final_path = base + "." + ext
            if not os.path.exists(final_path): final_path = filename
            return final_path, thumb_path, info

    try:
        return await asyncio.get_event_loop().run_in_executor(None, _dl)
    except Exception as e:
        return None, None, None

# ==========================================
# 2. أوامر البحث والجودة
# ==========================================

@zq_lo.rep_cmd(pattern="ارفع الجودة")
async def toggle_hq(event):
    if gvarstatus("VENOM_ULTRA_HQ"):
        delgvar("VENOM_ULTRA_HQ")
        return await edit_or_reply(event, "**⤶ تم إيقاف وضع الجودة الفائقة (التحميل الذكي مفعل) ✅**\n**• الفيديوهات الأكبر من 50 ميجا ستُحمل بدقة 480p لسرعة الإرسال.**")
    addgvar("VENOM_ULTRA_HQ", "True")
    await edit_or_reply(event, "**⤶ تم تفعيل وضع الجودة الفائقة 🚀\n**• سيتم تحميل أعلى دقة دائماً متجاهلاً حجم الملف.**")

@zq_lo.rep_cmd(pattern="بحث(?: |$)(.*)")
async def yt_search_10(event):
    query = event.pattern_match.group(1)
    if not query: return await edit_delete(event, "**⤶ يرجى كتابة كلمة للبحث**")
    
    zed = await edit_or_reply(event, "**⪼ جاري البحث في يوتيوب ... 🔍**")
    res = await search_yt(query, limit=10)
    
    if not res: return await zed.edit("**⤶ لم يتم العثور على نتائج.**")
    
    text = f"**• أفضل 10 نتائج لـ ↶** `{query}`\n\n"
    for i, entry in enumerate(res, 1):
        url = entry.get('url') or entry.get('webpage_url')
        title = entry.get('title')
        text += f"**{i}.** [{title}]({url})\n"
        
    await zed.edit(text, link_preview=False)

# ==========================================
# 3. أوامر التنزيل المباشر (صوت / فيديو / ذكي)
# ==========================================

@zq_lo.rep_cmd(pattern="يوت(?: |$)(?!فيديو)(.*)")
async def yt_smart_dl(event):
    """التحميل الذكي (يوت) ينزل فيديو بذكاء مدمج بأعلى صوت"""
    query = event.pattern_match.group(1).strip() or (await event.get_reply_message()).text
    if not query: return await edit_delete(event, "**⤶ يرجى إدراج نص أو رابط**")
    
    zed = await edit_or_reply(event, "**⪼ جاري التحميل الذكي (فيديو) ... ⚡**")
    data = await search_yt(query, limit=1)
    if not data: return await zed.edit("**⤶ فشل العثور على المقطع.**")
    
    size_mb = (data.get('filesize') or data.get('filesize_approx') or 0) / (1024*1024)
    path, thumb, info = await venom_yt_download(data['webpage_url'], "video", size_mb)
    
    if path:
        await zed.edit("**⪼ جاري الرفع بنظام 8 خطوط ... 🚀**")
        quality_msg = "Ultra HQ" if gvarstatus("VENOM_ULTRA_HQ") else ("720p" if size_mb <= 50 else "480p")
        await event.client.send_file(
            event.chat_id, path, thumb=thumb, supports_streaming=True,
            caption=f"**• تم التحميل بنجاح ✅**\n**• العنوان ↶** `{info['title']}`\n**• الجودة ↶** `{quality_msg}`",
            reply_to=await reply_id(event)
        )
        await zed.delete()
        if os.path.exists(path): os.remove(path)
        if thumb and os.path.exists(thumb): os.remove(thumb)
    else:
        await zed.edit("**⤶ حدث خطأ أثناء التحميل.**")

@zq_lo.rep_cmd(pattern="(تنزيل صوت|صوت)(?: |$)(.*)")
async def yt_audio_dl(event):
    query = event.pattern_match.group(2).strip() or (await event.get_reply_message()).text
    if not query: return await edit_delete(event, "**⤶ يرجى إدراج نص أو رابط**")
    
    zed = await edit_or_reply(event, "**⪼ جاري استخراج الصوت بأعلى نقاء (m4a) ... 🎧**")
    data = await search_yt(query, limit=1)
    if not data: return await zed.edit("**⤶ فشل العثور على المقطع.**")
    
    path, thumb, info = await venom_yt_download(data['webpage_url'], "audio")
    
    if path:
        await zed.edit("**⪼ جاري الرفع ... 🚀**")
        await event.client.send_file(
            event.chat_id, path, thumb=thumb,
            caption=f"**• تم التنزيل بنجاح ✅**\n**• العنوان ↶** `{info['title']}`",
            attributes=[types.DocumentAttributeAudio(duration=int(info.get('duration', 0)), title=info.get('title'), performer="Venom")],
            reply_to=await reply_id(event)
        )
        await zed.delete()
        if os.path.exists(path): os.remove(path)
        if thumb and os.path.exists(thumb): os.remove(thumb)

@zq_lo.rep_cmd(pattern="(تنزيل فيديو|تنزيل فيد|يوت فيديو)(?: |$)(.*)")
async def yt_video_dl(event):
    query = event.pattern_match.group(2).strip() or (await event.get_reply_message()).text
    if not query: return await edit_delete(event, "**⤶ يرجى إدراج نص أو رابط**")
    
    zed = await edit_or_reply(event, "**⪼ جاري تجهيز وتحميل الفيديو ... 🎬**")
    data = await search_yt(query, limit=1)
    if not data: return await zed.edit("**⤶ فشل العثور على المقطع.**")
    
    size_mb = (data.get('filesize') or data.get('filesize_approx') or 0) / (1024*1024)
    path, thumb, info = await venom_yt_download(data['webpage_url'], "video", size_mb)
    
    if path:
        await zed.edit("**⪼ جاري الرفع ... 🚀**")
        await event.client.send_file(
            event.chat_id, path, thumb=thumb, supports_streaming=True,
            caption=f"**• تم التحميل بنجاح ✅**\n**• العنوان ↶** `{info['title']}`",
            reply_to=await reply_id(event)
        )
        await zed.delete()
        if os.path.exists(path): os.remove(path)
        if thumb and os.path.exists(thumb): os.remove(thumb)

# ==========================================
# 4. أمر التحميل بالزراير (يوتيوب / تنزيل)
# ==========================================

@zq_lo.rep_cmd(pattern="(يوتيوب|تنزيل)(?: |$)(.*)")
async def yt_inline_btn(event):
    query = event.pattern_match.group(2).strip()
    if not query and event.reply_to_msg_id:
        query = (await event.get_reply_message()).text
        
    if not query:
        return await edit_delete(event, "**⤶ يرجى إدراج اسم المقطع أو الرابط مع الأمر**")
        
    data = await search_yt(query, limit=1)
    if not data: return await edit_delete(event, "**⤶ فشل العثور على نتائج.**")
    
    url = data.get('webpage_url') or data.get('url')
    title = data.get('title', 'مقطع يوتيوب')
    
    buttons = [
        [Button.inline("صوت 🎧", data=f"ytdl_a")],
        [Button.inline("فيديو 🎬", data=f"ytdl_v")]
    ]
    
    try:
        msg = await zq_lo.tgbot.send_message(
            event.chat_id, 
            f"**╮ اختر نوع الملف الذي تريد تحميله ╰**\n**• المقطع ↶** `{title}`", 
            buttons=buttons
        )
        YT_DL_CACHE[f"{msg.chat_id}_{msg.id}"] = url
        await event.delete()
    except Exception as e:
        await edit_or_reply(event, "**⤶ يرجى إضافة البوت المساعد للمجموعة لاستخدام الأزرار، أو استخدم أوامر التنزيل المباشرة مثل:**\n`.صوت` **أو** `.فيديو`")

# معالج ضغطات زراير اليوتيوب
@zq_lo.tgbot.on(events.CallbackQuery(data=re.compile(b"ytdl_(a|v)")))
async def on_ytdl_cb(event):
    if event.sender_id != zq_lo.uid:
        return await event.answer("هذا الأمر للمالك فقط! ❌", alert=True)
        
    action = event.data_match.group(1).decode()
    cache_key = f"{event.chat_id}_{event.message_id}"
    url = YT_DL_CACHE.get(cache_key)
    
    if not url:
        return await event.answer("انتهت صلاحية هذا الزر ❌", alert=True)
        
    await event.edit("**⪼ جاري المعالجة والتحميل، انتظر قليلاً ... ⚡**")
    
    data = await search_yt(url, limit=1)
    size_mb = (data.get('filesize') or data.get('filesize_approx') or 0) / (1024*1024) if data else 0
    mode = "audio" if action == "a" else "video"
    
    path, thumb, info = await venom_yt_download(url, mode, size_mb)
    
    if not path:
        return await event.edit("**⤶ حدث خطأ أثناء التحميل أو الملف كبير جداً.**")
        
    # الرفع عبر الحساب الشخصي (Userbot) عشان السرعة والمظهر
    await zq_lo.send_file(
        event.chat_id, path, thumb=thumb,
        caption=f"**• تم التحميل بنجاح ✅**\n**• العنوان ↶** `{info['title']}`",
        attributes=[types.DocumentAttributeAudio(duration=int(info.get('duration',0)), title=info.get('title'), performer="Venom")] if mode == "audio" else [],
        supports_streaming=True if mode == "video" else False
    )
    
    await event.delete()
    if os.path.exists(path): os.remove(path)
    if thumb and os.path.exists(thumb): os.remove(thumb)
