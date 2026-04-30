# Venom Userbot - @S_G0C7
# Copyright (C) 2026 Abdullah (Venom). All Rights Reserved
# مـحـرك حـمـايـة الـخـاص (PM Security) | Modern Python 3.11+ Architecture

import random
import re
from datetime import datetime

from telethon import Button, functions
from telethon.events import CallbackQuery
from telethon.utils import get_display_name

from repthon import zq_lo
from repthon.core.logger import logging

# -- الاستدعاءات المباشرة (Absolute Imports) لضمان عدم وجود أخطاء مسارات --
from repthon.Config import Config
from repthon.core.managers import edit_delete, edit_or_reply
from repthon.helpers.utils import _format, get_user_from_event, reply_id
from repthon.sql_helper import global_collectionjson as sql
from repthon.sql_helper import global_list as sqllist
from repthon.sql_helper import pmpermit_sql
from repthon.sql_helper.globals import addgvar, delgvar, gvarstatus

plugin_category = "البوت"
LOGS = logging.getLogger(__name__)
cmdhd = Config.COMMAND_HAND_LER

class PMPERMIT:
    def __init__(self):
        self.TEMPAPPROVED = []

PMPERMIT_ = PMPERMIT()

# ==========================================
# 0. دوال قاعدة البيانات الحديثة (2026)
# ==========================================
def get_db_json(collection_name: str) -> dict:
    """دالة ذكية وآمنة لجلب البيانات من قاعدة البيانات"""
    try:
        coll = sql.get_collection(collection_name)
        return getattr(coll, "json", {}) if coll else {}
    except Exception:
        return {}

def save_db_json(collection_name: str, data: dict):
    """دالة ذكية لحفظ البيانات وتحديثها بأمان"""
    try:
        sql.del_collection(collection_name)
        sql.add_collection(collection_name, data, {})
    except Exception as e:
        LOGS.error(f"DB Save Error: {e}")

# ==========================================
# 1. محرك معالجة التكرار (Anti-Spam Engine)
# ==========================================
async def handle_repeated_pm(event, chat, list_name: str, reason_msg: str):
    """دالة مركزية لمعالجة تكرار الرسائل والخيارات"""
    PM_WARNS = get_db_json("pmwarns")
    PMMESSAGE_CACHE = get_db_json("pmmessagecache")
    
    if str(chat.id) not in PM_WARNS:
        if list_name == "pmoptions":
            text = "**⤶ اخـتـر أحـد الـخـيـارات بــدون تـكـرار ، وهـذا هــو تـحـذيـرك الأخـيـر**"
        else:
            text = "**⤶ بـرجـاء الانـتـظـار حـتـى يـتـم قـراءة رسـائـلـك.\n⤶ مـالـك الـحـسـاب سَــوف يـرد عـلـيـك عـنـد تـفـرغـه ..\n⤶ بـرجـاء عـدم تـكـرار الـرسـائـل لـتـجـنـب الـحـظـر**"
        await event.reply(text)
        PM_WARNS[str(chat.id)] = 1
        save_db_json("pmwarns", PM_WARNS)
        return None
        
    del PM_WARNS[str(chat.id)]
    save_db_json("pmwarns", PM_WARNS)
    
    if str(chat.id) in PMMESSAGE_CACHE:
        try:
            await event.client.delete_messages(chat.id, PMMESSAGE_CACHE[str(chat.id)])
            del PMMESSAGE_CACHE[str(chat.id)]
        except Exception:
            pass
            
    save_db_json("pmmessagecache", PMMESSAGE_CACHE)
    
    USER_BOT_WARN_ZERO = "**⤶ لـقـد حـذرتــك مـسـبـقـاً مـن تـكـرار الـرسـائـل ...**\n**⤶ تـم حـظـرك تـلـقـائـيـاً.** \n**⤶ إلـى أن يـأتـي مـالـك الـحـسـاب**"
    await event.reply(USER_BOT_WARN_ZERO)
    await event.client(functions.contacts.BlockRequest(chat.id))
    
    the_message = f"#حـمـايـة_الـخـاص\n[{get_display_name(chat)}](tg://user?id={chat.id}) تـم حـظـره\n**الـسـبـب:** __{reason_msg}__"
    sqllist.rm_from_list(list_name, chat.id)
    
    try:
        if Config.PRIVATE_GROUP_BOT_API_ID:
            return await event.client.send_message(Config.PRIVATE_GROUP_BOT_API_ID, the_message)
    except Exception:
        return


async def do_pm_permit_action(event, chat):
    reply_to_id = await reply_id(event)
    PM_WARNS = get_db_json("pmwarns")
    PMMESSAGE_CACHE = get_db_json("pmmessagecache")
    
    me = await event.client.get_me()
    mention = f"[{chat.first_name}](tg://user?id={chat.id})"
    my_mention = f"[{me.first_name}](tg://user?id={me.id})"
    
    if str(chat.id) not in PM_WARNS:
        PM_WARNS[str(chat.id)] = 0
        
    try:
        MAX_FLOOD_IN_PMS = int(gvarstatus("MAX_FLOOD_IN_PMS") or 6)
    except (ValueError, TypeError):
        MAX_FLOOD_IN_PMS = 6
        
    totalwarns = MAX_FLOOD_IN_PMS + 1
    warns = PM_WARNS[str(chat.id)] + 1
    remwarns = totalwarns - warns
    
    if PM_WARNS[str(chat.id)] >= MAX_FLOOD_IN_PMS:
        try:
            if str(chat.id) in PMMESSAGE_CACHE:
                await event.client.delete_messages(chat.id, PMMESSAGE_CACHE[str(chat.id)])
                del PMMESSAGE_CACHE[str(chat.id)]
        except Exception:
            pass
            
        custompmblock = gvarstatus("pmblock")
        if custompmblock:
            USER_BOT_WARN_ZERO = custompmblock.format(mention=mention, my_mention=my_mention, totalwarns=totalwarns, warns=warns, remwarns=remwarns)
        else:
            USER_BOT_WARN_ZERO = f"**⤶ لـقـد حـذرتـك مـسـبـقـاً مـن الـتـكـرار** \n**⤶ تـم حـظـرك تـلـقـائـيـاً .. الآن لا يـمـكـنـك إزعـاجـي**\n\n**⤶ تـحـيـاتـي** {my_mention} **"
            
        await event.reply(USER_BOT_WARN_ZERO)
        await event.client(functions.contacts.BlockRequest(chat.id))
        
        the_message = f"#حـمـايـة_الـخـاص\n[{get_display_name(chat)}](tg://user?id={chat.id}) تـم حـظـره\n**عـدد رسـائـلـه:** {PM_WARNS[str(chat.id)]}"
        
        del PM_WARNS[str(chat.id)]
        save_db_json("pmwarns", PM_WARNS)
        save_db_json("pmmessagecache", PMMESSAGE_CACHE)
        
        try:
            if Config.PRIVATE_GROUP_BOT_API_ID:
                return await event.client.send_message(Config.PRIVATE_GROUP_BOT_API_ID, the_message)
        except Exception:
            return
            
    custompmpermit = gvarstatus("pmpermit_txt")
    if custompmpermit:
        USER_BOT_NO_WARN = custompmpermit.format(mention=mention, my_mention=my_mention, totalwarns=totalwarns, warns=warns, remwarns=remwarns)
    elif gvarstatus("pmmenu") is None:
        USER_BOT_NO_WARN = f"𓆩𝙎𝙊𝙐𝙍𝘾𝙀 𝙍𝙀𝙋𝙏𝙃𝙊𝙉 - 𝑷𝑴 𝑺𝑬𝑪𝑼𝑹𝑰𝑻𝒀𓆪\n◐━─━─━─━─𝙍𝙀𝙋𝙏𝙃𝙊𝙉─━─━─━─━◐\n\n❞ **مـرحـبـاً** {mention} ❝\n\n**⤶ أنـا مـشـغـول حـالـيـاً، لا تـقـم بـإزعـاجـي وإلا سـوف يـتـم حـظـرك تـلـقـائـيـاً.....**\n**⤶ ❨ لـديـك** {warns}/{totalwarns} **تـحـذيـرات ❩**\n\n**⤶ فـقـط قـل سـبـب مـجـيـئـك أو اخـتـر أحـد الـخـيـارات بـالأسـفـل وانـتـظـر الـرد**"
    else:
        USER_BOT_NO_WARN = f"𓆩𝙎𝙊𝙐𝙍𝘾𝙀 𝙍𝙀𝙋𝙏𝙃𝙊𝙉 - 𝑷𝑴 𝑺𝑬𝑪𝑼𝑹𝑰𝑻𝒀𓆪\n◐━─━─━─━─𝙍𝙀𝙋𝙏𝙃𝙊𝙉─━─━─━─━◐\n\n❞ **مـرحـبـاً** {mention} ❝\n\n**⤶ أنـا مـشـغـول حـالـيـاً، لا تـقـم بـإزعـاجـي وإلا سـوف يـتـم حـظـرك تـلـقـائـيـاً.....**\n**⤶ ❨ لـديـك** {warns}/{totalwarns} **تـحـذيـرات ❩**\n\n**⤶ فـقـط قـل سـبـب مـجـيـئـك وانـتـظـر الـرد**"
        
    addgvar("pmpermit_text", USER_BOT_NO_WARN)
    PM_WARNS[str(chat.id)] += 1
    
    try:
        if gvarstatus("pmmenu") is None:
            results = await event.client.inline_query(Config.TG_BOT_USERNAME, "pmpermit")
            msg = await results[0].click(chat.id, reply_to=reply_to_id, hide_via=True)
        else:
            PM_PIC = gvarstatus("pmpermit_pic")
            CAT_IMG = random.choice(PM_PIC.split()) if PM_PIC else None
            if CAT_IMG:
                msg = await event.client.send_file(chat.id, CAT_IMG, caption=USER_BOT_NO_WARN, reply_to=reply_to_id)
            else:
                msg = await event.client.send_message(chat.id, USER_BOT_NO_WARN, reply_to=reply_to_id)
    except Exception:
        msg = await event.reply(USER_BOT_NO_WARN)
        
    try:
        if str(chat.id) in PMMESSAGE_CACHE:
            await event.client.delete_messages(chat.id, PMMESSAGE_CACHE[str(chat.id)])
            del PMMESSAGE_CACHE[str(chat.id)]
    except Exception:
        pass
        
    PMMESSAGE_CACHE[str(chat.id)] = msg.id
    save_db_json("pmwarns", PM_WARNS)
    save_db_json("pmmessagecache", PMMESSAGE_CACHE)


# ==========================================
# 2. مستقبل الأحداث (Events Listener)
# ==========================================
@zq_lo.rep_cmd(incoming=True, func=lambda e: e.is_private, edited=False, forwards=False)
async def on_new_private_message(event):
    if gvarstatus("pmpermit") is None:
        return
    chat = await event.get_chat()
    if chat.bot or chat.verified:
        return
    if pmpermit_sql.is_approved(chat.id):
        return
        
    # حماية المطورين التلقائية
    dev_ids = [1260465030, 5502537272]
    if event.chat_id in dev_ids:
        reason = "**- إنـه أحـد مـطـوري الـسـورس 𓆰**"
        PM_WARNS = get_db_json("pmwarns")
        if str(chat.id) in PM_WARNS:
            del PM_WARNS[str(chat.id)]
        start_date = str(datetime.now().strftime("%B %d, %Y"))
        pmpermit_sql.approve(chat.id, get_display_name(chat), start_date, chat.username, reason)
        return await event.client.send_message(chat, "**⪼ أطـلـق هـلا أحـد مـطـوري الـسـورس هـنـا إنـنـي مـحـظـوظ لـقـدومـك إلـي 𓆰**")
        
    if chat.id in PMPERMIT_.TEMPAPPROVED:
        return
        
    # فحص القوائم السوداء المؤقتة (Match Case - 3.10+)
    if str(chat.id) in sqllist.get_collection_list("pmspam"):
        return await handle_repeated_pm(event, chat, "pmspam", "اخـتـار خـيـار الإزعـاج وأرسـل مـرة أخـرى.")
    elif str(chat.id) in sqllist.get_collection_list("pmchat"):
        return await handle_repeated_pm(event, chat, "pmchat", "لـقـد اخـتـار خـيـار الـدردشـة واسـتـمـر بـتـكـرار الـرسـائـل.")
    elif str(chat.id) in sqllist.get_collection_list("pmrequest"):
        return await handle_repeated_pm(event, chat, "pmrequest", "لـقـد اخـتـار خـيـار الـطـلـب واسـتـمـر بـتـكـرار الـرسـائـل.")
    elif str(chat.id) in sqllist.get_collection_list("pmenquire"):
        return await handle_repeated_pm(event, chat, "pmenquire", "لـقـد اخـتـار خـيـار الاسـتـفـسـار واسـتـمـر بـتـكـرار الـرسـائـل.")
    elif str(chat.id) in sqllist.get_collection_list("pmoptions"):
        return await handle_repeated_pm(event, chat, "pmoptions", "لـم يـخـتـر أي مـن الـخـيـارات الـمـتـاحـة.")
        
    await do_pm_permit_action(event, chat)


@zq_lo.rep_cmd(outgoing=True, func=lambda e: e.is_private, edited=False, forwards=False)
async def you_dm_other(event):
    if gvarstatus("pmpermit") is None:
        return
    chat = await event.get_chat()
    if chat.bot or chat.verified:
        return
        
    ignore_lists = ["pmspam", "pmchat", "pmrequest", "pmenquire", "pmoptions"]
    if any(str(chat.id) in sqllist.get_collection_list(lst) for lst in ignore_lists):
        return
        
    # تجاهل أوامر الحماية نفسها
    if event.text and event.text.startswith((
        f"{cmdhd}بلوك", f"{cmdhd}رفض", f"{cmdhd}قبول", f"{cmdhd}da", f"{cmdhd}سماح",
        f"{cmdhd}tempapprove", f"{cmdhd}tempa", f"{cmdhd}tapprove", f"{cmdhd}ta",
    )):
        return
        
    PM_WARNS = get_db_json("pmwarns")
    if not pmpermit_sql.is_approved(chat.id) and str(chat.id) not in PM_WARNS:
        start_date = str(datetime.now().strftime("%B %d, %Y"))
        pmpermit_sql.approve(chat.id, get_display_name(chat), start_date, chat.username, "لـم يـتـم رفـضـه")
        
        PMMESSAGE_CACHE = get_db_json("pmmessagecache")
        if str(chat.id) in PMMESSAGE_CACHE:
            try:
                await event.client.delete_messages(chat.id, PMMESSAGE_CACHE[str(chat.id)])
            except Exception:
                pass
            del PMMESSAGE_CACHE[str(chat.id)]
        save_db_json("pmmessagecache", PMMESSAGE_CACHE)


# ==========================================
# 3. واجهة الأزرار التفاعلية (Inline Callbacks)
# ==========================================
@zq_lo.tgbot.on(CallbackQuery(data=re.compile(rb"show_pmpermit_options")))
async def on_plug_in_callback_query_handler(event):
    if event.query.user_id == event.client.uid:
        return await event.answer("⤶ عـذراً سـيـدي ، هـذه الـخـيـارات لـلـمـسـتـخـدم الـذي يـراسـلـك", cache_time=0, alert=True)
        
    text = "**⤶ حـسـنـاً عـزيـزي بـإمـكـانـك اخـتـيـار أحـد الـخـيـارات فـي الأسـفـل :**\n\n**⤶ اخـتـر خـيـار واحـد فـقـط لـنـعـرف سـبـب قـدومـك إلـى هـنـا **"
    buttons = [
        [Button.inline("⤶ لـ إسـتـفـسـار مـعـيـن", data=b"to_enquire_something")],
        [Button.inline("⤶ لـ طـلـب مـعـيـن", data=b"to_request_something")],
        [Button.inline("⤶ لـ الـدردشــه فـقـط", data=b"to_chat_with_my_master")],
        [Button.inline("⤶ لـ إزعـاجـي فـقـط", data=b"to_spam_my_master_inbox")],
    ]
    sqllist.add_to_list("pmoptions", event.query.user_id)
    PM_WARNS = get_db_json("pmwarns")
    if str(event.query.user_id) in PM_WARNS:
        del PM_WARNS[str(event.query.user_id)]
        save_db_json("pmwarns", PM_WARNS)
        
    await event.edit(text, buttons=buttons)


@zq_lo.tgbot.on(CallbackQuery(data=re.compile(rb"to_(enquire_something|request_something|chat_with_my_master|spam_my_master_inbox)")))
async def on_options_selected(event):
    if event.query.user_id == event.client.uid:
        return await event.answer("⤶ عـذراً سـيـدي ، هـذه الـخـيـارات لـلـمـسـتـخـدم الـذي يـراسـلـك", cache_time=0, alert=True)
        
    action = event.data_match.group(1).decode()
    
    match action:
        case "enquire_something":
            text = "**⤶ حـسـنـاً عـزيـزي ، تـم إرسـال طـلـبـك بـنـجـاح . لا تـقـم بـ إخـتـيـار خـيـار آخــر .**\n**⤶ سـيـتـم الـرد عـلـيـك عـنـد تـفـرغ الـمـالـك .**"
            sqllist.add_to_list("pmenquire", event.query.user_id)
        case "request_something":
            text = "**⤶ حـسـنـاً عـزيـزي .. قـمـت بـإبـلاغ مـالـك الـحـسـاب بـطـلـبـك**\n**⤶ لا تـكـرر الـرسـائـل حـالـيـاً لـ تـجـنـب الـحـظـر **"
            sqllist.add_to_list("pmrequest", event.query.user_id)
        case "chat_with_my_master":
            text = "**⤶ بـالـطـبـع عـزيـزي يـمـكـنـك الـتـحـدث مـع مـالـك الـحـسـاب \n\n⤶ حـالـيـاً أنـا مـشـغـول قـلـيـلاً  - عـنـد تـفـرغـي سـأكـلـمـك بـالـتـأكـيـد .**"
            sqllist.add_to_list("pmchat", event.query.user_id)
        case "spam_my_master_inbox":
            text = "**⤶ لـسـت مـتـفـرغـاً لـ تـراهـاتـك.\n\n⤶ وهـذا هـو تـحـذيـرك الأخـيـر إذا قـمـت بـإرسـال رسـالـة أخـرى فـ سـيـتـم حـظـرك تـلـقـائـيـاً **"
            sqllist.add_to_list("pmspam", event.query.user_id)

    PM_WARNS = get_db_json("pmwarns")
    if str(event.query.user_id) in PM_WARNS:
        del PM_WARNS[str(event.query.user_id)]
        save_db_json("pmwarns", PM_WARNS)
        
    sqllist.rm_from_list("pmoptions", event.query.user_id)
    await event.edit(text)


# ==========================================
# 4. أوامر المطور للتحكم (Commands)
# ==========================================
@zq_lo.rep_cmd(pattern="الحماي[هة] (تفعيل|تعطيل)$", command=("الحماية", plugin_category))
async def pmpermit_on(event):
    input_str = event.pattern_match.group(1)
    if input_str == "تفعيل":
        if gvarstatus("pmpermit") is None:
            addgvar("pmpermit", "true")
            await edit_delete(event, "**⌔∮ تـم تـفـعـيـل أمـر حـمـايـة الـخـاص .. بـنـجـاح ...**")
        else:
            await edit_delete(event, "** ⌔∮ أمـر حـمـايـة الـخـاص بـالـفـعـل .. مُـفـعـل **")
    else:
        if gvarstatus("pmpermit") is not None:
            delgvar("pmpermit")
            await edit_delete(event, "**⌔∮ تـم تـعـطـيـل أمـر حـمـايـة الـخـاص .. بـنـجـاح ...**")
        else:
            await edit_delete(event, "** ⌔∮ أمـر حـمـايـة الـخـاص بـالـفـعـل .. مُـعـطـل **")
        if gvarstatus("pmmenu") is not None:
            delgvar("pmmenu")
            

@zq_lo.rep_cmd(pattern="(قبول|سماح)(?:\s|$)([\s\S]*)", command=("سماح", plugin_category))
async def approve_p_m(event):
    if gvarstatus("pmpermit") is None:
        return await edit_delete(event, f"** ⌔∮ يـجـب تـفـعـيـل الـحـمـايـة أولاً بـإرسـال `{cmdhd}الحماية تفعيل`**")
        
    if event.is_private:
        user = await event.get_chat()
        reason = event.pattern_match.group(2)
    else:
        user, reason = await get_user_from_event(event, secondgroup=True)
        if not user: return
            
    reason = reason or "**⌔∮ لـم يـذكـر **"
    PM_WARNS = get_db_json("pmwarns")
    
    if not pmpermit_sql.is_approved(user.id):
        if str(user.id) in PM_WARNS:
            del PM_WARNS[str(user.id)]
            
        start_date = str(datetime.now().strftime("%B %d, %Y"))
        pmpermit_sql.approve(user.id, get_display_name(user), start_date, user.username, reason)
        
        for list_name in ["pmspam", "pmchat", "pmrequest", "pmenquire", "pmoptions"]:
            sqllist.rm_from_list(list_name, user.id)
                
        await edit_delete(event, f"⌔∮ [{user.first_name}](tg://user?id={user.id})\n**⌔∮ تـم الـسـمـاح لـه بـإرسـال الـرسـائـل ** \n **⌔∮ الـسـبـب :** {reason}")
        
        PMMESSAGE_CACHE = get_db_json("pmmessagecache")
        if str(user.id) in PMMESSAGE_CACHE:
            try:
                await event.client.delete_messages(user.id, PMMESSAGE_CACHE[str(user.id)])
            except Exception:
                pass
            del PMMESSAGE_CACHE[str(user.id)]
            
        save_db_json("pmwarns", PM_WARNS)
        save_db_json("pmmessagecache", PMMESSAGE_CACHE)
    else:
        await edit_delete(event, f"[{user.first_name}](tg://user?id={user.id}) \n**⌔∮ هـو بـالـفـعـل فـي قـائـمـة الـسـمـاح **")


@zq_lo.rep_cmd(pattern="(رف|رفض)(?:\s|$)([\s\S]*)", command=("رفض", plugin_category))
async def disapprove_p_m(event):
    if gvarstatus("pmpermit") is None:
        return await edit_delete(event, f"** ⌔∮ يـجـب تـفـعـيـل الـحـمـايـة أولاً بـإرسـال `{cmdhd}الحماية تفعيل`**")
        
    if event.is_private:
        user = await event.get_chat()
        reason = event.pattern_match.group(2)
    else:
        reason = event.pattern_match.group(2)
        if reason != "الكل":
            user, reason = await get_user_from_event(event, secondgroup=True)
            if not user: return
                
    if reason == "الكل":
        pmpermit_sql.disapprove_all()
        return await edit_delete(event, "**⌔∮ حـسـنـا تـم رفـض الـجـمـيـع .. بـنـجـاح **")
        
    reason = reason or "**⌔∮ لـم يـذكـر **"
    
    if pmpermit_sql.is_approved(user.id):
        pmpermit_sql.disapprove(user.id)
        await edit_or_reply(event, f"[{user.first_name}](tg://user?id={user.id})\n**⌔∮ تـم رفـضـه مـن إرسـال الـرسـائـل **\n**⌔∮ الـسـبـب :** {reason}")
    else:
        await edit_delete(event, f"[{user.first_name}](tg://user?id={user.id})\n **⌔∮ لــم تـتـم الـمـوافـقـة عـلـيـه مـسـبـقـاً **")


@zq_lo.rep_cmd(pattern="بلوك(?:\s|$)([\s\S]*)")
async def block_p_m(event):
    if event.is_private:
        user = await event.get_chat()
        reason = event.pattern_match.group(1)
    else:
        user, reason = await get_user_from_event(event)
        if not user: return
            
    reason = reason or "**⌔∮ لـم يـذكـر **"
    PM_WARNS = get_db_json("pmwarns")
    PMMESSAGE_CACHE = get_db_json("pmmessagecache")
    
    if str(user.id) in PM_WARNS:
        del PM_WARNS[str(user.id)]
    if str(user.id) in PMMESSAGE_CACHE:
        try:
            await event.client.delete_messages(user.id, PMMESSAGE_CACHE[str(user.id)])
        except Exception:
            pass
        del PMMESSAGE_CACHE[str(user.id)]
        
    if pmpermit_sql.is_approved(user.id):
        pmpermit_sql.disapprove(user.id)
        
    save_db_json("pmwarns", PM_WARNS)
    save_db_json("pmmessagecache", PMMESSAGE_CACHE)
    
    await event.client(functions.contacts.BlockRequest(user.id))
    await edit_or_reply(event, f"**- الـمـسـتـخـدم :** [{user.first_name}](tg://user?id={user.id}) **تـم حـظـره بـنـجـاح**\n**- الـسـبـب :** {reason}")


@zq_lo.rep_cmd(pattern="الغاء بلوك(?:\s|$)([\s\S]*)")
async def unblock_pm(event):
    if event.is_private:
        user = await event.get_chat()
        reason = event.pattern_match.group(1)
    else:
        user, reason = await get_user_from_event(event)
        if not user: return
            
    reason = reason or "**⌔∮ لـم يـذكـر **"
    await event.client(functions.contacts.UnblockRequest(user.id))
    await edit_or_reply(event, f"**- الـمـسـتـخـدم :** [{user.first_name}](tg://user?id={user.id}) **تـم إلـغـاء حـظـره بـنـجـاح**\n**- الـسـبـب :** {reason}")


@zq_lo.rep_cmd(pattern="المقبولين$")
async def get_approved_p_m(event):
    if gvarstatus("pmpermit") is None:
        return await edit_delete(event, f"** ⌔∮ يـجـب تـفـعـيـل الـحـمـايـة أولاً بـإرسـال `{cmdhd}الحماية تفعيل`**")
        
    approved_users = pmpermit_sql.get_all_approved()
    APPROVED_PMs = "**- قـائـمـة الـمـسـمـوح لـهـم ( الـمـقـبـولـيـن ) :**\n\n"
    
    if len(approved_users) > 0:
        for user in approved_users:
            APPROVED_PMs += f"**• الـاسـم :** {_format.mentionuser(user.first_name , user.user_id)}\n**- الأيـدي :** `{user.user_id}`\n**- الـتـاريـخ : **__{user.date}__\n**- الـسـبـب : **__{user.reason}__\n\n"
    else:
        APPROVED_PMs = "**- أنـت لـم تـوافـق عـلـى أي شـخـص بـعـد**"
        
    await edit_or_reply(
        event, APPROVED_PMs, file_name="قـائـمـة الـحـمـايـة.txt",
        caption="**- قـائـمـة الـمـسـمـوح لـهـم ( الـمـقـبـولـيـن )**\n\n**- سـورس 𝙑𝙚𝙣𝙤𝙢 **",
    )
