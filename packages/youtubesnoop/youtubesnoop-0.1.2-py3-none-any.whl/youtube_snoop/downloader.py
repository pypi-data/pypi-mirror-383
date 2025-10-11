"""YouTube download functionality using yt-dlp."""

from pathlib import Path
from typing import Dict, List, Optional
import yt_dlp


class YouTubeDownloader:
    """Handles downloading videos/playlists from YouTube."""

    def __init__(self, output_dir: Path, video_mode: bool = False):
        self.output_dir = Path(output_dir)
        self.temp_dir = self.output_dir / '.youtube_snoop_temp'
        self.temp_dir.mkdir(exist_ok=True)
        self.video_mode = video_mode
        self.file_ext = 'mp4' if video_mode else 'flac'

    def get_info(self, url: str) -> Dict:
        """Extract video/playlist information without downloading.

        Args:
            url: YouTube URL

        Returns:
            Dictionary containing video/playlist metadata
        """
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': 'in_playlist',
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return info

    def is_playlist(self, info: Dict) -> bool:
        """Check if the URL is a playlist."""
        return info.get('_type') == 'playlist'

    def download(self, video_id: str, url: str) -> List[Path]:
        """Download video to temporary directory.

        Args:
            video_id: Video ID for filename
            url: YouTube URL

        Returns:
            List of downloaded file paths
        """
        output_template = str(self.temp_dir / f'{video_id}.%(ext)s')

        if self.video_mode:
            # Download video in MP4 format (best quality, widely compatible)
            ydl_opts = {
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                'outtmpl': output_template,
                'merge_output_format': 'mp4',
                'quiet': False,
                'no_warnings': False,
            }
        else:
            # Download audio only and convert to FLAC
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': output_template,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'flac',
                }],
                'quiet': False,
                'no_warnings': False,
            }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        # Find the downloaded file
        downloaded_files = list(self.temp_dir.glob(f'{video_id}.{self.file_ext}'))
        return downloaded_files

    def cleanup(self):
        """Remove temporary download directory."""
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
