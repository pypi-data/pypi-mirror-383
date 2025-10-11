"""CLI interface for YoutubeSnoop."""

import click
import subprocess
from pathlib import Path
from youtube_snoop.downloader import YouTubeDownloader
from youtube_snoop.metadata import MetadataManager
from youtube_snoop.parser import MetadataParser
from youtube_snoop.coverart import CoverArtManager
from youtube_snoop.utils import create_album_path, create_track_filename, sanitize_filename


@click.command()
@click.argument('url')
@click.option('--video', is_flag=True, help='Download as video (mp4) instead of audio (flac)')
def main(url, video):
    """Download YouTube videos/playlists with metadata tagging.

    URL: YouTube video or playlist URL
    """
    click.echo(f"🎵 YoutubeSnoop - Analyzing URL...")

    current_dir = Path.cwd()
    downloader = YouTubeDownloader(current_dir, video_mode=video)
    metadata_mgr = MetadataManager(interactive=True)
    parser = MetadataParser()
    coverart_mgr = CoverArtManager()

    try:
        # Get video/playlist info
        info = downloader.get_info(url)
        is_playlist = downloader.is_playlist(info)

        if is_playlist:
            click.echo(f"📀 Detected playlist: {info.get('title', 'Unknown')}")
            process_playlist(info, downloader, metadata_mgr, parser, coverart_mgr, current_dir)
        else:
            click.echo(f"🎵 Detected single video: {info.get('title', 'Unknown')}")
            process_single_video(info, downloader, metadata_mgr, parser, current_dir)

    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        raise
    finally:
        downloader.cleanup()

    click.echo("✅ Download complete!")

    # Run beets for metadata correction
    run_beets(current_dir)


def process_single_video(info, downloader, metadata_mgr, parser, output_dir):
    """Process a single video download."""
    video_title = info.get('title', 'Unknown')
    upload_date = info.get('upload_date', '')

    # Parse metadata from title
    parsed = parser.parse_video_title(video_title)

    # Prepare suggestions
    suggestions = {
        'artist': parsed.get('artist', info.get('uploader', '')),
        'title': parsed.get('title', video_title),
        'year': parser.extract_year_from_date(upload_date) or '',
    }

    # Show detected info and confirm
    click.echo("\n📝 Detected metadata:")
    click.echo(f"  Artist: {suggestions['artist']}")
    click.echo(f"  Title: {suggestions['title']}")
    click.echo(f"  Year: {suggestions['year']}")
    click.echo()

    # Prompt for confirmation/correction
    metadata = metadata_mgr.prompt_single_video_info(suggestions)

    # Download
    click.echo("\n⬇️  Downloading...")
    downloaded_files = downloader.download(info['id'], info['webpage_url'])

    if not downloaded_files:
        click.echo("❌ No files were downloaded", err=True)
        return

    # Tag and rename
    source_file = downloaded_files[0]
    file_ext = downloader.file_ext
    final_filename = f"{sanitize_filename(metadata['title'])}.{file_ext}"
    final_path = output_dir / final_filename

    # Tag the file (only for FLAC)
    if not downloader.video_mode:
        metadata_mgr.tag_flac(source_file, {
            'artist': metadata['artist'],
            'title': metadata['title'],
            'date': metadata['year'],
        })

    # Move to final location
    source_file.rename(final_path)
    click.echo(f"💾 Saved: {final_path}")


def process_playlist(info, downloader, metadata_mgr, parser, coverart_mgr, output_dir):
    """Process a playlist download."""
    playlist_title = info.get('title', 'Unknown Playlist')
    entries = info.get('entries', [])

    if not entries:
        click.echo("❌ No videos found in playlist", err=True)
        return

    # Parse playlist metadata
    parsed_playlist = parser.parse_playlist_title(playlist_title)
    first_video = entries[0]

    # Prepare album-level suggestions
    suggestions = {
        'artist': parsed_playlist.get('artist', first_video.get('uploader', '')),
        'album': parsed_playlist.get('album', playlist_title),
        'year': parsed_playlist.get('year', parser.extract_year_from_date(first_video.get('upload_date', '')) or ''),
    }

    # Show detected info and confirm
    click.echo("\n📝 Detected album metadata:")
    click.echo(f"  Artist: {suggestions['artist']}")
    click.echo(f"  Album: {suggestions['album']}")
    click.echo(f"  Year: {suggestions['year']}")
    click.echo(f"  Tracks: {len(entries)}")
    click.echo()

    # Prompt for album info
    album_metadata = metadata_mgr.prompt_album_info(suggestions)

    # Create album directory
    album_dir = create_album_path(
        output_dir,
        album_metadata['artist'],
        album_metadata['year'],
        album_metadata['album']
    )

    click.echo(f"\n📁 Album folder: {album_dir.relative_to(output_dir)}")

    # Download and process each track
    audio_files = []
    for idx, entry in enumerate(entries, 1):
        video_title = entry.get('title', f'Track {idx}')
        parsed_track = parser.parse_video_title(video_title)
        track_title_suggestion = parsed_track.get('title', video_title)

        # Confirm track title
        track_title = metadata_mgr.prompt_track_info(idx, track_title_suggestion)

        # Download
        click.echo(f"⬇️  Downloading track {idx}/{len(entries)}...")
        downloaded_files = downloader.download(entry['id'], entry['url'])

        if not downloaded_files:
            click.echo(f"⚠️  Failed to download track {idx}", err=True)
            continue

        # Tag the file (only for FLAC)
        source_file = downloaded_files[0]
        if not downloader.video_mode:
            metadata_mgr.tag_flac(source_file, {
                'artist': album_metadata['artist'],
                'album': album_metadata['album'],
                'title': track_title,
                'tracknumber': idx,
                'date': album_metadata['year'],
            })

        # Rename and move
        final_filename = create_track_filename(idx, track_title, downloader.file_ext)
        final_path = album_dir / final_filename
        source_file.rename(final_path)
        click.echo(f"💾 Saved: {final_path.relative_to(output_dir)}")

        # Track audio files for cover art embedding
        if not downloader.video_mode:
            audio_files.append(final_path)

    # Search and embed cover art for the album (audio only)
    if not downloader.video_mode and audio_files:
        click.echo()
        coverart_mgr.process_album_cover(
            album_dir,
            album_metadata['artist'],
            album_metadata['album'],
            audio_files
        )


def run_beets(directory):
    """Run beets on the downloaded files for metadata correction."""
    click.echo("\n🎼 Running beets for metadata correction...")
    click.echo("(You can interact with beets now)\n")

    try:
        # Run beets import in the directory
        subprocess.run(['beet', 'import', str(directory)], check=False)
    except Exception as e:
        click.echo(f"⚠️  Error running beets: {e}")


if __name__ == '__main__':
    main()
