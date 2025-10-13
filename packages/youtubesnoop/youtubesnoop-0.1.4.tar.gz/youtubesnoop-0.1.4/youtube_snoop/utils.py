"""Utility functions for file organization and path management."""

from pathlib import Path
from typing import Dict
import shutil


def sanitize_filename(filename: str) -> str:
    """Remove or replace characters that are invalid in filenames.

    Args:
        filename: Raw filename string

    Returns:
        Sanitized filename
    """
    # Replace invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')

    # Remove leading/trailing spaces and dots
    filename = filename.strip('. ')

    return filename


def create_album_path(base_dir: Path, artist: str, year: str, album: str) -> Path:
    """Create directory structure: {artist}/{year} - {album}

    Args:
        base_dir: Base output directory
        artist: Artist name
        year: Album year
        album: Album name

    Returns:
        Path to album directory
    """
    artist_safe = sanitize_filename(artist)
    album_safe = sanitize_filename(album)

    album_dir = base_dir / artist_safe / f"{year} - {album_safe}"
    album_dir.mkdir(parents=True, exist_ok=True)

    return album_dir


def create_track_filename(track_number: int, title: str, extension: str = 'flac') -> str:
    """Create filename: {tracknumber}. {title}.{extension}

    Args:
        track_number: Track number (will be zero-padded to 2 digits)
        title: Track title
        extension: File extension (default: flac)

    Returns:
        Filename string
    """
    title_safe = sanitize_filename(title)
    return f"{track_number:02d}. {title_safe}.{extension}"


def move_and_rename(src: Path, dest_dir: Path, new_filename: str) -> Path:
    """Move file to destination directory with new name.

    Args:
        src: Source file path
        dest_dir: Destination directory
        new_filename: New filename

    Returns:
        Final file path
    """
    dest_path = dest_dir / new_filename
    shutil.move(str(src), str(dest_path))
    return dest_path
