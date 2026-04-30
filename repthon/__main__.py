import sys
import repthon
from repthon import BOTLOG_CHATID, PM_LOGGER_GROUP_ID
from .Config import Config
from .core.logger import logging
from .core.session import zq_lo
from .utils import mybot, autoname, autovars
from .utils import (
    add_bot_to_logger_group,
    load_plugins,
    setup_bot,
    saves,
    startupmessage,
    verifyLoggerGroup,
)

LOGS = logging.getLogger("𝙑🇪🇳🇴🇲")

print(repthon.__copyright__)
print(f"المرخصة بموجب شروط  {repthon.__license__}")

cmdhr = Config.COMMAND_HAND_LER

try:
    LOGS.info("⌭ جـاري تحميـل الملحقـات ⌭")
    zq_lo.loop.run_until_complete(autovars())
    LOGS.info("✓ تـم تحميـل الملحقـات .. بنجـاح ✓")
except Exception as e:
    LOGS.error(f"{e}")
    sys.exit()

if not Config.ALIVE_NAME:
    try: 
        LOGS.info("⌭ بـدء إضافة الاسـم التلقـائـي ⌭")
        zq_lo.loop.run_until_complete(autoname())
        LOGS.info("✓ تـم إضافة فار الاسـم .. بـنجـاح ✓")
    except Exception as e:
        LOGS.error(f"- {e}")

try: 
    LOGS.info("⌭ بـدء تنزيـل فـيـنــــوم ⌭")
    zq_lo.loop.run_until_complete(setup_bot())
    LOGS.info("⌭ بـدء تشغيل البـوت ⌭")
except Exception as e:
    LOGS.error(f"- {e}")

try:
    LOGS.info("⌭ جـار تفعيـل وضـع الانـلاين ⌭")
    zq_lo.loop.run_until_complete(mybot())
    LOGS.info("✓ تـم تفعيـل الانـلاين .. بـنجـاح ✓")
except Exception as e:
    LOGS.error(f"- {e}")

try:
    LOGS.info("⌭ جـار تفعـيـل وضـع حمــاية الحـسـاب من الاختـراق ⌭")
    zq_lo.loop.run_until_complete(saves())
    LOGS.info("✓ تـم تفعـيل .. وضـع حـمايـة الحـسـاب بنجــاح ✓")
except Exception as e:
    LOGS.error(f"- {e}")


async def startup_process():
    await verifyLoggerGroup()
    
    # تحـميل الـإضافات الـأساسية
    await load_plugins("plugins")
    
    # 🔴 تـطـويـر 2026: تـحـمـيـل الـإضـافـات مـن الـمـجـلـد الـمـخـصـص الـجـديـد
    LOGS.info("⌭ جـارِ تـحـمـيـل إضـافـات Pluginsme الـخـاصـة ⌭")
    await load_plugins("Pluginsme")
    
    # تـحـمـيـل الـمـسـاعـد
    await load_plugins("assistant")
    
    print("➖➖➖➖➖ 𝙑🇪🇳🇴🇲™ ➖➖➖➖➖")
    print("تـم التنصـيب .. بنجـاح ✓")
    print(
        f"⌔┊تـم تنصيـب فـيـنــــوم يـوزربـوت . . بنجـاح 🧸♥️ \n\n⌔┊تحيـاتي ..  بـودا\n⌔┊قنـاة السـورس ↶.\n🌐┊@SourceBoda"
    )
    print("➖➖➖➖➖ 𝙑🇪🇳🇴🇲™ ➖➖➖➖➖")
    
    await verifyLoggerGroup()
    await add_bot_to_logger_group(BOTLOG_CHATID)
    if PM_LOGGER_GROUP_ID != -100:
        await add_bot_to_logger_group(PM_LOGGER_GROUP_ID)
    await startupmessage()
    return

zq_lo.loop.run_until_complete(startup_process())
if len(sys.argv) not in (1, 3, 4):
    zq_lo.disconnect()
else:
    try:
        zq_lo.run_until_disconnected()
    except ConnectionError:
        pass
