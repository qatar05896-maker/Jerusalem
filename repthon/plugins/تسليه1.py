import asyncio
from collections import deque
from typing import List, Dict

# افترضت وجود هذه الاستيرادات بناءً على الكود الأصلي، يجب التأكد من توفرها في مشروعك
from repthon.core.logger import logging
from repthon import zq_lo
from ..Config import Config
from ..core.managers import edit_delete, edit_or_reply
from . import ALIVE_NAME, deEmojify

DEFAULTUSER = str(ALIVE_NAME) if ALIVE_NAME else "rep"

class AnimationData:
    """كلاس لتنظيم وحفظ بيانات الانيميشن (الفريمات)"""
    BOMB_FRAMES: List[str] = [
        "▪️▪️▪️▪️ \n▪️▪️▪️▪️ \n▪️▪️▪️▪️ \n▪️▪️▪️▪️ \n▪️▪️▪️▪️ \n",
        "💣💣💣💣 \n▪️▪️▪️▪️ \n▪️▪️▪️▪️ \n▪️▪️▪️▪️ \n▪️▪️▪️▪️ \n",
        "▪️▪️▪️▪️ \n💣💣💣💣 \n▪️▪️▪️▪️ \n▪️▪️▪️▪️ \n▪️▪️▪️▪️ \n",
        "▪️▪️▪️▪️ \n▪️▪️▪️▪️ \n💣💣💣💣 \n▪️▪️▪️▪️ \n▪️▪️▪️▪️ \n",
        "▪️▪️▪️▪️ \n▪️▪️▪️▪️ \n▪️▪️▪️▪️ \n💣💣💣💣 \n▪️▪️▪️▪️ \n",
        "▪️▪️▪️▪️ \n▪️▪️▪️▪️ \n▪️▪️▪️▪️ \n▪️▪️▪️▪️ \n💣💣💣💣 \n",
        "▪️▪️▪️▪️ \n▪️▪️▪️▪️ \n▪️▪️▪️▪️ \n▪️▪️▪️▪️ \n💥💥💥💥 \n",
        "▪️▪️▪️▪️ \n▪️▪️▪️▪️ \n▪️▪️▪️▪️ \n💥💥💥💥 \n💥💥💥💥 \n",
        "▪️▪️▪️▪️ \n▪️▪️▪️▪️ \n▪️▪️▪️▪️ \n▪️▪️▪️▪️ \n😵😵😵😵 \n",
        "`RIP PLOXXX......`"
    ]

    CHESS_FRAMES: List[str] = [
        "⬜⬜⬜⬜⬜⬜⬜\n⬜⬜⬜⬜⬜⬜⬜\n⬜⬜⬜⬜⬜⬜⬜\n⬜⬜⬜⬜⬜⬜⬜\n⬜⬜⬜⬜⬜⬜⬜\n⬜⬜⬜⬜⬜⬜⬜\n⬜⬜⬜⬜⬜⬜⬜",
        "⬜⬜⬜⬜⬜⬜⬜\n⬜⬜⬜⬜⬜⬜⬜\n⬜⬜⬜⬜⬜⬜⬜\n⬜⬜⬜⬛⬜⬜⬜\n⬜⬜⬜⬜⬜⬜⬜\n⬜⬜⬜⬜⬜⬜⬜\n⬜⬜⬜⬜⬜⬜⬜",
        "⬜⬜⬜⬜⬜⬜⬜\n⬜⬜⬜⬜⬜⬜⬜\n⬜⬜⬛⬛⬛⬜⬜\n⬜⬜⬛⬜⬛⬜⬜\n⬜⬜⬛⬛⬛⬜⬜\n⬜⬜⬜⬜⬜⬜⬜\n⬜⬜⬜⬜⬜⬜⬜",
        "⬜⬜⬜⬜⬜⬜⬜\n⬜⬛⬛⬛⬛⬛⬜\n⬜⬛⬜⬜⬜⬛⬜\n⬜⬛⬜⬜⬜⬛⬜\n⬜⬛⬜⬜⬜⬛⬜\n⬜⬛⬛⬛⬛⬛⬜\n⬜⬜⬜⬜⬜⬜⬜",
        "⬛⬛⬛⬛⬛⬛⬛\n⬛⬜⬜⬜⬜⬜⬛\n⬛⬜⬜⬜⬜⬜⬛\n⬛⬜⬜⬜⬜⬜⬛\n⬛⬜⬜⬜⬜⬜⬛\n⬛⬜⬜⬜⬜⬜⬛\n⬛⬛⬛⬛⬛⬛⬛",
        "⬛⬜⬛⬜⬛⬜⬛⬜\n⬜⬛⬜⬛⬜⬛⬜⬛\n⬛⬜⬛⬜⬛⬜⬛⬜\n⬜⬛⬜⬛⬜⬛⬜⬛\n⬛⬜⬛⬜⬛⬜⬛⬜\n⬜⬛⬜⬛⬜⬛⬜⬛\n⬛⬜⬛⬜⬛⬜⬛⬜\n⬜⬛⬜⬛⬜⬛⬜⬛",
        "⬜⬛⬜⬛⬜⬛⬜⬛\n⬛⬜⬛⬜⬛⬜⬛⬜\n⬜⬛⬜⬛⬜⬛⬜⬛\n⬛⬜⬛⬜⬛⬜⬛⬜\n⬜⬛⬜⬛⬜⬛⬜⬛\n⬛⬜⬛⬜⬛⬜⬛⬜\n⬜⬛⬜⬛⬜⬛⬜⬛\n⬛⬜⬛⬜⬛⬜⬛⬜",
        "⬜⬜⬜⬜⬜⬜⬜\n⬜⬛⬛⬛⬛⬛⬜\n⬜⬛⬜⬜⬜⬛⬜\n⬜⬛⬜⬛⬜⬛⬜\n⬜⬛⬜⬜⬜⬛⬜\n⬜⬛⬛⬛⬛⬛⬜\n⬜⬜⬜⬜⬜⬜⬜",
        "⬛⬛⬛⬛⬛⬛⬛\n⬛⬜⬜⬜⬜⬜⬛\n⬛⬜⬛⬛⬛⬜⬛\n⬛⬜⬛⬜⬛⬜⬛\n⬛⬜⬛⬛⬛⬜⬛\n⬛⬜⬜⬜⬜⬜⬛\n⬛⬛⬛⬛⬛⬛⬛",
        "⬜⬜⬜⬜⬜⬜⬜\n⬜⬛⬛⬛⬛⬛⬜\n⬜⬛⬜⬜⬜⬛⬜\n⬜⬛⬜⬛⬜⬛⬜\n⬜⬛⬜⬜⬜⬛⬜\n⬜⬛⬛⬛⬛⬛⬜\n⬜⬜⬜⬜⬜⬜⬜",
        "⬛⬛⬛⬛⬛⬛⬛\n⬛⬜⬜⬜⬜⬜⬛\n⬛⬜⬛⬛⬛⬜⬛\n⬛⬜⬛⬜⬛⬜⬛\n⬛⬜⬛⬛⬛⬜⬛\n⬛⬜⬜⬜⬜⬜⬛\n⬛⬛⬛⬛⬛⬛⬛",
        "⬜⬜⬜⬜⬜⬜⬜\n⬜⬛⬛⬛⬛⬛⬜\n⬜⬛⬜⬜⬜⬛⬜\n⬜⬛⬜⬛⬜⬛⬜\n⬜⬛⬜⬜⬜⬛⬜\n⬜⬛⬛⬛⬛⬛⬜\n⬜⬜⬜⬜⬜⬜⬜",
        "⬛⬛⬛⬛⬛\n⬛⬜⬜⬜⬛\n⬛⬜⬛⬜⬛\n⬛⬜⬜⬜⬛\n⬛⬛⬛⬛⬛",
        "⬜⬜⬜\n⬜⬛⬜\n⬜⬜⬜",
        "[👉🔴👈])"
    ]

    GANGSTA_FRAMES: List[str] = [
        "EVERyBOdy",
        "iZ",
        "GangSTur",
        "UNtIL ",
        "I",
        "ArRivE",
        "🔥🔥🔥",
        "EVERyBOdy iZ GangSTur UNtIL I ArRivE 🔥🔥🔥"
    ]

    BALL_FRAMES: List[str] = [
        "🔴⬛⬛⬜⬜\n⬜⬜⬜⬜⬜\n⬜⬜⬜⬜⬜",
        "⬜⬜⬛⬜⬜\n⬜⬛⬜⬜⬜\n🔴⬜⬜⬜⬜",
        "⬜⬜⬛⬜⬜\n⬜⬜⬛⬜⬜\n⬜⬜🔴⬜⬜",
        "⬜⬜⬛⬜⬜\n⬜⬜⬜⬛⬜\n⬜⬜⬜⬜🔴",
        "⬜⬜⬛⬛🔴\n⬜⬜⬜⬜⬜\n⬜⬜⬜⬜⬜",
        "⬜⬜⬛⬜⬜\n⬜⬜⬜⬛⬜\n⬜⬜⬜⬜🔴",
        "⬜⬜⬛⬜⬜\n⬜⬜⬛⬜⬜\n⬜⬜🔴⬜⬜",
        "⬜⬜⬛⬜⬜\n⬜⬛⬜⬜⬜\n🔴⬜⬜⬜⬜",
        "🔴⬛⬛⬜⬜\n⬜⬜⬜⬜⬜\n⬜⬜⬜⬜⬜",
    ]

    STUPID_FRAMES: List[str] = [
        "**- عقلك** ➡️ 🧠\n\n🧠         <(^_^ <)🗑",
        "**- عقلك** ➡️ 🧠\n\n🧠       <(^_^ <)  🗑",
        "**- عقلك** ➡️ 🧠\n\n🧠     <(^_^ <)    🗑",
        "**- عقلك** ➡️ 🧠\n\n🧠   <(^_^ <)      🗑",
        "**- عقلك** ➡️ 🧠\n\n🧠 <(^_^ <)        🗑",
        "**- عقلك** ➡️ 🧠\n\n🧠<(^_^ <)         🗑",
        "**- عقلك** ➡️ 🧠\n\n(> ^_^)>🧠         🗑",
        "**- عقلك** ➡️ 🧠\n\n  (> ^_^)>🧠       🗑",
        "**- عقلك** ➡️ 🧠\n\n    (> ^_^)>🧠     🗑",
        "**- عقلك** ➡️ 🧠\n\n      (> ^_^)>🧠   🗑",
        "**- عقلك** ➡️ 🧠\n\n        (> ^_^)>🧠 🗑",
        "**- عقلك** ➡️ 🧠\n\n          (> ^_^)>🧠🗑",
        "**- عقلك** ➡️ 🧠\n\n           (> ^_^)>🗑",
        "**- عقلك** ➡️ 🧠\n\n           <(^_^ <)🗑",
    ]

    CALL_FRAMES: List[str] = [
        "`Connecting To Telegram Headquarters...`",
        "`Call Connected.`",
        "`Telegram: Hello This is Telegram HQ. Who is this?`",
        f"`Me: Yo this is` {DEFAULTUSER} ,`Please Connect me to my lil bro, Pavel Durov `",
        "`User Authorised.`",
        "`Calling Pavel Durov `  `At +916969696969`",
        "`Private  Call Connected...`",
        "`Me: Hello Sir, Please Ban This Telegram Account.`",
        "`Pavel Durov : May I Know Who is This?`",
        f"`Me: Yo Brah, I Am` {DEFAULTUSER} ",
        "`Pavel Durov : OMG!!! Long time no see, Wassup cat...\nI'll Make Sure That Guy Account Will Get Blocked Within 24Hrs.`",
        "`Me: Thanks, See You Later Brah.`",
        "`Pavel Durov : Please Don't Thank Brah, Telegram Is Our's. Just Gimme A Call When You Become Free.`",
        "`Me: Is There Any Issue/Emergency???`",
        "`Pavel Durov : Yes Sur, There is A Bug in Telegram v69.6.9.\nI Am Not Able To Fix It. If Possible, Please Help Fix The Bug.`",
        "`Me: Send Me The App On My Telegram Account, I Will Fix The Bug & Send You.`",
        "`Pavel Durov : Sure Sur \nTC Bye Bye :)`",
        "`Private Call Disconnected.`",
    ]

class AnimationEngine:
    """كلاس لتنفيذ الانيميشن وتسهيل إعادة الاستخدام"""
    @staticmethod
    async def play(event, frames: List[str], interval: float, start_msg: str = None, link_preview: bool = False):
        """دالة عامة لتشغيل أي انيميشن"""
        message = await edit_or_reply(event, start_msg if start_msg else frames[0])
        for frame in frames:
            await asyncio.sleep(interval)
            await message.edit(frame, link_preview=link_preview)

# ----------------- الأوامر -----------------

@zq_lo.rep_cmd(pattern="غبي$")
async def animate_stupid(event):
    if event.fwd_from:
        return
    await AnimationEngine.play(event, AnimationData.STUPID_FRAMES, 1.0, "🧠.")

@zq_lo.rep_cmd(pattern=r"قنابل$")
async def animate_bombs(event):
    if event.fwd_from:
        return
    message = await edit_or_reply(event, "💣.")
    for i, frame in enumerate(AnimationData.BOMB_FRAMES):
        # محاكاة التوقيتات المختلفة في الكود الأصلي
        sleep_time = 1.0 if i == 6 else (2.0 if i == 9 else 0.5)
        await asyncio.sleep(sleep_time)
        await message.edit(frame)

@zq_lo.rep_cmd(pattern=r"اتصل$")
async def animate_call(event):
    if event.fwd_from:
        return
    await AnimationEngine.play(
        event, 
        AnimationData.CALL_FRAMES, 
        3.0, 
        "Calling Pavel Durov (ceo of telegram)......"
    )

@zq_lo.rep_cmd(pattern="طوبه$")
async def animate_ball(event):
    if event.fwd_from:
        return
    message = await edit_or_reply(event, "طوبه..طبت..طوبه..طبت..بيك...")
    await asyncio.sleep(4)
    # تشغيل الفريمات 3 مرات (كما في range(30) للكود الأصلي الذي يحتوي 10 فريمات)
    for _ in range(3):
        for frame in AnimationData.BALL_FRAMES:
            await asyncio.sleep(0.3)
            await message.edit(frame)

@zq_lo.rep_cmd(pattern=r"شطرنج$")
async def animate_chess(event):
    if event.fwd_from:
        return
    await AnimationEngine.play(event, AnimationData.CHESS_FRAMES, 0.3, "hypno....")

@zq_lo.rep_cmd(pattern=r"حلويات$")
async def animate_sweets(event):
    if event.fwd_from:
        return
    message = await edit_or_reply(event, "🍦")
    deq = deque(list("🍦🍧🍩🍪🎂🍰🧁🍫🍬🍭"))
    # تم تقليل العدد من 999 إلى 30 لمنع حظر تيليجرام (FloodWait)
    for _ in range(30):
        await asyncio.sleep(0.5)
        await message.edit("".join(deq))
        deq.rotate(1)

@zq_lo.rep_cmd(pattern="gangasta$")
async def animate_gangsta(event):
    if event.fwd_from:
        return
    message = await edit_or_reply(event, "gangasta")
    sleep_times = [0.3, 0.2, 0.5, 0.2, 0.3, 0.3, 0.3]
    for i, frame in enumerate(AnimationData.GANGSTA_FRAMES):
        if i > 0:
            await asyncio.sleep(sleep_times[i-1] if i-1 < len(sleep_times) else 0.3)
        await message.edit(frame)

@zq_lo.rep_cmd(pattern=r"charging$")
async def animate_charging(event):
    if event.fwd_from:
        return
    message = await edit_or_reply(event, "charging")
    # استخراج النص بشكل أكثر أماناً
    base_text = event.text.split("charging", 1)[-1].strip() + "\n\n`Tesla Wireless Charging (beta) Started...\nDevice Detected: Nokia 1100\nBattery Percentage:` "
    
    for k in range(10, 101, 10):
        await asyncio.sleep(1)
        await message.edit(base_text + str(k))
        
    await asyncio.sleep(1)
    await message.edit(
        "`Tesla Wireless Charging (beta) Completed...\nDevice Detected: Nokia 1100 (Space Grey Varient)\nBattery Percentage:` [100%](https://telegra.ph/file/a45aa7450c8eefed599d9.mp4) ",
        link_preview=True,
    )

@zq_lo.rep_cmd(pattern="تسليه1")
async def help_cmd(event):
    help_text = (
        "**Commands in animation1 are **\n"
        "  •  `.غبي`\n"
        "  •  `.قنابل`\n"
        "  •  `.اتصل`\n"
        "  •  `.شنو`\n"
        "  •  `.طوبه`\n"
        "  •  `.شطرنج`\n"
        "  •  `.حلويات`\n"
        "  •  `.gangasta`\n"
        "  •  `.charging` \n"
    )
    await edit_or_reply(event, help_text)
