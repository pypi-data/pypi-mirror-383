#!/usr/bin/env python3

import argparse
import subprocess
import json
import sys
import shutil

# Metadata
__version__ = "0.3.0"
__author__ = "Mallik Mohammad Musaddiq"
__email__ = "mallikmusaddiq1@gmail.com"
__github__ = "https://github.com/mallikmusaddiq1/yt-chap"

def seconds_to_hms(seconds: float | None) -> str:
    """Converts seconds to HH:MM:SS.mmm format or 'N/A' if None."""
    if seconds is None:
        return "N/A"
    if seconds < 0:
        seconds = 0
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = seconds % 60
    whole_s = int(s)
    ms = int(round((s - whole_s) * 1000))
    return f"{h:02}:{m:02}:{whole_s:02}.{ms:03}"

def print_chapters(chapters: list, url: str, json_output: bool = False, ffmpeg_metadata: bool = False):
    """Prints chapters in a table format, JSON format, or FFmpeg metadata format."""
    if json_output:
        print(json.dumps(chapters, indent=2))
        return
    if ffmpeg_metadata:
        print(';FFMETADATA1')
        for chapter in chapters:
            start_time = int(chapter['start_time'] * 1000)  # Convert to milliseconds
            end_time = int(chapter['end_time'] * 1000)      # Convert to milliseconds
            title = chapter['title'].replace('=', '\\=')    # Escape '=' for FFmpeg
            print(f'[CHAPTER]')
            print(f'TIMEBASE=1/1000')
            print(f'START={start_time}')
            print(f'END={end_time}')
            print(f'title={title}\n')
        return

    print(f"[info] Chapters from: {url}\n")
    print(f"{'No.':<4} | {'Start':<13} | {'End':<13} | {'Duration':<13} | Title")
    print("-" * 80)

    for i, chap in enumerate(chapters, 1):
        start_time = chap.get("start_time")
        end_time = chap.get("end_time")
        title = chap.get("title", "No Title")
        start = seconds_to_hms(start_time)
        if end_time is None:
            end = "N/A"
            duration = "N/A"
        else:
            end = seconds_to_hms(end_time)
            duration_sec = end_time - (start_time or 0)
            duration = seconds_to_hms(max(duration_sec, 0))
        print(f"{i:<4} | {start:<13} | {end:<13} | {duration:<13} | {title}")

def run_yt_dlp(extra_args: list, url: str):
    """Runs yt-dlp with the given extra args."""
    cmd = ['yt-dlp'] + extra_args + ['--no-warnings']
    try:
        result = subprocess.run(
            cmd + [url],
            capture_output=True,
            text=True,
            check=True,
            encoding='utf-8'
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running yt-dlp: {e}", file=sys.stderr)
        if e.stderr:
            print(f"yt-dlp error:\n{e.stderr.strip()}", file=sys.stderr)
        raise

def main():
    """Main entry point of the script."""
    # Check if yt-dlp is installed
    if not shutil.which('yt-dlp'):
        print("\nError: 'yt-dlp' not found.", file=sys.stderr)
        print("Please ensure Python is installed, then install yt-dlp using:", file=sys.stderr)
        print("   pip install --upgrade yt-dlp\n", file=sys.stderr)
        sys.exit(1)

    parser = argparse.ArgumentParser(
        description="yt-chap - Fetch and display video chapters from any yt-dlp supported URL.",
    )
    parser.add_argument("url", nargs="?", help="Video URL (from any yt-dlp supported site)")
    parser.add_argument("--version", "-v", action="store_true", help="show version and author info")
    parser.add_argument("-q", "--quiet", action="store_true", help="output only the main content without extra logs")
    output_group = parser.add_mutually_exclusive_group()
    output_group.add_argument("-j", "--json", action="store_true", help="output chapters in JSON format")
    output_group.add_argument("-f", "--ffmpeg-metadata", action="store_true", help="output chapters in FFmpeg metadata format")
    output_group.add_argument("-t", "--table", action="store_true", help="output chapters in table format")
    args = parser.parse_args()

    if args.version:
        print(f"yt-chap v{__version__}")
        print(f"\nAuthor : {__author__}")
        print(f"Email  : {__email__}")
        print(f"GitHub : {__github__}")
        sys.exit(0)

    if not args.url:
        parser.print_help()
        sys.exit(1)

    if not (args.json or args.ffmpeg_metadata or args.table):
        print("\n[error] One of -j/--json, -f/--ffmpeg-metadata, or -t/--table must be specified.\n", file=sys.stderr)
        sys.exit(1)

    url = args.url

    if not args.quiet:
        print(f"\n[info] Fetching metadata for {url}...\n")

    try:
        json_out = run_yt_dlp(['--dump-json'], url)
        lines = json_out.splitlines()
        if len(lines) > 1:
            if not args.quiet:
                print("\n[warning] Multiple entries detected (possibly a playlist). Using the first entry.\n", file=sys.stderr)
            info_str = lines[0]
        else:
            info_str = json_out
        info = json.loads(info_str)

        chapters = info.get('chapters') or []
        if not isinstance(chapters, list):
            raise ValueError("Chapters data is not a list.")

        if not chapters:
            duration = info.get('duration')
            if not isinstance(duration, (int, float)) or duration <= 0:
                raise ValueError("Duration unavailable or invalid.")
            if not args.quiet:
                print("\n[info] No chapter metadata found.\n\n[info] Using video duration from metadata.\n")
            chapters = [{
                "start_time": 0.0,
                "end_time": duration,
                "title": "Full Video"
            }]

        print_chapters(chapters, url, args.json, args.ffmpeg_metadata)

    except (subprocess.CalledProcessError, json.JSONDecodeError, ValueError, KeyError) as e:
        print(f"\n[error] Failed to process metadata for '{url}': {e}\n", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\n[error] An unexpected error occurred: {e}\n", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()