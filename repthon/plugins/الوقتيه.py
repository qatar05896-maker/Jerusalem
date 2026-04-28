# Venom
# Copyright (C) 2026 Abdullah (Venom). All Rights Reserved
#
# This file is a part of < https://github.com/VenomArabic/VenomAr/ >
#
""" 
وصـف الملـف : اوامـر تغييـر زخـارف البروفايـل والاسـم الوقـتي
كود حديث (إصدار 2026) - خفيف، سريع، ومحسّن
حقـوق للتـاريخ : @Venom
كتـابـة وتطويـر : عبـدالله
"""

import asyncio
import os
import time

# -------------------------------------------------------------
# إجبار السيرفر والبوت على العمل بتوقيت مصر تلقائياً بدون فارات
os.environ['TZ'] = 'Africa/Cairo'
try:
    time.tzset()
except AttributeError:
    pass
# -------------------------------------------------------------

from repthon import zq_lo
from ..Config import Config
from ..core.managers import edit_or_reply
from ..sql_helper.globals import addgvar, gvarstatus

plugin_category = "الادوات"

# ==================== ( القواميس الذكية للخطوط ) ==================== #
# قاموس زخارف صور البروفايل وخطوط الحقوق
FONTS_MAP = {
    "1": "ZThon.ttf",
    "2": "Starjedi.ttf",
    "3": "Papernotes.ttf",
    "4": "Terserah.ttf",
    "5": "Photography Signature.ttf",
    "6": "Austein.ttf",
    "7": "Dream MMA.ttf",
    "8": "EASPORTS15.ttf",
    "9": "KGMissKindergarten.ttf",
    "10": "212 Orion Sans PERSONAL USE.ttf",
    "11": "PEPSI_pl.ttf",
    "12": "Paskowy.ttf",
    "13": "Cream Cake.otf",
    "14": "Hello Valentina.ttf",
    "15": "Alien-Encounters-Regular.ttf",
    "16": "Linebeam.ttf",
    "17": "EASPORTS15.ttf"
}

# قاموس زخارف الاسم الوقتي
TIME_FONTS_MAP = {
    "1": "𝟭𝟮𝟯𝟰𝟱𝟲𝟳𝟴𝟵𝟬",
    "2": "𝟏𝟐𝟑𝟒𝟓𝟔𝟕𝟖𝟗𝟎",
    "3": "١٢٣٤٥٦٧٨٩٠",
    "4": "₁₂₃₄₅₆₇₈₉₀",
    "5": "¹²³⁴⁵⁶⁷⁸⁹⁰",
    "6": "➊➋➌➍➎➏➐➑➒✪",
    "7": "❶❷❸❹❺❻❼❽❾⓿",
    "8": "➀➁➂➃➄➅➆➇➈⊙",
    "9": "⓵⓶⓷⓸⓹⓺⓻⓼⓽⓪",
    "10": "①②③④⑤⑥⑦⑧⑨⓪",
    "11": "𝟣𝟤𝟥𝟦𝟧𝟨𝟩𝟪𝟫𝟢",
    "12": "𝟷𝟸𝟹𝟺𝟻𝟼𝟽𝟾𝟿𝟶",
    "13": "𝟙𝟚𝟛𝟜𝟝𝟞𝟟𝟠𝟡𝟘",
    "14": "１２３４５６７８９０"
}

Venom_cmd = (
    "𓆩 [𝗦𝗼𝘂𝗿𝗰𝗲 𝗩𝗲𝗻𝗼𝗺 - اوامـر الفـارات](t.me/Venom) 𓆪\n\n"
    "**✾╎قائـمه اوامـر تغييـر زخـارف البروفايـل + الاسـم الوقـتي بأمـر واحـد فقـط - المطور عبـدالله 🦾 :** \n\n"
    "⪼ `.وقتيه 1` / `.الوقتي 1`\n"
    "⪼ `.وقتيه 2` / `.الوقتي 2`\n"
    "⪼ `.وقتيه 3` / `.الوقتي 3`\n"
    "⪼ `.وقتيه 4` / `.الوقتي 4`\n"
    "⪼ `.وقتيه 5` / `.الوقتي 5`\n"
    "⪼ `.وقتيه 6` / `.الوقتي 6`\n"
    "⪼ `.وقتيه 7` / `.الوقتي 7`\n"
    "⪼ `.وقتيه 8` / `.الوقتي 8`\n"
    "⪼ `.وقتيه 9` / `.الوقتي 9`\n"
    "⪼ `.وقتيه 10` / `.الوقتي 10`\n"
    "⪼ `.وقتيه 11` / `.الوقتي 11`\n"
    "⪼ `.وقتيه 12` / `.الوقتي 12`\n"
    "⪼ `.وقتيه 13` / `.الوقتي 13`\n"
    "⪼ `.وقتيه 14` / `.الوقتي 14`\n"
    "⪼ `.وقتيه 15`\n"
    "⪼ `.وقتيه 16`\n"
    "⪼ `.وقتيه 17`\n\n"
    "**✾╎لـ رؤيـة زغـارف البروفايـل الوقتـي ↶** [⦇  اضـغـط هنــا  ⦈](t.me/Venom/20) \n"
    "**✾╎لـ رؤيـة زغـارف الاســم الوقتـي ↶** [⦇  اضـغـط هنــا  ⦈](t.me/Venom/24) \n\n"
    "🛃 سيتـم اضـافة المزيـد من الزغـارف بالتحديثـات الجـايـه\n\n"
    "\n𓆩 [𐇮 𓆩✗ ¦ ↱ 𝐴𝑏𝑑𝑢𝑙𝑙𝑎ℎ ↲ ¦ ✗𓆪 𐇮](t.me/Venom) 𓆪"
)


@zq_lo.rep_cmd(pattern="وقتيه(?:\s|$)([\s\S]*)")
async def set_profile_font(event):
    input_str = event.pattern_match.group(1).strip()
    
    if not input_str or input_str not in FONTS_MAP:
        return await edit_or_reply(event, "**✾╎عذراً، الرجاء اختيار رقم صحيح من 1 إلى 17.**")

    zed = await edit_or_reply(event, "**✾╎جـاري اضـافة زخـرفـة الوقتيـه لـ بوتـك 💞🦾 . . .**")
    zinfo = f"repthon/helpers/styles/{FONTS_MAP[input_str]}"
    
    await asyncio.sleep(1)
    
    action_text = "اضـافـة" if gvarstatus("DEFAULT_PIC") is None else "تغييـر"
    await zed.edit(f"**✾╎تم {action_text} زغـرفـة البروفـايل الوقـتي {input_str} بنجـاح ☑️**\n\n**✾╎الان قـم بـ ارسـال الامـر ↶** `.البروفايل` **لـ بـدء البروفـايل الوقتـي . .**")
    addgvar("DEFAULT_PIC", zinfo)


@zq_lo.rep_cmd(pattern="الوقتي(?:\s|$)([\s\S]*)")
async def set_time_font(event):
    input_str = event.pattern_match.group(1).strip()
    
    if not input_str or input_str not in TIME_FONTS_MAP:
        return await edit_or_reply(event, "**✾╎عذراً، الرجاء اختيار رقم صحيح من 1 إلى 14.**")

    zed = await edit_or_reply(event, "**✾╎جـاري اضـافة زخـرفـة الوقتيـه لـ بوتـك 💞🦾 . . .**")
    zinfo = TIME_FONTS_MAP[input_str]
    
    await asyncio.sleep(1)
    
    action_text = "إضـافة" if gvarstatus("BA_FN") is None else "تغييـر"
    await zed.edit(f"**✾╎تم {action_text} زغـرفة الاسـم الوقتـي .. بنجـاح✓**\n**✾╎نـوع الزخـرفـه {zinfo} **\n**✾╎الان ارسـل ↶** `.الاسم تلقائي`")
    addgvar("BA_FN", zinfo)


@zq_lo.rep_cmd(pattern="اوامر الوقتي")
async def cmd(event):
    await edit_or_reply(event, Venom_cmd)


@zq_lo.rep_cmd(pattern="الخط(?:\s|$)([\s\S]*)")
async def set_watermark_font(event):
    input_str = event.pattern_match.group(1).strip()
    
    if not input_str or input_str not in FONTS_MAP:
        return await edit_or_reply(event, "**✾╎عذراً، الرجاء اختيار رقم صحيح من 1 إلى 17.**")

    zed = await edit_or_reply(event, "**✾╎جـاري اضـافة زخـرفـة خـط الحقـوق لـ بوتـك 💞🦾 . . .**")
    zinfo = f"repthon/helpers/styles/{FONTS_MAP[input_str]}"
    
    await asyncio.sleep(1)
    
    action_text = "اضـافـة" if gvarstatus("ZED_FONTS") is None else "تغييـر"
    await zed.edit(f"**✾╎تم {action_text} زغـرفـة خـط الحقـوق {input_str} بنجـاح ☑️**\n\n**✾╎الان قـم بـ ارسـال الامـر ↶** `.حقوق` **+ كلمـه بالـرد ع (صوره-ملصق-متحركه-فيديو) . .**")
    addgvar("ZED_FONTS", zinfo)
