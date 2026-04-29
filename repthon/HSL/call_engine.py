# Venom Userbot
# Copyright (C) 2026 Abdullah (Venom). All Rights Reserved
# الـمـالـك: @S_G0C7
# مـحـرك الـمـكـالـمـات الـمـتـقـدم (Call Engine) - بـدون تـقـطـيـع وبـدعـم الـطـابـور

import asyncio
import logging
from asyncio import Lock
from contextlib import suppress

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

# اسـتـدعـاء مـحـرك يـوتـيـوب الـذي صـمـمـنـاه مـسـبـقـاً داخـل نـفـس الـمـجـلـد
from .yt_api import YouTube

logging.basicConfig(level=logging.ERROR)
def LOGGER(name): return logging.getLogger(name)


class CallEngine:
    def __init__(self, client):
        self.client = client
        
        # -----------------------------------------------------------------
        # تـرقـيـة 2026: خـداع مـكـتـبـة PyTgCalls لـتـقـبـل الـيـوزربـوت الـمـعـدل
        # إجـبـار دالـة الـفـحـص (package_name) عـلـى إرجـاع 'telethon' دائـمـاً
        from pytgcalls.mtproto.bridged_client import BridgedClient
        BridgedClient.package_name = lambda c: 'telethon'
        # -----------------------------------------------------------------
        
        self.app = PyTgCalls(client)
        self.queue: dict[int, list] = {}
        self.chat_locks: dict[int, Lock] = {}
        self._stream_end_cache = {}

    def get_lock(self, chat_id: int) -> Lock:
        """لـمـنـع الـتـداخـل بـيـن الـطـلـبـات فـي نـفـس الـمـجـمـوعـة"""
        if chat_id not in self.chat_locks:
            self.chat_locks[chat_id] = Lock()
        return self.chat_locks[chat_id]

    async def start(self):
        """تـشـغـيـل مـحـرك الـمـكـالـمـات وتـفـعـيـل مـسـتـمـعـي الـأحـداث"""
        self._setup_decorators()
        try:
            await self.app.start()
        except PyTgCallsAlreadyRunning:
            pass
        LOGGER("CallEngine").info("تـم تـشـغـيـل مـحـرك הـمـكـالـمـات بـنـجـاح.")

    def _setup_decorators(self):
        """إعـداد الـفـلاتـر والـمـراقـبـيـن لـلـانـتـقـال الـتـلـقـائـي والـأخـطـاء"""
        
        @self.app.on_update(filters.stream_end())
        async def on_stream_end(client: PyTgCalls, update: StreamEnded):
            chat_id = update.chat_id
            
            # مـنـع الـتـكـرار الـوهـمـي לـحـدث انـتـهـاء الـبـث (بـفـاصـل 2 ثـوانٍ)
            current_time = asyncio.get_running_loop().time()
            if chat_id in self._stream_end_cache:
                if current_time - self._stream_end_cache[chat_id] < 2.0:
                    return
            self._stream_end_cache[chat_id] = current_time
            self._stream_end_cache = {cid: t for cid, t in self._stream_end_cache.items() if current_time - t < 5.0}
            
            await self._play_next(chat_id)

        @self.app.on_update(filters.chat_update(ChatUpdate.Status.LEFT_CALL))
        async def on_left_call(client: PyTgCalls, update: Update):
            await self.stop(update.chat_id)
            
        @self.app.on_update(filters.call_participant(GroupCallParticipant.Action.KICKED))
        async def on_kicked(client: PyTgCalls, update: Update):
            await self.stop(update.chat_id)

    def _build_stream(self, path: str, is_video: bool = False) -> MediaStream:
        """بـنـاء مـجـرى الـبـيـانـات مـع اسـتـغـلال مـوارد الـسـيـرفـر بـالـكـامـل"""
        # -threads 0 : يـجـعـل FFmpeg يـسـتـخـدم كـافـة أنـويـة الـمـعـالـج
        ffmpeg_opts = "-probesize 10M -analyzeduration 10M -threads 0 "
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        }
        
        return MediaStream(
            media_path=str(path),
            audio_parameters=AudioQuality.HIGH,
            video_parameters=VideoQuality.HD_720p if is_video else None,
            video_flags=MediaStream.Flags.REQUIRED if is_video else MediaStream.Flags.IGNORE,
            audio_flags=MediaStream.Flags.REQUIRED,
            ffmpeg_parameters=ffmpeg_opts,
            headers=headers
        )

    async def play_or_queue(self, chat_id: int, url: str, title: str, is_video: bool = False, force: bool = False):
        """إضـافـة الـمـقـطـع لـلـطـابـور أو تـشـغـيـلـه مـبـاشـرةً"""
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
                    return f"**• تـم الـبـدء بـتـشـغـيـل ↶** `{title}`"
                else:
                    self.queue[chat_id].pop(0)
                    return "**⤶ حـدث خـطـأ أثـنـاء جـلـب رابـط הـبـث الـمـبـاشـر.**"
            else:
                self.queue[chat_id].append(track)
                position = len(self.queue[chat_id]) - 1
                return f"**• تـمـت الـإضـافـة لـلـطـابـور ↶** `{title}`\n**• الـمـركـز ↶** `{position}`"

    async def _execute_play(self, chat_id: int, track: dict):
        """مـعـالـجـة الـرابط وتـشـغـيـلـه عـبـر PyTgCalls"""
        url = track["url"]
        is_video = track["is_video"]
        
        # اسـتـخـدام مـحـرك الـيـوتـيـوب لـجـلـب الـرابـط الـمـبـاشـر الـسـريـع
        direct_link = await YouTube.get_direct_link(url, audio_only=not is_video)
        if not direct_link:
            # مـحـاولـة الـتـحـمـيـل إلـى הـرام كـبـديـل إذا فـشـل الـرابـط الـمـبـاشـر
            direct_link, _ = await YouTube.download(url, is_video=is_video)
            
        if not direct_link:
            return False

        stream = self._build_stream(direct_link, is_video=is_video)
        
        try:
            await self.app.play(chat_id, stream, config=GroupCallConfig(auto_start=True))
            return True
        except Exception as e:
            LOGGER("CallEngine").error(f"Play Error: {e}")
            return False

    async def _play_next(self, chat_id: int):
        """تـشـغـيـل الـمـقـطـع الـتـالـي فـي الـطـابـور"""
        async with self.get_lock(chat_id):
            if chat_id in self.queue and len(self.queue[chat_id]) > 0:
                self.queue[chat_id].pop(0) # إزالـة الـمـقـطـع الـمـنـتـهـي
                
                if len(self.queue[chat_id]) > 0:
                    next_track = self.queue[chat_id][0]
                    await self._execute_play(chat_id, next_track)
                else:
                    await self.stop(chat_id, clear_only=False)
            else:
                await self.stop(chat_id, clear_only=False)

    async def skip(self, chat_id: int):
        """تـخـطـي الـمـقـطـع الـحـالـي"""
        if chat_id not in self.queue or len(self.queue[chat_id]) <= 1:
            await self.stop(chat_id)
            return "**⤶ الـطـابـور فـارغ، تـم إيـقـاف الـتـشـغـيـل والـمـغـادرة.**"
            
        async with self.get_lock(chat_id):
            self.queue[chat_id].pop(0)
            next_track = self.queue[chat_id][0]
            success = await self._execute_play(chat_id, next_track)
            
        if success:
            return f"**• تـم الـتـخـطـي.**\n**• يـعـمـل الـآن ↶** `{next_track['title']}`"
        return "**⤶ حـدث خـطـأ أثـنـاء הـتـخـطـي.**"

    async def stop(self, chat_id: int, clear_only: bool = False):
        """إيـقـاف الـتـشـغـيـل وتـفـريـغ الـطـابـور"""
        if chat_id in self.queue:
            self.queue[chat_id].clear()
            
        if not clear_only:
            with suppress(Exception):
                await self.app.leave_call(chat_id)

    async def pause(self, chat_id: int):
        """إيـقـاف مـؤقـت"""
        with suppress(Exception):
            await self.app.pause(chat_id)

    async def resume(self, chat_id: int):
        """اسـتـئـنـاف הـتـشـغـيـل"""
        with suppress(Exception):
            await self.app.resume(chat_id)
            
    def get_playlist(self, chat_id: int) -> list:
        """جـلـب قـائـمـة الـتـشـغـيـل الـحـالـيـة"""
        return self.queue.get(chat_id, [])
