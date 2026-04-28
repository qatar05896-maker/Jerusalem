# Venom
# Copyright (C) 2026 Abdullah (Venom). All Rights Reserved
# < https://t.me/Venom >
#
""" 
وصـف الملـف : اوامـر تغييـر زخـارف البروفايـل والاسـم الوقـتي
كود حديث (إصدار 2026) - خفيف، سريع، ومحسّن
حقـوق للتـاريخ : @Venom
كتـابـة وتطويـر : عبـدالله
"""

import asyncio
import os
import shutil
import time
import requests
from datetime import datetime
import pytz

from PIL import Image, ImageDraw, ImageFont
from telethon.errors import FloodWaitError
from telethon.tl import functions

from ..Config import Config
from ..sql_helper.globals import addgvar, delgvar, gvarstatus
from . import edit_delete, zq_lo, logging

plugin_category = "الادوات"
DEFAULTUSER = gvarstatus("ALIVE_NAME") or Config.ALIVE_NAME
LOGS = logging.getLogger("𝙑𝙚𝙣𝙤𝙢")
CHANGE_TIME = int(gvarstatus("CHANGE_TIME")) if gvarstatus("CHANGE_TIME") else 60

# مسارات الصور
TEMP_DIR = os.path.join(os.getcwd(), "repthon")
os.makedirs(TEMP_DIR, exist_ok=True)
digitalpic_path = os.path.join(TEMP_DIR, "digital_pic.png")
autophoto_path = os.path.join(TEMP_DIR, "photo_pfp.png")

# متغيرات الأوامر
NAUTO = gvarstatus("R_NAUTO") or "(الاسم تلقائي|الاسم الوقتي|اسم وقتي|اسم تلقائي)"
PAUTO = gvarstatus("R_PAUTO") or "(البروفايل تلقائي|الصوره الوقتيه|الصورة الوقتية|صوره وقتيه|البروفايل)"
BAUTO = gvarstatus("R_BAUTO") or "(البايو تلقائي|البايو الوقتي|بايو وقتي|نبذه وقتيه|النبذه الوقتيه)"

# ----------------- دوال مساعدة ----------------- #
def get_egypt_time():
    """جلب الوقت بتوقيت مصر حصراً"""
    tz = pytz.timezone("Africa/Cairo")
    return datetime.now(tz).strftime("%I:%M")

def translate_time(time_str):
    """ترجمة الأرقام للزخرفة المحددة بسرعة فائقة"""
    standard_nums = "1234567890"
    custom_font = gvarstatus("BA_FN") or "𝟭𝟮𝟯𝟰𝟱𝟲𝟳𝟴𝟵𝟬"
    trans_table = str.maketrans(standard_nums, custom_font[:10])
    return time_str.translate(trans_table)

async def download_image(url, path):
    """تحميل الصورة في الخلفية بدون تجميد البوت"""
    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(None, requests.get, url)
    if response.status_code == 200:
        with open(path, 'wb') as f:
            f.write(response.content)
# ----------------------------------------------- #


async def digitalpicloop():
    i = 0
    while gvarstatus("digitalpic") == "true":
        if not os.path.exists(digitalpic_path):
            digitalpfp = gvarstatus("DIGITAL_PIC")
            if digitalpfp:
                await download_image(digitalpfp, digitalpic_path)
        
        repfont = gvarstatus("DEFAULT_PIC") or "repthon/helpers/styles/Papernotes.ttf"
        
        if os.path.exists(digitalpic_path):
            shutil.copy(digitalpic_path, autophoto_path)
            current_time = get_egypt_time()
            
            try:
                img = Image.open(autophoto_path)
                drawn_text = ImageDraw.Draw(img)
                fnt = ImageFont.truetype(repfont, 35)
                drawn_text.text((140, 70), current_time, font=fnt, fill=(255, 255, 255))
                img.save(autophoto_path)
                
                file = await zq_lo.upload_file(autophoto_path)
                if i > 0:
                    # مسح الصورة القديمة حتى لا يمتلئ الحساب
                    await zq_lo(functions.photos.DeletePhotosRequest(await zq_lo.get_profile_photos("me", limit=1)))
                i += 1
                await zq_lo(functions.photos.UploadProfilePhotoRequest(file))
                os.remove(autophoto_path)
            except Exception as e:
                LOGS.error(f"خطأ في صورة البروفايل: {e}")
        
        await asyncio.sleep(CHANGE_TIME)


async def autoname_loop():
    while gvarstatus("autoname") == "true":
        HM = get_egypt_time()
        styled_time = translate_time(HM)
        REPT = gvarstatus("CUSTOM_ALIVE_EMZED") or ""
        name = f"{REPT}{styled_time}"
        
        try:
            await zq_lo(functions.account.UpdateProfileRequest(last_name=name))
        except FloodWaitError as ex:
            LOGS.warning(f"انتظار فلود الاسم: {ex.seconds} ثانية")
            await asyncio.sleep(ex.seconds)
        
        await asyncio.sleep(CHANGE_TIME)


async def autobio_loop():
    while gvarstatus("autobio") == "true":
        HM = get_egypt_time()
        styled_time = translate_time(HM)
        DEFAULTUSERBIO = gvarstatus("DEFAULT_BIO") or "الحمد الله على كل شئ - @Venom"
        bio = f"{DEFAULTUSERBIO} ⏐ {styled_time}"
        
        try:
            await zq_lo(functions.account.UpdateProfileRequest(about=bio))
        except FloodWaitError as ex:
            LOGS.warning(f"انتظار فلود البايو: {ex.seconds} ثانية")
            await asyncio.sleep(ex.seconds)
            
        await asyncio.sleep(CHANGE_TIME)


@zq_lo.rep_cmd(pattern=f"{PAUTO}$")
async def start_auto_pic(event):
    if gvarstatus("DIGITAL_PIC") is None:
        return await edit_delete(event, "**- فار الصـورة الوقتيـه غيـر موجـود ؟!**\n**- ارسـل صورة ثم قم بالـرد عليهـا بالامـر :**\n\n`.اضف صورة الوقتي`")
    if gvarstatus("digitalpic") == "true":
        return await edit_delete(event, "**⎉╎البروفـايل الوقتـي .. مفعـل سابقـاً 🦾**")
    
    addgvar("digitalpic", "true")
    await edit_delete(event, "**⎉╎تـم بـدء البروفـايل الوقتـي .. بنجـاح ✓**")
    zq_lo.loop.create_task(digitalpicloop())


@zq_lo.rep_cmd(pattern=f"{NAUTO}$")
async def start_auto_name(event):
    if gvarstatus("autoname") == "true":
        return await edit_delete(event, "**⎉╎الاسـم الوقتـي .. مفعـل سابقـاً 🦾**")
    
    addgvar("autoname", "true")
    await edit_delete(event, "**⎉╎تـم بـدء الاسـم الوقتـي .. بنجـاح ✓**")
    zq_lo.loop.create_task(autoname_loop())


@zq_lo.rep_cmd(pattern=f"{BAUTO}$")
async def start_auto_bio(event):
    if gvarstatus("DEFAULT_BIO") is None:
        return await edit_delete(event, "**- فار النبـذة الوقتيـه غيـر موجـود ؟!**\n**- ارسـل نـص النبـذه ثم قم بالـرد عليهـا بالامـر :**\n\n`.اضف البايو`")
    if gvarstatus("autobio") == "true":
        return await edit_delete(event, "**⎉╎النبـذه الوقتـيه .. مفعلـه سابقـاً 🦾**")
    
    addgvar("autobio", "true")
    await edit_delete(event, "**⎉╎تـم بـدء الـنبذة الوقتيـه .. بنجـاح ✓**")
    zq_lo.loop.create_task(autobio_loop())


# كود واحد ذكي يدمج (إلغاء، إيقاف، إنهاء) بدل التكرار القديم
@zq_lo.rep_cmd(pattern="(الغاء|ايقاف|انهاء)(?:\s|$)([\s\S]*)")
async def stop_auto_features(event):
    target = event.pattern_match.group(2).strip()
    
    pic_cmds = ["البروفايل تلقائي", "البروفايل", "البروفايل التلقائي", "الصوره الوقتيه", "الصورة الوقتية"]
    name_cmds = ["الاسم تلقائي", "الاسم", "الاسم التلقائي", "الاسم الوقتي", "اسم الوقتي", "اسم وقتي", "اسم تلقائي"]
    bio_cmds = ["البايو تلقائي", "البايو", "البايو التلقائي", "البايو الوقتي", "النبذه الوقتيه", "النبذة الوقتية", "بايو الوقتي", "نبذه الوقتي"]
    
    if target in pic_cmds:
        if gvarstatus("digitalpic") == "true":
            delgvar("digitalpic")
            await event.client(functions.photos.DeletePhotosRequest(await event.client.get_profile_photos("me", limit=1)))
            return await edit_delete(event, "**⎉╎تم إيقـاف البروفـايل الوقتـي .. بنجـاح ✓**")
        return await edit_delete(event, "**⎉╎البروفـايل الوقتـي .. غيـر مفعـل اصـلاً ؟!**")
        
    elif target in name_cmds:
        if gvarstatus("autoname") == "true":
            delgvar("autoname")
            await event.client(functions.account.UpdateProfileRequest(last_name=DEFAULTUSER))
            return await edit_delete(event, "**⎉╎تم إيقـاف الاسـم الوقتـي .. بنجـاح ✓**")
        return await edit_delete(event, "**⎉╎الاسـم الوقتـي .. غيـر مفعـل اصـلاً ؟!**")
        
    elif target in bio_cmds:
        if gvarstatus("autobio") == "true":
            delgvar("autobio")
            DEFAULTUSERBIO = gvarstatus("DEFAULT_BIO") or "الحمد الله على كل شئ - @Venom"
            await event.client(functions.account.UpdateProfileRequest(about=DEFAULTUSERBIO))
            return await edit_delete(event, "**⎉╎تم إيقـاف النبـذه الوقتيـه .. بنجـاح ✓**")
        return await edit_delete(event, "**⎉╎النبـذه الوقتيـه .. غيـر مفعـله اصـلاً ؟!**")
        
    else:
        await edit_delete(event, "**⎉╎عذراً، حدد بشكل صحيح ما تريد إيقافه (الاسم تلقائي، البروفايل تلقائي، البايو تلقائي).**")


# تشغيل المهام في الخلفية
if gvarstatus("digitalpic") == "true":
    zq_lo.loop.create_task(digitalpicloop())
if gvarstatus("autoname") == "true":
    zq_lo.loop.create_task(autoname_loop())
if gvarstatus("autobio") == "true":
    zq_lo.loop.create_task(autobio_loop())
