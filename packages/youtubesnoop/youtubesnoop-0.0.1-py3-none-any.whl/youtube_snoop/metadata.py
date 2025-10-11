"""Metadata extraction, prompting, and tagging functionality."""

from pathlib import Path
from typing import Dict, Optional
import questionary
from mutagen.flac import FLAC


class MetadataManager:
    """Handles metadata prompting and file tagging."""

    def __init__(self, interactive: bool = True):
        self.interactive = interactive

    def prompt_album_info(self, suggestions: Dict[str, str]) -> Dict[str, str]:
        """Prompt user for album-level metadata.

        Args:
            suggestions: Dictionary with suggested values

        Returns:
            Dictionary with confirmed metadata (artist, album, year)
        """
        if not self.interactive:
            return suggestions

        artist = questionary.text(
            "Artist name:",
            default=suggestions.get('artist', '')
        ).ask()

        album = questionary.text(
            "Album name:",
            default=suggestions.get('album', '')
        ).ask()

        year = questionary.text(
            "Year:",
            default=suggestions.get('year', '')
        ).ask()

        return {
            'artist': artist,
            'album': album,
            'year': year
        }

    def prompt_single_video_info(self, suggestions: Dict[str, str]) -> Dict[str, str]:
        """Prompt user for single video metadata.

        Args:
            suggestions: Dictionary with suggested values

        Returns:
            Dictionary with confirmed metadata (artist, title, year)
        """
        if not self.interactive:
            return suggestions

        artist = questionary.text(
            "Artist name:",
            default=suggestions.get('artist', '')
        ).ask()

        title = questionary.text(
            "Song title:",
            default=suggestions.get('title', '')
        ).ask()

        year = questionary.text(
            "Year:",
            default=suggestions.get('year', '')
        ).ask()

        return {
            'artist': artist,
            'title': title,
            'year': year
        }

    def prompt_track_info(self, track_number: int, suggestion: str, auto_accept: bool = True) -> str:
        """Prompt user to confirm/edit track title.

        Args:
            track_number: Track number
            suggestion: Suggested track title
            auto_accept: If True, only prompt if suggestion seems unclear

        Returns:
            Confirmed track title
        """
        if not self.interactive:
            return suggestion

        # Auto-accept if the suggestion looks good (not empty, not just "Track N")
        if auto_accept and suggestion and not suggestion.startswith('Track '):
            return suggestion

        title = questionary.text(
            f"Track {track_number} title:",
            default=suggestion
        ).ask()

        return title

    def tag_flac(self, file_path: Path, metadata: Dict[str, str]):
        """Write metadata tags to FLAC file.

        Args:
            file_path: Path to FLAC file
            metadata: Dictionary containing tags (artist, album, title, tracknumber, date)
        """
        audio = FLAC(file_path)

        if 'artist' in metadata:
            audio['artist'] = metadata['artist']
        if 'album' in metadata:
            audio['album'] = metadata['album']
        if 'title' in metadata:
            audio['title'] = metadata['title']
        if 'tracknumber' in metadata:
            audio['tracknumber'] = str(metadata['tracknumber'])
        if 'date' in metadata:
            audio['date'] = str(metadata['date'])

        audio.save()
