"""Cover art search and download functionality using MusicBrainz."""

import musicbrainzngs
from pathlib import Path
from typing import Optional, Dict
import requests
from mutagen.flac import FLAC, Picture
import filetype


class CoverArtManager:
    """Handles cover art search, download, and embedding."""

    def __init__(self):
        # Set up MusicBrainz client
        musicbrainzngs.set_useragent(
            "YoutubeSnoop",
            "0.1",
            "https://github.com/yourusername/YoutubeSnoop"
        )

    def search_cover_art(self, artist: str, album: str) -> Optional[str]:
        """Search for album cover art using MusicBrainz.

        Args:
            artist: Artist name
            album: Album name

        Returns:
            URL to cover art image, or None if not found
        """
        try:
            # Search for releases matching artist and album
            result = musicbrainzngs.search_releases(
                artist=artist,
                release=album,
                limit=5
            )

            if not result.get('release-list'):
                return None

            # Try each result until we find one with cover art
            for release in result['release-list']:
                release_id = release['id']
                try:
                    # Try to get cover art from Cover Art Archive
                    artwork = musicbrainzngs.get_image_list(release_id)
                    if artwork.get('images'):
                        # Get the front cover, or first image if no front specified
                        for image in artwork['images']:
                            if image.get('front'):
                                return image['image']
                        # If no front image, return first image
                        return artwork['images'][0]['image']
                except musicbrainzngs.musicbrainz.ResponseError:
                    # No cover art for this release, try next one
                    continue

            return None

        except Exception as e:
            print(f"Error searching for cover art: {e}")
            return None

    def download_cover_art(self, url: str, output_path: Path) -> bool:
        """Download cover art image to file.

        Args:
            url: URL to image
            output_path: Path to save image

        Returns:
            True if successful, False otherwise
        """
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()

            # Write image data
            output_path.write_bytes(response.content)

            # Detect image type and rename if needed
            kind = filetype.guess(output_path)
            if kind:
                correct_path = output_path.parent / f"Cover.{kind.extension}"
                if correct_path != output_path:
                    output_path.rename(correct_path)

            return True

        except Exception as e:
            print(f"Error downloading cover art: {e}")
            return False

    def find_cover_in_folder(self, folder: Path) -> Optional[Path]:
        """Look for Cover.jpg or Cover.png in folder.

        Args:
            folder: Folder to search

        Returns:
            Path to cover image if found, None otherwise
        """
        for ext in ['jpg', 'jpeg', 'png']:
            cover_path = folder / f"Cover.{ext}"
            if cover_path.exists():
                return cover_path
        return None

    def embed_cover_art(self, audio_file: Path, cover_image: Path) -> bool:
        """Embed cover art into FLAC file.

        Args:
            audio_file: Path to FLAC file
            cover_image: Path to cover image

        Returns:
            True if successful, False otherwise
        """
        try:
            audio = FLAC(audio_file)

            # Read image data
            image_data = cover_image.read_bytes()

            # Detect MIME type
            kind = filetype.guess(cover_image)
            if kind:
                mime = kind.mime
            else:
                mime = 'image/jpeg'  # Default fallback

            # Create Picture object
            picture = Picture()
            picture.type = 3  # Cover (front)
            picture.mime = mime
            picture.desc = 'Cover'
            picture.data = image_data

            # Add to FLAC file
            audio.clear_pictures()
            audio.add_picture(picture)
            audio.save()

            return True

        except Exception as e:
            print(f"Error embedding cover art: {e}")
            return False

    def process_album_cover(
        self,
        album_folder: Path,
        artist: str,
        album: str,
        audio_files: list[Path]
    ) -> bool:
        """Search, download, and embed cover art for an album.

        Args:
            album_folder: Folder containing the album
            artist: Artist name
            album: Album name
            audio_files: List of audio files to embed cover into

        Returns:
            True if cover art was processed successfully
        """
        # First check if cover already exists in folder
        cover_path = self.find_cover_in_folder(album_folder)

        # If not found, search and download
        if not cover_path:
            print(f"Searching for cover art for '{album}' by {artist}...")
            cover_url = self.search_cover_art(artist, album)

            if cover_url:
                print(f"Found cover art, downloading...")
                temp_cover = album_folder / "Cover.tmp"
                if self.download_cover_art(cover_url, temp_cover):
                    cover_path = self.find_cover_in_folder(album_folder)
                    print(f"✓ Cover art saved to {cover_path}")
                else:
                    print("✗ Failed to download cover art")
                    return False
            else:
                print("✗ No cover art found")
                return False

        # Embed cover art into all audio files
        if cover_path:
            print(f"Embedding cover art into {len(audio_files)} file(s)...")
            for audio_file in audio_files:
                self.embed_cover_art(audio_file, cover_path)
            print("✓ Cover art embedded")
            return True

        return False
