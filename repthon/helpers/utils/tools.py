import os
from typing import Optional

# التعديل الأول: استدعاء آمن لمكتبة الفيديوهات لتعمل على كل الإصدارات
try:
    from moviepy import VideoFileClip
except ImportError:
    from moviepy.editor import VideoFileClip

from PIL import Image

from ...core.logger import logging
from ...core.managers import edit_or_reply
from ..tools import media_type
from .utils import runcmd

LOGS = logging.getLogger(__name__)

# التعديل الثاني: دالة مساعدة لتخطي خطأ save_frame المحذوف في الإصدارات الجديدة
def safe_save_frame(clip, filename, t):
    if hasattr(clip, "save_frame"):
        clip.save_frame(filename, t)
    else:
        # طريقة الإصدار 2.0+ 
        frame = clip.get_frame(t)
        Image.fromarray(frame).save(filename)


async def media_to_pic(event, reply, noedits=False):  # sourcery no-metrics
    mediatype = media_type(reply)
    if mediatype not in [
        "Photo",
        "Round Video",
        "Gif",
        "Sticker",
        "Video",
        "Voice",
        "Audio",
        "Document",
    ]:
        return event, None
    if not noedits:
        zedevent = await edit_or_reply(
            event, "`Transfiguration Time! Converting to ....`"
        )

    else:
        zedevent = event
    zedmedia = None
    zedfile = os.path.join("./temp/", "meme.png")
    if os.path.exists(zedfile):
        os.remove(zedfile)
    if mediatype == "Photo":
        zedmedia = await reply.download_media(file="./temp")
        im = Image.open(zedmedia)
        im.save(zedfile)
    elif mediatype in ["Audio", "Voice"]:
        await event.client.download_media(reply, zedfile, thumb=-1)
    elif mediatype == "Sticker":
        zedmedia = await reply.download_media(file="./temp")
        if zedmedia.endswith(".tgs"):
            zedcmd = f"lottie_convert.py --frame 0 -if lottie -of png '{zedmedia}' '{zedfile}'"
            stdout, stderr = (await runcmd(zedcmd))[:2]
            if stderr:
                LOGS.info(stdout + stderr)
        elif zedmedia.endswith(".webm"):
            clip = VideoFileClip(zedmedia)
            try:
                # استخدام الدالة الآمنة
                safe_save_frame(clip, zedfile, 0.1)
            except Exception:
                safe_save_frame(clip, zedfile, 0)
        elif zedmedia.endswith(".webp"):
            im = Image.open(zedmedia)
            im.save(zedfile)
    elif mediatype in ["Round Video", "Video", "Gif"]:
        await event.client.download_media(reply, zedfile, thumb=-1)
        if not os.path.exists(zedfile):
            zedmedia = await reply.download_media(file="./temp")
            clip = VideoFileClip(zedmedia)
            try:
                # استخدام الدالة الآمنة
                safe_save_frame(clip, zedfile, 0.1)
            except Exception:
                safe_save_frame(clip, zedfile, 0)
    elif mediatype == "Document":
        mimetype = reply.document.mime_type
        mtype = mimetype.split("/")
        if mtype[0].lower() == "image":
            zedmedia = await reply.download_media(file="./temp")
            im = Image.open(zedmedia)
            im.save(zedfile)
    if zedmedia and os.path.lexists(zedmedia):
        os.remove(zedmedia)
    if os.path.lexists(zedfile):
        return zedevent, zedfile, mediatype
    return zedevent, None


async def take_screen_shot(
    video_file: str, duration: int, path: str = ""
) -> Optional[str]:
    thumb_image_path = path or os.path.join(
        "./temp/", f"{os.path.basename(video_file)}.jpg"
    )
    command = f"ffmpeg -ss {duration} -i '{video_file}' -vframes 1 '{thumb_image_path}'"
    err = (await runcmd(command))[1]
    if err:
        LOGS.error(err)
    return thumb_image_path if os.path.exists(thumb_image_path) else None
