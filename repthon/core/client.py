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
import marshal
from pathlib import Path
from typing import Dict, List, Union, Callable

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
        self.regex = ""
        self.regex1 = ""
        self.regex2 = ""

REGEX_ = REGEX()
sudo_enabledcmds = sudo_enabled_cmds()


class RepUserBotClient(TelegramClient):
    
    def rep_cmd(
        self: TelegramClient,
        pattern: Union[str, tuple] = None,
        info: Union[str, Dict[str, Union[str, List[str], Dict[str, str]]], tuple] = None,
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
        file_test = Path(previous_stack_frame.filename).stem.replace(".py", "")
        
        if command is not None:
            command = list(command)
            if not command[1] in BOT_INFO:
                BOT_INFO.append(command[1])
            try:
                if file_test not in GRP_INFO[command[1]]:
                    GRP_INFO[command[1]].append(file_test)
            except KeyError:
                GRP_INFO.update({command[1]: [file_test]})
            try:
                if command[0] not in PLG_INFO[file_test]:
                    PLG_INFO[file_test].append(command[0])
            except KeyError:
                PLG_INFO.update({file_test: [command[0]]})
            if not command[0] in CMD_INFO:
                CMD_INFO[command[0]] = [_format_about(info)]
                
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
                    return await edit_delete(check, "**⪼ هـذا الـأمـر يـسـتـخـدم فـقـط فـي الـدردشـات الـخـاصـة 𓆰.**", 10)
                try:
                    await func(check)
                except events.StopPropagation:
                    raise
                except KeyboardInterrupt:
                    pass
                except MessageNotModifiedError:
                    LOGS.error("الـرسـالـة مـمـاثـلـة لـلـرسـالـة الـسـابـقـة.")
                except MessageIdInvalidError:
                    LOGS.error("الـرسـالـة تـم حـذفـهـا أو لـم يـتـم الـعـثـور عـلـيـهـا.")
                except BotInlineDisabledError:
                    await edit_delete(check, "**⪼ يـجـب عـلـيـك تـفـعـيـل وضـع الـإنـلايـن أولاً 𓆰.**", 10)
                except ChatSendStickersForbiddenError:
                    await edit_delete(check, "**⪼ هـذه الـمـجـمـوعـة لا تـسـمـح بـإرسـال الـمـلـصـقـات هـنـا 𓆰.**", 10)
                except BotResponseTimeoutError:
                    await edit_delete(check, "**⪼ اسـتـخـدم الـمـيـزة بـعـد وقـت قـلـيـل، لا يـمـكـن الـاسـتـجـابـة الـآن 𓆰.**", 10)
                except ChatSendMediaForbiddenError:
                    await edit_delete(check, "**⪼ هـذه الـمـجـمـوعـة تـمـنـع إرسـال الـمـيـديـا هـنـا 𓆰.**", 10)
                except AlreadyInConversationError:
                    await edit_delete(check, "**⪼ الـمـحـادثـة تـجـري بـالـفـعـل، حـاول مـرة أخـرى بـعـد قـلـيـل 𓆰.**", 10)
                except ChatSendInlineForbiddenError:
                    await edit_delete(check, "**⪼ عـذراً .. الـإنـلايـن فـي هـذه الـمـجـمـوعـة مـغـلـق 𓆰.**", 10)
                except FloodWaitError as e:
                    LOGS.error(f"إيـقـاف مـؤقـت بـسـبـب الـتـكـرار. انـتـظـر {e.seconds} ثـانـيـة.")
                    await check.delete()
                    await asyncio.sleep(e.seconds + 5)
                except Exception as e:
                    LOGS.exception(e)
                    if not disable_errors and Config.PRIVATE_GROUP_BOT_API_ID != 0:
                        # Report Error to Logger Group
                        date = datetime.datetime.now().strftime("%Y/%m/%d - %H:%M:%S")
                        ftext = f"**✘ تـقـريـر خـطـأ فـي سـورس ڤـيـنـوم 𝙑𝙚𝙣𝙤𝙢 ✘**\n\n"
                        ftext += f"- **الـتـاريـخ:** `{date}`\n"
                        ftext += f"- **آيـدي الـدردشـة:** `{check.chat_id}`\n"
                        ftext += f"- **الـمـرسـل:** `{check.sender_id}`\n\n"
                        ftext += f"**- الـنـص:**\n`{str(check.text)}`\n\n"
                        ftext += f"**- الـتـفـاصـيـل:**\n`{str(traceback.format_exc())}`\n"
                        
                        try:
                            command_log = 'git log --pretty=format:"%an: %s" -5'
                            output = (await runcmd(command_log))[:2]
                            ftext += f"\n\n**- آخـر الـتـحـديـثـات:**\n`{output[0] + output[1]}`"
                        except Exception:
                            pass

                        pastelink = await paste_message(ftext, pastetype="s", markdown=False)
                        link = "[𝙑𝙚𝙣𝙤𝙢 | S_G0C7](https://t.me/S_G0C7)"
                        
                        text = f"**✘ تـم اكـتـشـاف خـطـأ فـي الـسـورس ✘**\n\n"
                        text += f"- يـرجـى إعـادة تـوجـيـه هـذه الـرسـالـة إلـى الـمـطـور: {link}\n"
                        text += f"**- سـجـل الـأخـطـاء:** [اضـغـط هـنـا لـعـرض الـتـقـريـر]({pastelink})"
                        
                        await check.client.send_message(Config.PRIVATE_GROUP_BOT_API_ID, text, link_preview=False)

            from .session import zq_lo

            if func.__doc__ is not None:
                CMD_INFO[command[0]].append((func.__doc__).strip())
            
            if pattern is not None:
                if command is not None:
                    if command[0] in LOADED_CMDS and wrapper in LOADED_CMDS[command[0]]:
                        return None
                    try:
                        LOADED_CMDS[command[0]].append(wrapper)
                    except KeyError:
                        LOADED_CMDS.update({command[0]: [wrapper]})
                if edited:
                    zq_lo.add_event_handler(wrapper, MessageEdited(pattern=REGEX_.regex1, outgoing=True, **kwargs))
                zq_lo.add_event_handler(wrapper, NewMessage(pattern=REGEX_.regex1, outgoing=True, **kwargs))
                
                if allow_sudo and gvarstatus("sudoenable") is not None:
                    if command is None or command[0] in sudo_enabledcmds:
                        if edited:
                            zq_lo.add_event_handler(wrapper, MessageEdited(pattern=REGEX_.regex2, from_users=_sudousers_list(), **kwargs))
                        zq_lo.add_event_handler(wrapper, NewMessage(pattern=REGEX_.regex2, from_users=_sudousers_list(), **kwargs))
            else:
                if file_test in LOADED_CMDS and func in LOADED_CMDS[file_test]:
                    return None
                try:
                    LOADED_CMDS[file_test].append(func)
                except KeyError:
                    LOADED_CMDS.update({file_test: [func]})
                if edited:
                    zq_lo.add_event_handler(func, events.MessageEdited(**kwargs))
                zq_lo.add_event_handler(func, events.NewMessage(**kwargs))
            return wrapper
        return decorator

    def bot_cmd(
        self: TelegramClient,
        disable_errors: bool = False,
        edited: bool = False,
        forwards: bool = False,
        **kwargs,
    ) -> Callable:
        kwargs["func"] = kwargs.get("func", lambda e: e.via_bot_id is None)
        kwargs.setdefault("forwards", forwards)

        def decorator(func):
            async def wrapper(check):
                try:
                    await func(check)
                except events.StopPropagation:
                    raise
                except KeyboardInterrupt:
                    pass
                except MessageNotModifiedError:
                    LOGS.error("الـرسـالـة مـمـاثـلـة.")
                except MessageIdInvalidError:
                    LOGS.error("الـرسـالـة غـيـر مـوجـودة.")
                except Exception as e:
                    LOGS.exception(e)
                    if not disable_errors and Config.PRIVATE_GROUP_BOT_API_ID != 0:
                        pastelink = await paste_message(str(traceback.format_exc()), pastetype="s", markdown=False)
                        link = "[𝙑𝙚𝙣𝙤𝙢 | S_G0C7](https://t.me/S_G0C7)"
                        text = f"**✘ تـم اكـتـشـاف خـطـأ فـي الـبـوت الـمـسـاعـد ✘**\n\n"
                        text += f"- يـرجـى إعـادة تـوجـيـه هـذه الـرسـالـة إلـى الـمـطـور: {link}\n"
                        text += f"**- سـجـل الـأخـطـاء:** [الـتـقـريـر]({pastelink})"
                        await check.client.send_message(Config.PRIVATE_GROUP_BOT_API_ID, text, link_preview=False)

            from .session import zq_lo

            if edited:
                zq_lo.tgbot.add_event_handler(func, events.MessageEdited(**kwargs))
            else:
                zq_lo.tgbot.add_event_handler(func, events.NewMessage(**kwargs))
            return wrapper
        return decorator

    async def get_traceback(self, exc: Exception) -> str:
        return "".join(traceback.format_exception(etype=type(exc), value=exc, tb=exc.__traceback__))

    def _kill_running_processes(self) -> None:
        """Kill all the running asyncio subprocesses"""
        for _, process in self.running_processes.items():
            try:
                process.kill()
                LOGS.debug(f"Killed {process.pid} which was still running.")
            except Exception as e:
                LOGS.debug(e)
        self.running_processes.clear()

RepUserBotClient.fast_download_file = download_file
RepUserBotClient.fast_upload_file = upload_file
RepUserBotClient.reload = restart_script
RepUserBotClient.get_msg_link = get_message_link
RepUserBotClient.check_testcases = checking

try:
    send_message_check = TelegramClient.send_message
except AttributeError:
    RepUserBotClient.send_message = send_message
    RepUserBotClient.send_file = send_file
    RepUserBotClient.edit_message = edit_message
