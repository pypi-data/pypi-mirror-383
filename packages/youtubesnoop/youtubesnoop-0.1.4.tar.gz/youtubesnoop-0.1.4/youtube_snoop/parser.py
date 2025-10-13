"""Parsing utilities for extracting metadata from titles and descriptions."""

import re
from typing import Dict, Optional, Tuple


class MetadataParser:
    """Extract artist, album, track info from video/playlist titles."""

    # Common patterns for video titles
    PATTERNS = [
        # "Artist - Song Title"
        re.compile(r'^(?P<artist>.+?)\s*[-–—]\s*(?P<title>.+)$'),
        # "01. Song Title" or "1. Song Title"
        re.compile(r'^\d+\.\s*(?P<title>.+)$'),
        # "Artist - Album - Track"
        re.compile(r'^(?P<artist>.+?)\s*[-–—]\s*(?P<album>.+?)\s*[-–—]\s*(?P<title>.+)$'),
    ]

    # Patterns for playlist titles
    PLAYLIST_PATTERNS = [
        # "Artist - Album (Year)" or "Artist - Album [Year]"
        re.compile(r'^(?P<artist>.+?)\s*[-–—]\s*(?P<album>.+?)\s*[\(\[](?P<year>\d{4})[\)\]]'),
        # "Album (Year)" or "Album [Year]"
        re.compile(r'^(?P<album>.+?)\s*[\(\[](?P<year>\d{4})[\)\]]'),
        # "Artist - Album"
        re.compile(r'^(?P<artist>.+?)\s*[-–—]\s*(?P<album>.+)$'),
    ]

    @staticmethod
    def clean_title(title: str) -> str:
        """Remove common extra text from titles.

        Args:
            title: Raw title string

        Returns:
            Cleaned title
        """
        # Remove common suffixes
        suffixes = [
            r'\s*\(Official.*?\)',
            r'\s*\[Official.*?\]',
            r'\s*\(Audio\)',
            r'\s*\[Audio\]',
            r'\s*\(HD\)',
            r'\s*\[HD\]',
            r'\s*\(Lyric.*?\)',
            r'\s*\[Lyric.*?\]',
        ]

        for suffix in suffixes:
            title = re.sub(suffix, '', title, flags=re.IGNORECASE)

        return title.strip()

    @staticmethod
    def parse_video_title(title: str) -> Dict[str, str]:
        """Parse artist and title from video title.

        Args:
            title: Video title

        Returns:
            Dictionary with parsed metadata
        """
        title = MetadataParser.clean_title(title)

        for pattern in MetadataParser.PATTERNS:
            match = pattern.match(title)
            if match:
                return match.groupdict()

        # If no pattern matches, return title as-is
        return {'title': title}

    @staticmethod
    def parse_playlist_title(title: str) -> Dict[str, str]:
        """Parse artist, album, year from playlist title.

        Args:
            title: Playlist title

        Returns:
            Dictionary with parsed metadata
        """
        for pattern in MetadataParser.PLAYLIST_PATTERNS:
            match = pattern.match(title)
            if match:
                return match.groupdict()

        # If no pattern matches, assume title is album name
        return {'album': title}

    @staticmethod
    def extract_year_from_date(date_str: str) -> Optional[str]:
        """Extract year from date string (e.g., '20231215').

        Args:
            date_str: Date string in YYYYMMDD format

        Returns:
            Year as string, or None
        """
        if date_str and len(date_str) >= 4:
            return date_str[:4]
        return None
