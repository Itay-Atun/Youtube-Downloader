#!/usr/bin/python3
from  pytube import YouTube
import ssl
from moviepy.editor import VideoFileClip
import os
import re
from typing import Optional

try:
    import yt_dlp  # type: ignore
except Exception:
    yt_dlp = None  # Fallback only if installed

try:
    import imageio_ffmpeg  # type: ignore
except Exception:
    imageio_ffmpeg = None

ssl._create_default_https_context = ssl._create_stdlib_context

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PLAYLIST_DIR = os.path.join(BASE_DIR, "playlist")
CONVERTED_DIR = os.path.join(BASE_DIR, "converted")

def ensure_directories() -> None:
    os.makedirs(PLAYLIST_DIR, exist_ok=True)
    os.makedirs(CONVERTED_DIR, exist_ok=True)

def normalize_youtube_url(raw: str) -> Optional[str]:
    """Return a clean watch URL from various YouTube URL formats or None if invalid."""
    line = raw.strip()
    if not line or line.startswith("#"):
        return None
    # Accept watch URLs and short youtu.be; strip extraneous params
    # Short url
    m = re.match(r"https?://(?:www\.)?youtu\.be/([\w-]{11})", line)
    if m:
        video_id = m.group(1)
        return f"https://www.youtube.com/watch?v={video_id}"
    # Standard watch URL
    m = re.match(r"https?://(?:www\.)?youtube\.com/watch\?([^\s#]+)", line)
    if m:
        # Keep only v= parameter
        query = m.group(1)
        for part in query.split('&'):
            if part.startswith('v=') and len(part[2:]) == 11:
                return f"https://www.youtube.com/watch?v={part[2:]}"
    return line if line.startswith("http") else None

def download_with_ytdlp(url: str) -> bool:
    """Download a single URL as MP3 into CONVERTED_DIR using yt_dlp.
    Returns True on success, False otherwise.
    """
    if yt_dlp is None:
        return False
    ffmpeg_path = None
    if imageio_ffmpeg is not None:
        try:
            candidate = imageio_ffmpeg.get_ffmpeg_exe()
            if candidate and os.path.exists(candidate):
                ffmpeg_path = candidate
            else:
                ffmpeg_path = None
        except Exception:
            ffmpeg_path = None
    # Options to extract best audio and convert to mp3
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(CONVERTED_DIR, '%(title)s.%(ext)s'),
        'quiet': True,
        'noprogress': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '0',
        }],
    }
    if ffmpeg_path:
        ydl_opts['ffmpeg_location'] = ffmpeg_path
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return True
    except Exception as e:
        print(f"yt_dlp failed: {e}")
        return False

# Downloading Youtube Video in mp4 Format
def download_from_youtube(musicFileInput: str) -> None:
    with open(musicFileInput, "r", encoding="utf-8") as musicFile:
        for idx, line in enumerate(musicFile, start=1):
            url = normalize_youtube_url(line)
            if not url:
                continue
            # Prefer yt_dlp audio extraction to mp3
            if download_with_ytdlp(url):
                print(f"downloaded (mp3): {url}")
                continue
            # Fallback to pytube -> mp4 -> convert via MoviePy
            try:
                yt = YouTube(url)
                print(f"downloading {yt.watch_url}")
                stream = (
                    yt.streams.filter(progressive=True, file_extension="mp4")
                    .order_by("resolution")
                    .desc()
                    .first()
                ) or yt.streams.filter(file_extension="mp4").first()
                if not stream:
                    print(f"No MP4 stream found for line {idx}: {url}")
                    continue
                stream.download(output_path=PLAYLIST_DIR)
            except Exception as e:
                print(f"Failed to download with pytube (line {idx}): {url} -> {e}")

# Converting downloaded mp4 to mp3 files
def convert_to_mp3() -> None:
    try:
        entries = os.listdir(PLAYLIST_DIR)
    except FileNotFoundError:
        entries = []
    for fileName in entries:
        if not fileName.lower().endswith(".mp4"):
            continue
        src_path = os.path.join(PLAYLIST_DIR, fileName)
        base_name, _ = os.path.splitext(fileName)
        dst_path = os.path.join(CONVERTED_DIR, f"{base_name}.mp3")
        print(f"Converting {fileName}")
        video = None
        try:
            video = VideoFileClip(src_path)
            audio = video.audio
            if audio is None:
                print(f"No audio track found in {fileName}")
                continue
            audio.write_audiofile(dst_path)
        finally:
            if video is not None:
                try:
                    video.close()
                except Exception:
                    pass

# Main function to run program
def main() -> None:
    ensure_directories()
    music_txt = os.path.join(BASE_DIR, "music.txt")
    download_from_youtube(music_txt)

# Running program locally
if __name__ == "__main__":
   main()