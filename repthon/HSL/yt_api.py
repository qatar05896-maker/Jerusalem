# Venom Userbot
# Copyright (C) 2026 Abdullah (Venom). All Rights Reserved
# الـمـالـك: @S_G0C7
# مـلـف مـحـرك يـوتـيـوب الـخـلـفـي (Zero-Latency API)

import asyncio
import os
import logging
import yt_dlp
from concurrent.futures import ThreadPoolExecutor

logging.basicConfig(level=logging.ERROR)
def LOGGER(name): return logging.getLogger(name)

# تـحـديـد الـمـسـارات بـشـكـل مـطـلـق مـن جـذر الـمـشـروع
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COOKIES_PATH = os.path.join(BASE_DIR, "plugins", "cookies.txt")

# اسـتـغـلال مـسـاحـة الـرام لـلـتـحـمـيـل الـسـريـع (إذ كـانـت مـتـاحـة بـيـئـة لـيـنـكـس)
if os.path.exists("/dev/shm"):
    DOWNLOAD_PATH = "/dev/shm/RepthonDownloads"
else:
    DOWNLOAD_PATH = os.path.join(BASE_DIR, "temp_downloads")

if not os.path.exists(DOWNLOAD_PATH):
    os.makedirs(DOWNLOAD_PATH, exist_ok=True)


class YouTubeDownloaderAPI:
    def __init__(self):
        # اسـتـخـدام 10 عـمـال فـي الـخـلـفـيـة لـاسـتـغـلال أنـويـة الـسـيـرفـر كـامـلـة
        self.pool = ThreadPoolExecutor(max_workers=10)
        self.playlist_limit = 10

    async def get_direct_link(self, link: str, audio_only: bool = False):
        """لـاسـتـخـراج الـرابـط الـمـبـاشـر لـاسـتـخـدامـه فـي تـدفـق الـمـكـالـمـات الـصـوتـيـة"""
        loop = asyncio.get_running_loop()
        
        def _extract():
            opts = {
                "format": "bestaudio/best" if audio_only else "best",
                "quiet": True,
                "no_warnings": True,
                "nocheckcertificate": True,
                "force_ipv4": True,
                "source_address": "0.0.0.0",
                "js_runtimes": {"node": {}},
                "remote_components": ["ejs:github"],
                "extractor_args": {
                    "youtube": {"player_client": ["web"]}
                }
            }
            if os.path.exists(COOKIES_PATH):
                opts["cookiefile"] = COOKIES_PATH

            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(link, download=False)
                if not info: return None
                if 'entries' in info and info['entries']:
                    return info['entries'][0].get("url")
                return info.get("url")
        
        try:
            return await loop.run_in_executor(self.pool, _extract)
        except Exception as e:
            LOGGER("YouTubeAPI").error(f"Extract Error: {e}")
            return None

    async def download(self, link: str, is_video: bool = False):
        """لـتـحـمـيـل الـمـقـطـع كـامـلـاً إلـى الـرام بـنـظـام الـخـطـوط الـمـتـعـددة"""
        loop = asyncio.get_running_loop()

        if is_video:
            fmt = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"
        else:
            fmt = "ba[ext=m4a]/ba/b"

        def _download_native():
            out_tmpl = os.path.join(DOWNLOAD_PATH, "%(title)s.%(ext)s")

            ydl_opts = {
                "format": fmt,
                "outtmpl": out_tmpl,
                "quiet": True,
                "no_warnings": True,
                "nocheckcertificate": True,
                
                # إعـدادات تـخـطـي حـظـر يـوتـيـوب كـمـا تـم الـاتـفـاق
                "force_ipv4": True,
                "source_address": "0.0.0.0",
                "geo_bypass": False, 
                
                "js_runtimes": {"node": {}},
                "remote_components": ["ejs:github"],
                "extractor_args": {
                    "youtube": {"player_client": ["web"]}
                },
                
                # عـمـلـيـة الـتـحـمـيـل الـمـتـوازيـة
                "concurrent_fragment_downloads": 10,  
                "http_chunk_size": 10485760,         
                "buffersize": 1024 * 1024 * 5,       
                "retries": 15,                       
                
                "noplaylist": False, 
                "ignoreerrors": True,
                "trim_file_name": 50,
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
            }
            
            if os.path.exists(COOKIES_PATH):
                ydl_opts["cookiefile"] = COOKIES_PATH
            
            if "list=" in link and self.playlist_limit > 0:
                ydl_opts["playlistend"] = self.playlist_limit
            
            if is_video:
                ydl_opts["merge_output_format"] = "mp4"

            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(link, download=True)
                    if not info: return None, None
                        
                    if 'entries' in info:
                        entries = [e for e in info['entries'] if e]
                        if entries: 
                            file_path = ydl.prepare_filename(entries[0])
                            return file_path, entries[0]
                    
                    file_path = ydl.prepare_filename(info)
                    return file_path, info
            except Exception as e:
                LOGGER("YouTubeAPI").error(f"Download Error: {e}")
            return None, None

        try:
            file_path, info = await loop.run_in_executor(self.pool, _download_native)
            if file_path and os.path.exists(file_path):
                return file_path, info
        except Exception:
            pass

        return None, None

YouTube = YouTubeDownloaderAPI()
