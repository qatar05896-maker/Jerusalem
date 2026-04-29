# Venom Userbot
# Copyright (C) 2026 Abdullah (Venom). All Rights Reserved
# الـمـالـك: @S_G0C7
# تـم الـتـرقـيـة لـمـعـايـيـر 2026 - Clean Architecture & Async Opt

import asyncio
import datetime
import inspect
import re
import os
import sys
import traceback
from pathlib import Path
from typing import Dict, List, Union, Callable, Any

from telethon import TelegramClient, events
from telethon.errors import (
    AlreadyInConversationError,
    BotInlineDisabledError,
    BotResponseTimeoutError,
    ChatSendInlineForbiddenError,
    ChatSendMediaForbiddenError,
    ChatSendStickersForbiddenError,
    FloodWaitError,
    MessageIdInvalidError,
    MessageNotModifiedError,
)

from ..Config import Config
from ..helpers.utils.events import checking
from ..helpers.utils.format import paste_message
from ..helpers.utils.utils import runcmd
from ..sql_helper.globals import gvarstatus
from . import BOT_INFO, CMD_INFO, GRP_INFO, LOADED_CMDS, PLG_INFO
from .cmdinfo import _format_about
from .data import _sudousers_list, blacklist_chats_list, sudo_enabled_cmds
from .events import *
from .fasttelethon import download_file, upload_file
from .logger import logging
from .managers import edit_delete
from .pluginManager import get_message_link, restart_script

LOGS = logging.getLogger("𝙑𝙚𝙣𝙤𝙢")

class REGEX:
    def __init__(self):
        self.regex1 = ""
        self.regex2 = ""

REGEX_ = REGEX()
sudo_enabledcmds = sudo_enabled_cmds()

class RepUserBotClient(TelegramClient):
    
    def rep_cmd(
        self,
        pattern: Union[str, tuple] = None,
        info: Union[str, Dict[str, Any], tuple] = None,
        groups_only: bool = False,
        private_only: bool = False,
        allow_sudo: bool = True,
        edited: bool = True,
        forwards: bool = False,
        disable_errors: bool = False,
        command: Union[str, tuple] = None,
        **kwargs,
    ) -> Callable:
        
        kwargs["func"] = kwargs.get("func", lambda e: e.via_bot_id is None)
        kwargs.setdefault("forwards", forwards)
        
        if gvarstatus("blacklist_chats") is not None:
            kwargs["blacklist_chats"] = True
            kwargs["chats"] = blacklist_chats_list()
            
        stack = inspect.stack()
        previous_stack_frame = stack[1]
        file_test = Path(previous_stack_frame.filename).stem
        
        # تـهـيـئـة الـمـعـلـومـات والـتـحـقـق مـن الـ NoneType (أهـم تـعـديـل)
        if command is not None and isinstance(command, (list, tuple)):
            cmd_name = command[0]
            cmd_group = command[1]
            
            if cmd_group not in BOT_INFO:
                BOT_INFO.append(cmd_group)
                
            if cmd_group not in GRP_INFO:
                GRP_INFO[cmd_group] = []
            if file_test not in GRP_INFO[cmd_group]:
                GRP_INFO[cmd_group].append(file_test)
                
            if file_test not in PLG_INFO:
                PLG_INFO[file_test] = []
            if cmd_name not in PLG_INFO[file_test]:
                PLG_INFO[file_test].append(cmd_name)
                
            if cmd_name not in CMD_INFO:
                CMD_INFO[cmd_name] = [_format_about(info)]
                
        if pattern is not None:
            if pattern.startswith(r"\#") or (not pattern.startswith(r"\#") and pattern.startswith(r"^")):
                REGEX_.regex1 = REGEX_.regex2 = re.compile(pattern)
            else:
                reg1 = "\\" + Config.COMMAND_HAND_LER
                reg2 = "\\" + Config.SUDO_COMMAND_HAND_LER
                REGEX_.regex1 = re.compile(reg1 + pattern)
                REGEX_.regex2 = re.compile(reg2 + pattern)

        def decorator(func):
            async def wrapper(check):
                if groups_only and not check.is_group:
                    return await edit_delete(check, "**⪼ عـذراً، هـذا الـأمـر يـسـتـخـدم فـي الـمـجـمـوعـات فـقـط 𓆰.**", 10)
                if private_only and not check.is_private:
                    return await edit_delete(check, "**⪼ هـذا الـأمـر يـسـتـخـدم فـقط فـي الـدردشـات الـخـاصـة 𓆰.**", 10)
                try:
                    await func(check)
                except events.StopPropagation:
                    raise
                except KeyboardInterrupt:
                    pass
                except (MessageNotModifiedError, MessageIdInvalidError):
                    pass
                except BotInlineDisabledError:
                    await edit_delete(check, "**⪼ يـجـب عـلـيـك تـفـعـيـل وضـع الـإنـلايـن أولاً 𓆰.**", 10)
                except FloodWaitError as e:
                    LOGS.error(f"FloodWait: {e.seconds}s")
                    await asyncio.sleep(e.seconds + 5)
                except Exception as e:
                    LOGS.exception(e)
                    if not disable_errors and Config.PRIVATE_GROUP_BOT_API_ID != 0:
                        date = datetime.datetime.now().strftime("%Y/%m/%d - %H:%M:%S")
                        ftext = f"**✘ تـقـريـر خـطـأ فـي سـورس ڤـيـنـوم 𝙑𝙚𝙣𝙤𝙢 ✘**\n\n"
                        ftext += f"- **الـتـاريـخ:** `{date}`\n"
                        ftext += f"- **الـنـص:** `{str(check.text)}`\n"
                        ftext += f"- **الـتـفـاصـيـل:**\n`{str(traceback.format_exc())}`"
                        pastelink = await paste_message(ftext, pastetype="s", markdown=False)
                        await check.client.send_message(Config.PRIVATE_GROUP_BOT_API_ID, f"**✘ خـطأ جـديـد:** [الـتـقـريـر هـنـا]({pastelink})", link_preview=False)

            from .session import zq_lo

            # حـمـايـة مـطـورة ضـد كـراش الـ NoneType
            if func.__doc__ and command and isinstance(command, (list, tuple)):
                if command[0] in CMD_INFO:
                    CMD_INFO[command[0]].append((func.__doc__).strip())
            
            if pattern is not None:
                if command and isinstance(command, (list, tuple)):
                    cmd_key = command[0]
                    if cmd_key in LOADED_CMDS and wrapper in LOADED_CMDS[cmd_key]:
                        return None
                    LOADED_CMDS.setdefault(cmd_key, []).append(wrapper)
                
                if edited:
                    zq_lo.add_event_handler(wrapper, MessageEdited(pattern=REGEX_.regex1, outgoing=True, **kwargs))
                zq_lo.add_event_handler(wrapper, NewMessage(pattern=REGEX_.regex1, outgoing=True, **kwargs))
                
                if allow_sudo and gvarstatus("sudoenable") is not None:
                    if command is None or command[0] in sudo_enabledcmds:
                        if edited:
                            zq_lo.add_event_handler(wrapper, MessageEdited(pattern=REGEX_.regex2, from_users=_sudousers_list(), **kwargs))
                        zq_lo.add_event_handler(wrapper, NewMessage(pattern=REGEX_.regex2, from_users=_sudousers_list(), **kwargs))
            else:
                LOADED_CMDS.setdefault(file_test, []).append(func)
                if edited:
                    zq_lo.add_event_handler(func, events.MessageEdited(**kwargs))
                zq_lo.add_event_handler(func, events.NewMessage(**kwargs))
            return wrapper
        return decorator

    def bot_cmd(self, disable_errors: bool = False, edited: bool = False, forwards: bool = False, **kwargs) -> Callable:
        kwargs["func"] = kwargs.get("func", lambda e: e.via_bot_id is None)
        kwargs.setdefault("forwards", forwards)
        def decorator(func):
            async def wrapper(check):
                try:
                    await func(check)
                except Exception as e:
                    LOGS.exception(e)
            from .session import zq_lo
            if edited:
                zq_lo.tgbot.add_event_handler(func, events.MessageEdited(**kwargs))
            else:
                zq_lo.tgbot.add_event_handler(func, events.NewMessage(**kwargs))
            return wrapper
        return decorator

# تـعـريـف الـوظـائـف الـسـريـعـة
RepUserBotClient.fast_download_file = download_file
RepUserBotClient.fast_upload_file = upload_file
RepUserBotClient.reload = restart_script
RepUserBotClient.get_msg_link = get_message_link
RepUserBotClient.check_testcases = checking
