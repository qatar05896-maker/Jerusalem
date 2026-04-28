# Venom Userbot
# Copyright (C) 2026 Abdullah (Venom). All Rights Reserved
# تم التحديث لمعايير 2026 - Non-Blocking I/O & Clean Architecture

import asyncio
import re
import time
from pathlib import Path

import aiohttp
import lottie
from validators.url import url

from .. import *
from ..Config import Config
from ..core.logger import logging
from ..core.managers import edit_delete, edit_or_reply
from ..core.session import zq_lo
from ..helpers import *
from ..helpers.utils import _reptools, _reputils, _format, install_pip, reply_id
from ..sql_helper.globals import gvarstatus
from repthon.helpers.functions.musictool import song_download

# =================== CONSTANT ===================
bot = zq_lo
LOGS = logging.getLogger(__name__)
USERID = zq_lo.uid if Config.OWNER_ID == 0 else Config.OWNER_ID
ALIVE_NAME = Config.ALIVE_NAME

# 1. إعدام هيروكو لتسريع الإقلاع على سيرفرات Fly.io
# تركنا المتغيرات بـ None لكي لا تنهار الإضافات القديمة التي تطلبها
Heroku = None
heroku_api = "https://api.heroku.com"
HEROKU_APP_NAME = None
HEROKU_API_KEY = None

# 2. استخدام Pathlib (معيار 2026) بدلاً من مكتبة os
TMP_DOWNLOAD_DIRECTORY = Path(Config.TMP_DOWNLOAD_DIRECTORY)
TMP_DOWNLOAD_DIRECTORY.mkdir(parents=True, exist_ok=True)
thumb_image_path = TMP_DOWNLOAD_DIRECTORY / "thumb_image.jpg"

# mention user
mention = f"[{Config.ALIVE_NAME}](tg://user?id={USERID})"
hmention = f"<a href='tg://user?id={USERID}'>{Config.ALIVE_NAME}</a>"

PM_START = []
PMMESSAGE_CACHE = {}
PMMENU = "pmpermit_menu" not in Config.NO_LOAD

# 3. حماية البوت من انهيار سيرفرات SpamWatch
spamwatch = None
if Config.SPAMWATCH_API:
    try:
        import spamwatch as spam_watch
        spamwatch = spam_watch.Client(Config.SPAMWATCH_API)
    except Exception as e:
        LOGS.warning(f"SpamWatch Initialization Failed: {e}")

# ================================================

# 4. تحميل الصورة في الخلفية (Async) لمنع تجميد السيرفر عند الإقلاع
async def download_thumb_image():
    if Config.THUMB_IMAGE and url(Config.THUMB_IMAGE):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(Config.THUMB_IMAGE) as resp:
                    if resp.status == 200:
                        thumb_image_path.write_bytes(await resp.read())
        except Exception as e:
            LOGS.warning(f"Failed to download thumb image: {e}")

# جدولة التحميل ليعمل في الخلفية فوراً دون تعطيل البوت
asyncio.get_event_loop().create_task(download_thumb_image())


def set_key(dictionary: dict, key: str, value):
    """دالة إضافة المفاتيح المحدثة (Type Hinted)"""
    if key not in dictionary:
        dictionary[key] = value
    elif isinstance(dictionary[key], list):
        if value not in dictionary[key]:
            dictionary[key].append(value)
    else:
        dictionary[key] = [dictionary[key], value]


async def make_gif(event, reply, quality=256, fps=1):
    """صناعة الصور المتحركة بشكل متوافق ومحمي"""
    result_p = Path("temp") / "animation.gif"
    result_p.parent.mkdir(exist_ok=True)
    
    try:
        animation = lottie.parsers.tgs.parse_tgs(reply)
        with result_p.open("wb") as result:
            await _reputils.run_sync(
                lottie.exporters.gif.export_gif, animation, result, quality, fps
            )
        return str(result_p)
    except Exception as e:
        LOGS.error(f"Lottie Export Error: {e}")
        return None
