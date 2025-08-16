import os
import subprocess
import tempfile
from yt_dlp import YoutubeDL


def _get_file_size_mb(path):
    return os.path.getsize(path) / (1024 * 1024)


def download_instagram_video(url: str, max_mb: int) -> str | None:
    """Download Instagram video using yt-dlp. Compress if larger than max_mb."""
    try:
        tmp_dir = tempfile.mkdtemp()
        output_path = os.path.join(tmp_dir, "video.%(ext)s")

        ydl_opts = {
            "outtmpl": output_path,
            "format": "mp4+bestaudio/best",
            "quiet": True,
        }

        with YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            downloaded_path = ydl.prepare_filename(info_dict)

        # If too large, compress
        if _get_file_size_mb(downloaded_path) > max_mb:
            compressed_path = os.path.join(tmp_dir, "compressed.mp4")
            cmd = [
                "ffmpeg",
                "-i", downloaded_path,
                "-vcodec", "libx264",
                "-crf", "28",
                "-preset", "veryfast",
                "-acodec", "aac",
                compressed_path,
                "-y"  # overwrite
            ]
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            if os.path.exists(compressed_path):
                os.remove(downloaded_path)
                return compressed_path
            else:
                return None

        return downloaded_path

    except Exception as e:
        print(f"Download error: {e}")
        return None
      
