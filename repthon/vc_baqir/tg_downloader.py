import pathlib
import time
from datetime import datetime

from telethon.tl import types
from telethon.utils import get_extension
from ..Config import Config
from ..core.managers import edit_or_reply
from ..helpers import progress

NAME = "untitled"

# استخدام pathlib بشكل كامل ومباشر لإدارة المسارات (الاستغناء عن مكتبة os)
BASE_DIR = pathlib.Path.cwd()
DOWNLOADS_DIR = BASE_DIR / Config.TMP_DOWNLOAD_DIRECTORY

async def tg_dl(event):
    """دالة حديثة لتحميل الملفات المرفقة في رسائل تيليجرام"""
    mone = await edit_or_reply(event, "**- جـارِ التحميـل 📥...**")
    
    reply = await event.get_reply_message()
    
    # التحقق من وجود رسالة مقتبسة تحتوي على ميديا بطريقة نظيفة
    if not reply or not (reply.document or reply.photo):
        await mone.edit("**- الرجاء الرد على فيديو أو ملف صوتي لتشغيله...**")
        return False

    # إنشاء مجلد التحميلات إذا لم يكن موجوداً
    DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)
    
    start_time = datetime.now()
    name = NAME
    
    # استخراج اسم الملف من خصائص المستند (إن وجد)
    if reply.document:
        for attr in reply.document.attributes:
            if isinstance(attr, types.DocumentAttributeFilename):
                name = attr.file_name
                break
                
    # استخراج الامتداد بشكل آمن
    ext = get_extension(reply.document) or get_extension(reply.photo) or ""
    
    # توليد اسم افتراضي في حال عدم وجود اسم للملف
    if name == NAME:
        name += f"_{reply.id}{ext}"
        
    file_path = DOWNLOADS_DIR / name

    # إضافة الامتداد إذا كان مفقوداً
    if not file_path.suffix and ext:
        file_path = file_path.with_suffix(ext)

    # معالجة تعارض الأسماء: إذا كان الملف موجوداً مسبقاً، نعيد تسمية القديم
    if file_path.exists() and file_path.is_file():
        new_name = f"{file_path.stem}_OLD{file_path.suffix}"
        file_path.rename(file_path.with_name(new_name))

    c_time = time.time()

    # دالة داخلية للتعامل مع شريط التقدم (أفضل من استخدام lambda و create_task)
    async def progress_cb(current, total):
        await progress(current, total, mone, c_time, "**- جـارِ التحميـل 📥...**")

    try:
        # استخدام fast_download_file دائماً مع الملفات لتسريع التحميل
        if reply.document:
            # فتح الملف باستخدام pathlib
            with file_path.open("wb") as fd:
                await event.client.fast_download_file(
                    location=reply.document,
                    out=fd,
                    progress_callback=progress_cb
                )
        else:
            # الصور والملفات الخفيفة تُحمل عبر الطريقة التقليدية
            await reply.download_media(
                file=str(file_path),
                progress_callback=progress_cb
            )
            
    except Exception as e:
        await mone.edit(f"**- حـدث خطـأ أثنـاء التحميـل:**\n`{e}`")
        return False

    end_time = datetime.now()
    ms = (end_time - start_time).seconds
    
    # حساب المسار النسبي (Relative Path) بطريقة احترافية
    try:
        rel_path = file_path.relative_to(BASE_DIR)
    except ValueError:
        rel_path = file_path

    await mone.edit(
        f"**❈╎تم التحميـل خلال {ms} ثانيـه.**\n**❈╎مسـار التحميـل :- ** `{rel_path}`\n"
    )
    
    return str(rel_path)
