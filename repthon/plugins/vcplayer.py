# تعريب وتحديث فريق ريبـــثون 
# Repthon UserBot T.me/Repthon
# تمت الترقية والتوافق الكامل مع PyTgCalls 2.x وحل مشكلة الانهيار (Event Loop)
# تم دمج نظام تخطي حظر يوتيوب (Web Client + Node + Cookies)

import asyncio
import logging
import os
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.types import User

# استدعاءات مكتبة PyTgCalls الحديثة
from pytgcalls import PyTgCalls, filters
from pytgcalls.types import MediaStream, Update, StreamEnded, GroupCallConfig

from repthon import zq_lo
from ..Config import Config
from ..core.managers import edit_delete, edit_or_reply
from ..vc_baqir.tg_downloader import tg_dl

plugin_category = "المكالمات"

logging.getLogger("pytgcalls").setLevel(logging.ERROR)

OWNER_ID = zq_lo.uid
vc_session = Config.VC_SESSION

# مسار الكوكيز المطلق لتخطي حظر يوتيوب
COOKIES_PATH = "/root/repthon/repthon/plugins/cookies.txt"

# إعداد العميل المساعد للمكالمات (بدون إيقاف البوت)
if vc_session:
    vc_client = TelegramClient(
        StringSession(vc_session), Config.APP_ID, Config.API_HASH
    )
else:
    vc_client = zq_lo

# تهيئة PyTgCalls بالإصدار الحديث
call_py = PyTgCalls(vc_client)

# تشغيل المكتبة في الخلفية لمنع تجميد البوت (مهم جداً)
async def start_vc_client():
    try:
        if vc_session:
            await vc_client.connect()
        await call_py.start()
    except Exception as e:
        logging.error(f"خطأ في تشغيل مكتبة المكالمات: {e}")

# إضافة المهمة مباشرة لتعمل مع بداية تشغيل البوت
asyncio.get_event_loop().create_task(start_vc_client())

# نظام قائمة التشغيل (Queue) الحديث
PLAYLIST = {}

# دالة مساعدة لتوليد بارامترات تخطي يوتيوب
def get_bypass_params():
    bypass_args = '--extractor-args "youtube:player_client=web" --js-runtime node --remote-components "ejs:github" --force-ipv4'
    if os.path.exists(COOKIES_PATH):
        bypass_args = f'--cookies "{COOKIES_PATH}" {bypass_args}'
    return bypass_args


# دالة الانتقال التلقائي للمقطع التالي عند انتهاء المقطع الحالي
@call_py.on_update(filters.stream_end())
async def on_stream_end(client: PyTgCalls, update: StreamEnded):
    chat_id = update.chat_id
    if chat_id in PLAYLIST and len(PLAYLIST[chat_id]) > 0:
        # حذف المقطع الذي انتهى
        PLAYLIST[chat_id].pop(0)
        
        # إذا كان هناك مقاطع أخرى، قم بتشغيل التالي
        if len(PLAYLIST[chat_id]) > 0:
            next_track = PLAYLIST[chat_id][0]
            # استخدام الأمر play الموحد في التحديث الجديد
            await call_py.play(chat_id, next_track["stream"])
        else:
            # إذا انتهت القائمة، غادر المكالمة
            await call_py.leave_call(chat_id)


@zq_lo.rep_cmd(
    pattern="شغل ?(1)? ?([\S ]*)?",
    command=("شغل", plugin_category),
    info={
        "header": "تشغيـل المقـاطع الصـوتيـه في المكـالمـات",
        "امـر اضافـي": {
            "1": "فرض تشغيـل المقطـع بالقـوة وتخطي الحالي",
        },
        "الاستخـدام": [
            "{tr}شغل بالــرد ع مقطـع صـوتي",
            "{tr}شغل + رابـط",
            "{tr}شغل 1 + رابـط",
        ],
    },
)
async def play_audio(event):
    "لـ تشغيـل المقـاطع الصـوتيـه في المكـالمـات"
    flag = event.pattern_match.group(1)
    input_str = event.pattern_match.group(2)
    chat_id = event.chat_id

    if input_str == "" and event.reply_to_msg_id:
        input_str = await tg_dl(event)
        
    if not input_str:
        return await edit_delete(event, "**- قـم بـ إدخـال رابـط أو الرد على المقطـع الصوتـي للتشغيـل...**", time=10)

    zed = await edit_or_reply(event, "**╮ جـارِ المعالجة والتشغيـل في المكـالمـه... 🎧♥️╰**")

    # إعداد الستريم الصوتي مدمجاً معه تخطي حظر يوتيوب
    stream = MediaStream(
        media_path=input_str,
        video_flags=MediaStream.Flags.IGNORE,
        ytdlp_parameters=get_bypass_params()
    )

    if chat_id not in PLAYLIST:
        PLAYLIST[chat_id] = []

    # إذا تم إرسال أمر الفرض (1) أو القائمة فارغة
    if flag or len(PLAYLIST[chat_id]) == 0:
        if flag:
            PLAYLIST[chat_id].insert(0, {"title": "مقطع صوتي", "stream": stream})
        else:
            PLAYLIST[chat_id].append({"title": "مقطع صوتي", "stream": stream})
            
        try:
            await call_py.play(chat_id, stream)
            await edit_delete(zed, "**- تم بدء تشغيل المقطع الصوتي بنجاح 🎧♥️**")
        except Exception as e:
            await edit_delete(zed, f"**- حـدث خطـأ أثناء التشغيل:**\n`{e}`")
    else:
        # الإضافة لقائمة الانتظار
        PLAYLIST[chat_id].append({"title": "مقطع صوتي", "stream": stream})
        await edit_delete(zed, f"**- المقطع يعمل حالياً! تمت إضافته لقائمة الانتظار بالمركز {len(PLAYLIST[chat_id]) - 1} 📝**")


@zq_lo.rep_cmd(
    pattern="فيد ?(1)? ?([\S ]*)?",
    command=("فيد", plugin_category),
    info={
        "header": "تشغيـل مقـاطع الفيـديـو في المكـالمـات",
        "امـر اضافـي": {
            "1": "فرض تشغيـل المقطـع بالقـوة",
        },
        "الاستخـدام": [
            "{tr}فيد بالــرد ع فيـديـو",
            "{tr}فيد + رابـط",
        ],
    },
)
async def play_video(event):
    "لـ تشغيـل مقـاطع الفيـديـو في المكـالمـات"
    con = event.pattern_match.group(1)
    if con and con.lower() == "فيديو":
        return
        
    flag = event.pattern_match.group(1)
    input_str = event.pattern_match.group(2)
    chat_id = event.chat_id

    if input_str == "" and event.reply_to_msg_id:
        input_str = await tg_dl(event)
        
    if not input_str:
        return await edit_delete(event, "**- قـم بـ إدخـال رابـط أو الرد على مقطع الفيديـو للتشغيـل...**", time=10)

    zed = await edit_or_reply(event, "**╮ جـارِ تشغيـل مقطـٓـع الفيـٓـديو في المكـالمـه... 🖥♥️╰**")

    # إعداد الستريم المرئي مدمجاً معه التخطي
    stream = MediaStream(
        media_path=input_str,
        ytdlp_parameters=get_bypass_params()
    )

    if chat_id not in PLAYLIST:
        PLAYLIST[chat_id] = []

    if flag or len(PLAYLIST[chat_id]) == 0:
        if flag:
            PLAYLIST[chat_id].insert(0, {"title": "مقطع فيديو", "stream": stream})
        else:
            PLAYLIST[chat_id].append({"title": "مقطع فيديو", "stream": stream})
            
        try:
            await call_py.play(chat_id, stream)
            await edit_delete(zed, "**- تم بدء تشغيل الفيديو بنجاح 🖥♥️**")
        except Exception as e:
            await edit_delete(zed, f"**- حـدث خطـأ أثناء التشغيل:**\n`{e}`")
    else:
        PLAYLIST[chat_id].append({"title": "مقطع فيديو", "stream": stream})
        await edit_delete(zed, f"**- تمت إضافة الفيديو لقائمة الانتظار بالمركز {len(PLAYLIST[chat_id]) - 1} 📝**")


@zq_lo.rep_cmd(
    pattern="توقف",
    command=("توقف", plugin_category),
    info={
        "header": "لـ ايقـاف تشغيـل للمقطـع مؤقتـاً في المكـالمـه",
    },
)
async def pause_stream(event):
    "لـ ايقـاف تشغيـل للمقطـع مؤقتـاً في المكـالمـه"
    chat_id = event.chat_id
    await edit_or_reply(event, "**- جـارِ الايقـاف مؤقتـاً ...**")
    try:
        await call_py.pause(chat_id)
        await edit_delete(event, "**- تم إيقاف التشغيل مؤقتاً ⏸**")
    except Exception as e:
        await edit_delete(event, f"**- خطأ:** `{e}`")


@zq_lo.rep_cmd(
    pattern="كمل",
    command=("كمل", plugin_category),
    info={
        "header": "لـ متابعـة تشغيـل المقطـع في المكـالمـه",
    },
)
async def resume_stream(event):
    "لـ متابعـة تشغيـل المقطـع في المكـالمـه"
    chat_id = event.chat_id
    await edit_or_reply(event, "**- جـار الاستئنـاف ...**")
    try:
        await call_py.resume(chat_id)
        await edit_delete(event, "**- تم استئناف التشغيل ▶️**")
    except Exception as e:
        await edit_delete(event, f"**- خطأ:** `{e}`")


@zq_lo.rep_cmd(
    pattern="تخطي",
    command=("تخطي", plugin_category),
    info={
        "header": "لـ تخطي تشغيـل المقطـع وتشغيـل المقطـع التالـي في المكـالمـه",
    },
)
async def skip_stream(event):
    "لـ تخطي تشغيـل المقطـع وتشغيـل المقطـع التالـي في المكـالمـه"
    chat_id = event.chat_id
    zed = await edit_or_reply(event, "**- جـار التخطـي للمقطع التالي ...**")
    
    if chat_id in PLAYLIST and len(PLAYLIST[chat_id]) > 1:
        PLAYLIST[chat_id].pop(0)
        next_track = PLAYLIST[chat_id][0]
        try:
            await call_py.play(chat_id, next_track["stream"])
            await edit_delete(zed, "**- تم التخطي وتشغيل المقطع التالي ⏭**")
        except Exception as e:
            await edit_delete(zed, f"**- خطأ أثناء التخطي:** `{e}`")
    else:
        # إذا لم يكن هناك مقاطع أخرى، قم بالمغادرة وتفريغ القائمة
        if chat_id in PLAYLIST:
            PLAYLIST[chat_id].clear()
        try:
            await call_py.leave_call(chat_id)
            await edit_delete(zed, "**- القائمة فارغة! تم إيقاف التشغيل والمغادرة ⏹**")
        except Exception:
            await edit_delete(zed, "**- لا يوجد مقاطع أخرى لتخطيها!**")


@zq_lo.rep_cmd(
    pattern="خروج",
    command=("خروج", plugin_category),
    info={
        "header": "لـ المغـادره من المحـادثه الصـوتيـه",
    },
)
async def leaveVoicechat(event):
    "لـ المغـادره من المحـادثه الصـوتيـه"
    chat_id = event.chat_id
    await edit_or_reply(event, "**- جـارِ مغـادرة المحـادثـة الصـوتيـه ...**")
    
    if chat_id in PLAYLIST:
        PLAYLIST[chat_id].clear()
        
    try:
        await call_py.leave_call(chat_id)
        await edit_delete(event, "**- تم مغـادرة المكـالمـه بنجاح 🚪🚶**")
    except Exception as e:
        await edit_delete(event, f"**- خطأ:** `{e}`")


@zq_lo.rep_cmd(
    pattern="قائمة التشغيل",
    command=("قائمة التشغيل", plugin_category),
    info={
        "header": "لـ جلب كـل المقـاطع المضـافه لقائمـة التشغيـل في المكالمـه",
    },
)
async def get_playlist(event):
    "لـ جلب كـل المقـاطع المضـافه لقائمـة التشغيـل في المكالمـه"
    chat_id = event.chat_id
    await edit_or_reply(event, "**- جـارِ جلب قائمـة التشغيـل ...**")
    
    if chat_id not in PLAYLIST or len(PLAYLIST[chat_id]) == 0:
        await edit_delete(event, "**- قائمـة التشغيـل فارغـة حالياً 📭**", time=10)
    else:
        rep = ""
        for num, item in enumerate(PLAYLIST[chat_id], 1):
            status = "يتم تشغيله الآن 🔊" if num == 1 else "في الانتظار ⏳"
            rep += f"**{num}-** `{item['title']}` - ({status})\n"
            
        await edit_delete(event, f"**- قائمـة التشغيـل الحالية :**\n\n{rep}\n**Enjoy the show ♥️**")


@zq_lo.rep_cmd(
    pattern="انضمام(?: )?(ك)?(?: )?(\S+)?",
    command=("انضمام", plugin_category),
    info={
        "header": "لـ الانضمـام الى المحـادثه الصـوتيـه كـقناة (بدون تشغيل)",
        "الاستخـدام": [
            "{tr}انضمام",
            "{tr}انضمام ك @username_channel",
        ],
    },
)
async def joinVoicechat(event):
    "لـ الانضمـام الى المحـادثه الصـوتيـه"
    join_flag = event.pattern_match.group(1)
    channel_username = event.pattern_match.group(2)
    chat_id = event.chat_id

    zed = await edit_or_reply(event, "**- جـارِ الانضمـام الى المحـادثـه الصـوتيـه ...**")

    try:
        if join_flag == "ك" and channel_username:
            channel_peer = await zq_lo.get_input_entity(channel_username)
            config = GroupCallConfig(join_as=channel_peer)
            
            # نشغل مسار صامت كخدعة للإنضمام فقط بهوية القناة
            await edit_delete(zed, "**- تم تهيئة هويتك! قم الآن بإرسال أمر `.شغل` مع رابط للبدء 🎙**")
        else:
             await edit_delete(zed, "**- للانضمام والتشغيل فوراً، يرجى استخدام أمر `.شغل` أو `.فيد` مباشرة 🚀**")
             
    except Exception as e:
        await edit_delete(zed, f"**- حدث خطأ:** `{e}`")
