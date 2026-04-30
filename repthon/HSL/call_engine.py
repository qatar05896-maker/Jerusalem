# Venom Userbot - Call Engine
# Copyright (C) 2026 Abdullah (Venom). All Rights Reserved
# مبني على أحدث إصدار من PyTgCalls (v2.1.0+)
# يدعم التشغيل الصوتي والفيديو مع طابور ومنع التداخل

import asyncio
import logging
from asyncio import Lock
from contextlib import suppress
from pathlib import Path
from typing import Optional, Tuple

import yt_dlp
from pytgcalls import PyTgCalls, filters
from pytgcalls.types import (
    MediaStream,
    AudioQuality,
    VideoQuality,
    GroupCallConfig,
    Update,
    ChatUpdate,
    StreamEnded,
    GroupCallParticipant
)
from pytgcalls.exceptions import (
    NoActiveGroupCall,
    NotInCallError,
    PyTgCallsAlreadyRunning
)

logging.basicConfig(level=logging.ERROR)
def LOGGER(name): return logging.getLogger(name)

# ==========================================
# 0. إعدادات البث والتحميل
# ==========================================
TEMP_DIR = Path("temp")
TEMP_DIR.mkdir(parents=True, exist_ok=True)

# ملف الكوكيز لتخطي حماية يوتيوب (عدل المسار حسب جهازك)
COOKIES_PATH = Path("/root/repthon/repthon/plugins/cookies.txt")


class CallEngine:
    def __init__(self, client):
        self.client = client
        
        # ------------------------------------------------------------
        # خداع مكتبة PyTgCalls لتقبل الـ Userbot المعدل (مهم لـ Repthon)
        from pytgcalls.mtproto.bridged_client import BridgedClient
        BridgedClient.package_name = lambda c: 'telethon'
        # ------------------------------------------------------------
        
        self.app = PyTgCalls(client)
        self.queue: dict[int, list] = {}
        self.chat_locks: dict[int, Lock] = {}
        self._stream_end_cache = {}

    def get_lock(self, chat_id: int) -> Lock:
        if chat_id not in self.chat_locks:
            self.chat_locks[chat_id] = Lock()
        return self.chat_locks[chat_id]

    async def start(self):
        self._setup_decorators()
        try:
            await self.app.start()
        except PyTgCallsAlreadyRunning:
            pass
        LOGGER("CallEngine").info("تم تشغيل محرك المكالمات بنجاح.")

    def _setup_decorators(self):
        @self.app.on_update(filters.stream_end())
        async def on_stream_end(_, update: StreamEnded):
            chat_id = update.chat_id
            # منع التكرار خلال ثانيتين
            loop = asyncio.get_running_loop()
            now = loop.time()
            if chat_id in self._stream_end_cache:
                if now - self._stream_end_cache[chat_id] < 2.0:
                    return
            self._stream_end_cache[chat_id] = now
            # تنظيف الكاش القديم
            self._stream_end_cache = {cid: t for cid, t in self._stream_end_cache.items() if now - t < 5.0}
            await self._play_next(chat_id)

        @self.app.on_update(filters.chat_update(ChatUpdate.Status.LEFT_CALL))
        async def on_left_call(_, update: Update):
            await self.stop(update.chat_id)

        @self.app.on_update(filters.call_participant(GroupCallParticipant.Action.KICKED))
        async def on_kicked(_, update: Update):
            await self.stop(update.chat_id)

    # ==========================================
    # 1. جلب رابط البث المباشر من يوتيوب
    # ==========================================
    @staticmethod
    async def _get_stream_info(query: str, is_video: bool = False) -> Tuple[Optional[str], Optional[str]]:
        """ترجع (direct_url, title) من يوتيوب باستخدام yt-dlp"""
        # إذا كان الرابط موجوداً استخدمه، وإلا بحث
        if query.startswith("http"):
            search_query = query
        else:
            search_query = f"ytsearch1:{query}"

        # تنسيق الصوت: صوت فقط بدون فيديو أبداً
        fmt = "bestvideo+bestaudio/best" if is_video else "ba[ext=m4a]/bestaudio"

        opts = {
            "format": fmt,
            "quiet": True,
            "noplaylist": True,
            "no_warnings": True,
            "force_ipv4": True,
            "source_address": "0.0.0.0",
            "socket_timeout": 30,
            "js_runtimes": {"node": {}},
            "remote_components": ["ejs:github"],
            "extractor_args": {"youtube": {"player_client": ["web"]}},
            "cookiefile": str(COOKIES_PATH) if COOKIES_PATH.exists() else None,
        }

        def _search():
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(search_query, download=False)
                if info:
                    if 'entries' in info and info['entries']:
                        entry = info['entries'][0]
                    else:
                        entry = info
                    return entry.get("url"), entry.get("title")
                return None, None

        try:
            return await asyncio.to_thread(_search)
        except Exception as e:
            LOGGER("CallEngine").error(f"Stream Info Error: {e}")
            return None, None

    # ==========================================
    # 2. بناء MediaStream بالطريقة الجديدة
    # ==========================================
    def _build_stream(self, path: str, is_video: bool = False) -> MediaStream:
        ffmpeg_opts = "-probesize 10M -analyzeduration 10M -threads 0"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        }

        if is_video:
            return MediaStream(
                media_path=path,
                audio_parameters=AudioQuality.HIGH,
                video_parameters=VideoQuality.HD_720p,
                audio_flags=MediaStream.Flags.REQUIRED,
                video_flags=MediaStream.Flags.REQUIRED,
                ffmpeg_parameters=ffmpeg_opts,
                headers=headers,
            )
        else:
            return MediaStream(
                media_path=path,
                audio_parameters=AudioQuality.HIGH,
                video_parameters=None,
                audio_flags=MediaStream.Flags.REQUIRED,
                video_flags=MediaStream.Flags.IGNORE,   # <-- السر هنا!
                ffmpeg_parameters=ffmpeg_opts,
                headers=headers,
            )

    # ==========================================
    # 3. دوال التشغيل والطابور
    # ==========================================
    async def play_or_queue(self, chat_id: int, url: str, title: str, is_video: bool = False, force: bool = False):
        """تشغيل مباشر أو إضافة للطابور"""
        async with self.get_lock(chat_id):
            if chat_id not in self.queue:
                self.queue[chat_id] = []

            track = {"url": url, "title": title, "is_video": is_video}

            if force or len(self.queue[chat_id]) == 0:
                if force:
                    self.queue[chat_id].insert(0, track)
                else:
                    self.queue[chat_id].append(track)

                success = await self._execute_play(chat_id, track)
                if success:
                    return f"**• تم البدء بتشغيل ↶** `{title}`"
                else:
                    self.queue[chat_id].pop(0)
                    return "**⤶ حدث خطأ أثناء جلب رابط البث المباشر.**"
            else:
                self.queue[chat_id].append(track)
                position = len(self.queue[chat_id]) - 1
                return f"**• تمت الإضافة للطابور ↶** `{title}`\n**• المركز ↶** `{position}`"

    async def _execute_play(self, chat_id: int, track: dict) -> bool:
        url = track["url"]
        is_video = track["is_video"]

        direct_link, title = await self._get_stream_info(url, is_video)
        if not direct_link:
            LOGGER("CallEngine").error(f"Failed to get direct link for: {url}")
            return False

        stream = self._build_stream(direct_link, is_video)
        try:
            # play يدخل المكالمة تلقائياً ويبدأ البث
            await self.app.play(chat_id, stream, config=GroupCallConfig(auto_start=True))
            return True
        except Exception as e:
            LOGGER("CallEngine").error(f"Play Error: {e}")
            return False

    async def _play_next(self, chat_id: int):
        async with self.get_lock(chat_id):
            if chat_id in self.queue and len(self.queue[chat_id]) > 0:
                self.queue[chat_id].pop(0)  # إزالة المنتهي
                if len(self.queue[chat_id]) > 0:
                    next_track = self.queue[chat_id][0]
                    await self._execute_play(chat_id, next_track)
                else:
                    await self.stop(chat_id, clear_only=False)
            else:
                await self.stop(chat_id, clear_only=False)

    async def skip(self, chat_id: int):
        if chat_id not in self.queue or len(self.queue[chat_id]) <= 1:
            await self.stop(chat_id)
            return "**⤶ الطابور فارغ، تم إيقاف التشغيل والمغادرة.**"

        async with self.get_lock(chat_id):
            self.queue[chat_id].pop(0)
            next_track = self.queue[chat_id][0]
            success = await self._execute_play(chat_id, next_track)

        if success:
            return f"**• تم التخطي.**\n**• يعمل الآن ↶** `{next_track['title']}`"
        return "**⤶ حدث خطأ أثناء التخطي.**"

    async def stop(self, chat_id: int, clear_only: bool = False):
        if chat_id in self.queue:
            self.queue[chat_id].clear()
        if not clear_only:
            with suppress(Exception):
                await self.app.leave_call(chat_id)

    async def pause(self, chat_id: int):
        with suppress(Exception):
            await self.app.pause(chat_id)

    async def resume(self, chat_id: int):
        with suppress(Exception):
            await self.app.resume(chat_id)

    def get_playlist(self, chat_id: int) -> list:
        return self.queue.get(chat_id, [])
