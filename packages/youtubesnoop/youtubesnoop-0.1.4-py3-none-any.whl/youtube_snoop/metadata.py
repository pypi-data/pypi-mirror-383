"""Metadata extraction, prompting, and tagging functionality."""

from pathlib import Path
from typing import Dict, Optional, List
import questionary
from mutagen.flac import FLAC
import musicbrainzngs
import click


class MetadataManager:
    """Handles metadata prompting and file tagging."""

    def __init__(self, interactive: bool = True):
        self.interactive = interactive
        # Set up MusicBrainz client
        musicbrainzngs.set_useragent(
            "YoutubeSnoop",
            "0.1",
            "https://github.com/anderslatif/YoutubeSnoop"
        )

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

    def correct_metadata_interactive(self, path: Path) -> bool:
        """Search MusicBrainz and correct metadata for files in place.

        Args:
            path: Path to file or directory containing FLAC files

        Returns:
            True if metadata was corrected, False otherwise
        """
        if not self.interactive:
            return False

        # Get list of FLAC files
        if path.is_file():
            if path.suffix.lower() != '.flac':
                return False
            flac_files = [path]
            # For single file, extract metadata
            audio = FLAC(path)
            artist = audio.get('artist', [''])[0]
            title = audio.get('title', [''])[0]
            album = audio.get('album', [''])[0]
        else:
            flac_files = sorted(path.glob('*.flac'))
            if not flac_files:
                return False
            # For album, get metadata from first file
            audio = FLAC(flac_files[0])
            artist = audio.get('artist', [''])[0]
            album = audio.get('album', [''])[0]
            title = None

        if not artist or (not album and not title):
            click.echo("⚠️  No existing metadata found to search with")
            return False

        # Search MusicBrainz
        click.echo(f"\n🔍 Searching MusicBrainz for: {artist} - {album or title}")

        try:
            if album:
                # Search for album/release
                results = musicbrainzngs.search_releases(
                    artist=artist,
                    release=album,
                    limit=5
                )

                if not results.get('release-list'):
                    click.echo("❌ No matches found on MusicBrainz")
                    return False

                # Present options to user
                choices = []
                for release in results['release-list'][:5]:
                    artist_name = release.get('artist-credit', [{}])[0].get('artist', {}).get('name', 'Unknown')
                    release_name = release.get('title', 'Unknown')
                    date = release.get('date', 'Unknown year')
                    score = release.get('ext:score', '0')
                    label = f"{artist_name} - {release_name} ({date}) [Match: {score}%]"
                    choices.append((label, release))

                choices.append(("Skip - Keep current metadata", None))

                selected = questionary.select(
                    "Select the correct release:",
                    choices=[c[0] for c in choices]
                ).ask()

                if not selected or selected.startswith("Skip"):
                    click.echo("⏭️  Skipping metadata correction")
                    return False

                # Get the selected release
                selected_idx = [c[0] for c in choices].index(selected)
                release = choices[selected_idx][1]

                # Get full release details with recordings
                release_id = release['id']
                release_details = musicbrainzngs.get_release_by_id(
                    release_id,
                    includes=['recordings', 'artist-credits']
                )['release']

                # Apply metadata to album
                self._apply_release_metadata(flac_files, release_details)
                click.echo("✅ Metadata corrected from MusicBrainz")
                return True

            else:
                # Search for single recording
                results = musicbrainzngs.search_recordings(
                    artist=artist,
                    recording=title,
                    limit=5
                )

                if not results.get('recording-list'):
                    click.echo("❌ No matches found on MusicBrainz")
                    return False

                # Present options to user
                choices = []
                for recording in results['recording-list'][:5]:
                    artist_name = recording.get('artist-credit', [{}])[0].get('artist', {}).get('name', 'Unknown')
                    title_name = recording.get('title', 'Unknown')
                    score = recording.get('ext:score', '0')
                    label = f"{artist_name} - {title_name} [Match: {score}%]"
                    choices.append((label, recording))

                choices.append(("Skip - Keep current metadata", None))

                selected = questionary.select(
                    "Select the correct recording:",
                    choices=[c[0] for c in choices]
                ).ask()

                if not selected or selected.startswith("Skip"):
                    click.echo("⏭️  Skipping metadata correction")
                    return False

                # Get the selected recording
                selected_idx = [c[0] for c in choices].index(selected)
                recording = choices[selected_idx][1]

                # Apply metadata to single file
                self._apply_recording_metadata(flac_files[0], recording)
                click.echo("✅ Metadata corrected from MusicBrainz")
                return True

        except Exception as e:
            click.echo(f"⚠️  Error searching MusicBrainz: {e}")
            return False

    def _apply_release_metadata(self, flac_files: List[Path], release: Dict):
        """Apply release metadata to FLAC files."""
        artist = release.get('artist-credit', [{}])[0].get('artist', {}).get('name', '')
        album = release.get('title', '')
        date = release.get('date', '')

        # Get track list
        medium_list = release.get('medium-list', [])
        if not medium_list:
            return

        tracks = medium_list[0].get('track-list', [])

        # Apply to each file
        for idx, flac_file in enumerate(flac_files):
            audio = FLAC(flac_file)
            audio['artist'] = artist
            audio['album'] = album

            if date:
                audio['date'] = date[:4]  # Just the year

            # Try to match track
            if idx < len(tracks):
                track = tracks[idx]
                recording = track.get('recording', {})
                track_title = recording.get('title', audio.get('title', [''])[0])
                audio['title'] = track_title
                audio['tracknumber'] = str(track.get('position', idx + 1))

            audio.save()

    def _apply_recording_metadata(self, flac_file: Path, recording: Dict):
        """Apply recording metadata to a single FLAC file."""
        audio = FLAC(flac_file)

        artist = recording.get('artist-credit', [{}])[0].get('artist', {}).get('name', '')
        title = recording.get('title', '')

        if artist:
            audio['artist'] = artist
        if title:
            audio['title'] = title

        audio.save()
