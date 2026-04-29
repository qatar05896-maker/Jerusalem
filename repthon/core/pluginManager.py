# Venom Userbot
# Copyright (C) 2026 Abdullah (Venom). All Rights Reserved
# الـمـالـك: @S_G0C7
# مـديـر الـإضـافـات ومـراقـب الـأخـطـاء الـذـكـي (Smart Plugin Manager)

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

package_pattern = re.compile(r"([\w-]+)(?:=|<|>|!)")
LOGS = logging.getLogger("VenomManager")

# -----------------------------------------------------------------
# تـطـويـر 2026: نـظـام تـحـمـيـل الـإضـافـات الـذـكـي (Smart Plugin Loader)
# يـقـوم بـمـراقـبـة كـل مـلـف وتـسـجـيـل الـأخـطـاء بـدقـة فـي الـلـوج بـدون إيـقـاف الـبـوت
# -----------------------------------------------------------------

def load_module(shortname):
    """تـحـمـيـل إضـافـة مـعـيـنـة مـع مـراقـبـة الـأخـطـاء"""
    if shortname.startswith("__"):
        pass
    elif shortname.endswith("_"):
        importlib.import_module(f"repthon.plugins.{shortname}")
    else:
        path = Path(f"repthon/plugins/{shortname}.py")
        name = f"repthon.plugins.{shortname}"
        spec = importlib.util.spec_from_file_location(name, path)
        
        if spec is None:
            LOGS.error(f"[{shortname}] ❌ لـم يـتـم الـعـثـور عـلـى مـسـار الـمـلـف.")
            return False
            
        mod = importlib.util.module_from_spec(spec)
        mod.plugin_name = shortname
        
        try:
            # مـحـاولـة تـشـغـيـل وحـقـن الـمـلـف
            spec.loader.exec_module(mod)
            sys.modules[name] = mod
            LOGS.info(f"[{shortname}] ✅ تـم الـتـحـمـيـل بـنـجـاح.")
            return True
        except Exception as e:
            # هـنـا يـتـم صـيـد الـخـطـأ وعـزلـه وطـبـاعـتـه بـالـتـفـصـيـل
            error_msg = f"\n⚠️ [تـحـذيـر] فـشـل تـحـمـيـل مـلـف: {shortname}.py\n"
            error_msg += f"➜ الـسـبـب: {e}\n"
            error_msg += f"➜ الـتـفـاصـيـل الـدـقـيـقـة:\n{traceback.format_exc()}"
            error_msg += "--------------------------------------------------"
            LOGS.error(error_msg)
            return False


def remove_plugin(shortname):
    """إزالـة إضـافـة قـيـد الـتـشـغـيـل"""
    try:
        from repthon import bot
        name = f"repthon.plugins.{shortname}"
        for i in reversed(range(len(bot._event_builders))):
            ev, cb = bot._event_builders[i]
            if cb.__module__ == name:
                del bot._event_builders[i]
        if name in sys.modules:
            del sys.modules[name]
        return True
    except Exception as e:
        LOGS.error(f"[{shortname}] ❌ حـدث خـطـأ أثـنـاء إزالـة الـمـلـف: {e}")
        return False

# -----------------------------------------------------------------
# مـديـر الـحـزم وإعـادة الـتـشـغـيـل
# -----------------------------------------------------------------

async def get_pip_packages(requirements):
    if requirements:
        packages = requirements
    else:
        cmd = await asyncio.create_subprocess_exec(
            sys.executable.replace(" ", "\\ "),
            "-m", "pip", "freeze",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, _ = await cmd.communicate()
        packages = stdout.decode("utf-8")
    tmp = package_pattern.findall(packages)
    return [package.lower() for package in tmp]


async def install_pip_packages(packages):
    args = ["-m", "pip", "install", "--upgrade", "--user"]
    cmd = await asyncio.create_subprocess_exec(
        sys.executable.replace(" ", "\\ "),
        *args, *packages,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    await cmd.communicate()
    return cmd.returncode == 0


def run_async(func: callable):
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(func)


async def restart_script(client: TelegramClient, sandy):
    """إعـادة تـشـغـيـل الـبـوت (مـتـوافـق مـع Fly.io)"""
    try:
        ulist = get_collectionlist_items()
        for i in ulist:
            if i == "restart_update":
                del_keyword_collectionlist("restart_update")
    except Exception as e:
        LOGS.error(e)
    try:
        add_to_collectionlist("restart_update", [sandy.chat_id, sandy.id])
    except Exception as e:
        LOGS.error(e)
        
    LOGS.info("جـارِ إعـادة تـشـغـيـل الـسـيـرفـر بـأمـان (Fly.io)...")
    sys.exit(143)


async def get_message_link(client, event):
    chat = await event.get_chat()
    if event.is_private:
        return f"tg://openmessage?user_id={chat.id}&message_id={event.id}"
    return f"https://t.me/c/{chat.id}/{event.id}"
