# Venom Userbot - @S_G0C7
# Copyright (C) 2026 Abdullah (Venom). All Rights Reserved
# الـمـالـك: @S_G0C7
# مـديـر الـإضـافـات ومـراقـب الـأخـطـاء الـذـكـي (Smart Plugin Manager v2.0)

import asyncio
import importlib
import importlib.util
import os
import re
import sys
import traceback
from pathlib import Path

from telethon import TelegramClient
from ..core.logger import logging
from ..sql_helper.global_collection import (
    add_to_collectionlist,
    del_keyword_collectionlist,
    get_collectionlist_items,
)

# الإعدادات الأساسية
LOGS = logging.getLogger("VenomManager")
package_pattern = re.compile(r"([\w-]+)(?:=|<|>|!)")
BASE_PATH = Path("repthon/plugins")

# -----------------------------------------------------------------
# تـطـويـر 2026: نـظـام تـحـمـيـل الـإضـافـات الـشـامـل (Deep Scan Loader)
# -----------------------------------------------------------------

def load_module(file_path: Path):
    """تـحـمـيـل الـمـوديـول مـن أي مـسـار داخـل الـبـلـوجـنـز"""
    # 1. تـجـاهـل مـلـفـات الـنـظـام
    if file_path.name.startswith("__") or not file_path.name.endswith(".py"):
        return False

    # 2. تـحـويـل مـسـار الـمـلـف إلـى اسـم مـوديـول (مثال: plugins.media.مكالمات)
    relative_path = file_path.relative_to("repthon")
    module_name = str(relative_path).replace(os.path.sep, ".").replace(".py", "")
    short_name = file_path.stem

    try:
        # 3. تـجـهـيـز الـمـواصـفـات والـتـحـمـيـل
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        if spec is None:
            LOGS.error(f"[{short_name}] ❌ تـعـذر تـحـديـد مـواصـفـات الـمـلـف فـي: {file_path}")
            return False
            
        mod = importlib.util.module_from_spec(spec)
        mod.plugin_name = short_name
        spec.loader.exec_module(mod)
        
        # 4. تـسـجـيـل الـمـوديـول فـي نـظـام بـايـثـون
        sys.modules[module_name] = mod
        LOGS.info(f"[{short_name}] ✅ تـم الـتـحـمـيـل بـنـجـاح مـن {file_path.parent.name}")
        return True

    except Exception as e:
        # 5. نـظـام تـقـارير الـأخـطـاء الـمـطـور
        error_msg = f"\n❌ [خـطـأ كـريـتـيـكـال] فـشـل تـحـمـيـل: {file_path.name}\n"
        error_msg += f"➜ الـمـسـار: {file_path}\n"
        error_msg += f"➜ الـسـبـب: {e}\n"
        error_msg += f"➜ تـفـاصـيـل الـمـشـكـلـة:\n{traceback.format_exc()}"
        error_msg += "--------------------------------------------------"
        LOGS.error(error_msg)
        return False


def load_all_plugins():
    """الـوظـيـفـة الـمـسـؤولـة عـن كـسـح الـمـجـلـدات وتـحـمـيـل كـل شـيء"""
    LOGS.info("🚀 جـارِ بـدء الـمـسـح الـشـامـل لـلإضـافـات (بـمـا فـيـهـا الـمـجـلـدات الـفـرعـيـة)...")
    
    count = 0
    # البحث المتكرر (rglob) في كل الفولدرات
    for file in BASE_PATH.rglob("*.py"):
        if load_module(file):
            count += 1
            
    LOGS.info(f"✨ انـتـهـى الـمـسـح. تـم تـفـعـيـل {count} مـلـف بـنـجـاح.")


def remove_plugin(shortname):
    """إزالـة إضـافـة مـن الـذاكـرة (تـدـعـم الـمـسـارات الـعـمـيـقـة)"""
    try:
        from repthon import bot
        # نـبـحـث فـي كـل الـمـوديـولات الـمـحـمـلـة الـتـي تـنـتـهـي بـهـذا الـاسـم
        for name in list(sys.modules.keys()):
            if name.startswith("repthon.plugins.") and name.endswith(shortname):
                for i in reversed(range(len(bot._event_builders))):
                    ev, cb = bot._event_builders[i]
                    if cb.__module__ == name:
                        del bot._event_builders[i]
                del sys.modules[name]
                LOGS.info(f"[{shortname}] 🗑️ تـم إزالـة الـإضـافـة مـن الـنـظـام.")
                return True
        return False
    except Exception as e:
        LOGS.error(f"[{shortname}] ❌ خـطـأ أثـنـاء الـإزالـة: {e}")
        return False

# -----------------------------------------------------------------
# إدارة الـحـزم وإعـادة الـتـشـغـيـل (Fly.io Optimized)
# -----------------------------------------------------------------

async def get_pip_packages(requirements=None):
    """جـلـب قـائـمـة الـمـكـتـبـات الـمـثـبـتـة"""
    if requirements:
        packages = requirements
    else:
        cmd = await asyncio.create_subprocess_exec(
            sys.executable, "-m", "pip", "freeze",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, _ = await cmd.communicate()
        packages = stdout.decode("utf-8")
    tmp = package_pattern.findall(packages)
    return [package.lower() for package in tmp]


async def install_pip_packages(packages):
    """تـثـبـيـت مـكـتـبـات جـديـدة تـلـقـائـيـاً"""
    args = ["-m", "pip", "install", "--upgrade", "--user"]
    cmd = await asyncio.create_subprocess_exec(
        sys.executable, *args, *packages,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    await cmd.communicate()
    return cmd.returncode == 0


async def restart_script(client: TelegramClient, event):
    """إعـادة تـشـغـيـل ذـكـيـة تـحـفـظ حـالـة الـتـحـديـث"""
    try:
        # حـذف أي طـلـب ريـسـتـارت قـديـم
        ulist = get_collectionlist_items()
        for i in ulist:
            if i == "restart_update":
                del_keyword_collectionlist("restart_update")
        
        # تـسـجـيـل مـكـان الـريـسـتـارت لـيـرد الـبـوت بـعـد الـعـودة
        add_to_collectionlist("restart_update", [event.chat_id, event.id])
    except Exception as e:
        LOGS.error(f"Restart Storage Error: {e}")
        
    LOGS.info("♻️ جـارِ إعـادة تـشـغـيـل الـسـيـرفـر (Fly.io)...")
    # الـخـروج بـكـود 143 لـتـحـفـيـز Fly.io عـلـى إعـادة الـتـشـغـيـل الـفـوري
    os.execv(sys.executable, [sys.executable] + sys.argv)


async def get_message_link(client, event):
    """تـولـيـد رابـط الـرسـالـة"""
    chat = await event.get_chat()
    if event.is_private:
        return f"tg://openmessage?user_id={chat.id}&message_id={event.id}"
    return f"https://t.me/c/{str(chat.id).replace('-100', '')}/{event.id}"
