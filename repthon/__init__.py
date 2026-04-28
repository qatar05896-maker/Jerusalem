# Venom Userbot
# Copyright (C) 2026 Abdullah (Venom). All Rights Reserved
# الـمـالـك: @S_G0C7
# مـلـف الـتـهـيـئـة الـرئـيـسـي (Init) - مـخـصـص لـبـيـئـة Fly.io بـدون هـيـروكـو

import signal
import sys
import time

from .Config import Config
from .core.logger import logging
from .core.session import zq_lo
from .helpers.utils.utils import runasync
from .sql_helper.globals import addgvar, delgvar, gvarstatus

__version__ = "2026.1.0"
__license__ = "GNU Affero General Public License v3.0"
__author__ = "Venom <https://t.me/S_G0C7>"
__copyright__ = f"Venom Copyright (C) 2026  {__author__}"

zq_lo.version = __version__
zq_lo.tgbot.version = __version__
LOGS = logging.getLogger("Venom")
bot = zq_lo

StartTime = time.time()
repversion = "2026"


def close_connection(*_):
    print("تـم إغـلاق اتـصـال الـسـورس بـأمـان.")
    runasync(zq_lo.disconnect())
    sys.exit(143)


signal.signal(signal.SIGTERM, close_connection)


if Config.UPSTREAM_REPO == "Repthon":
    UPSTREAM_REPO_URL = "https://github.com/RepthonArabic/Repthon"
else:
    UPSTREAM_REPO_URL = Config.UPSTREAM_REPO

# تـهـيـئـة وإعـداد آيـدي جـروب الـلـوج (سـجـل الـبـوت)
if Config.PRIVATE_GROUP_BOT_API_ID == 0:
    if gvarstatus("PRIVATE_GROUP_BOT_API_ID") is None:
        Config.BOTLOG = False
        Config.BOTLOG_CHATID = "me"
    else:
        Config.BOTLOG_CHATID = int(gvarstatus("PRIVATE_GROUP_BOT_API_ID"))
        Config.PRIVATE_GROUP_BOT_API_ID = int(gvarstatus("PRIVATE_GROUP_BOT_API_ID"))
        Config.BOTLOG = True
else:
    if str(Config.PRIVATE_GROUP_BOT_API_ID)[0] != "-":
        Config.BOTLOG_CHATID = int("-" + str(Config.PRIVATE_GROUP_BOT_API_ID))
    else:
        Config.BOTLOG_CHATID = Config.PRIVATE_GROUP_BOT_API_ID
    Config.BOTLOG = True

# تـهـيـئـة أيـدي جـروب سـجـل الـخـاص
if Config.PM_LOGGER_GROUP_ID == 0:
    if gvarstatus("PM_LOGGER_GROUP_ID") is None:
        Config.PM_LOGGER_GROUP_ID = -100
    else:
        Config.PM_LOGGER_GROUP_ID = int(gvarstatus("PM_LOGGER_GROUP_ID"))
elif str(Config.PM_LOGGER_GROUP_ID)[0] != "-":
    Config.PM_LOGGER_GROUP_ID = int("-" + str(Config.PM_LOGGER_GROUP_ID))


# 🔴 تـعـديـل حـاسـم: تـمـت إزالـة مـكـتـبـة heroku3 كـلـيـاً لـتـوافـق الـسـيـرفـر مـع Fly.io
# نـتـرك الـمـتـغـيـر بـقـيـمـة None لـكـي لـا تـنـهـار الـإضـافـات الـأخـرى الـتـي تـسـتـدعـيـه
HEROKU_APP = None


# مـتـغـيـرات عـامـة لـعـمـل الـسـورس (Global Configiables)
COUNT_MSG = 0
USERS = {}
COUNT_PM = {}
LASTMSG = {}
CMD_HELP = {}
ISAFK = False
AFKREASON = None
CMD_LIST = {}
SUDO_LIST = {}

# لـلـاسـتـخـدام الـلـاحـق فـي الـمـلـفـات
INT_PLUG = ""
LOAD_PLUG = {}

# ثـوابـت (Variables)
BOTLOG = Config.BOTLOG
BOTLOG_CHATID = Config.BOTLOG_CHATID
PM_LOGGER_GROUP_ID = Config.PM_LOGGER_GROUP_ID
