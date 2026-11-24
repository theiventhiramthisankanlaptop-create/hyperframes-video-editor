#!/usr/bin/env python3
"""Download a video with yt-dlp and save metadata for editing/review.

Only download videos you own or are authorized to download. Respect the
platform's terms, copyright, and any access restrictions.
"""
import argparse
import json
import sys
from pathlib import Path

import yt_dlp


def main():
    parser = argparse.ArgumentParser(
        description="Download an authorized video and save its metadata for study."
    )
    parser.add_argument("url", help="Video URL")
    parser.add_argument("-o", "--output-dir", default="downloads", help="Download folder (default: downloads)")
    parser.add_argument("--format", dest="format_id", default="bv*+ba/b",
                        help="yt-dlp format selector (default: best video + best audio)")
    parser.add_argument("--subtitles", action="store_true",
                        help="Also download available subtitles")
    parser.add_argument("--auto-subs", action="store_true",
                        help="Also download auto-generated subtitles when available")
    parser.add_argument("--sub-langs", default="en.*,si.*,ta.*",
                        help="Subtitle language selector (default: en.*,si.*,ta.*)")
    parser.add_argument("--no-playlist", action="store_true", default=True,
                        help="Download only the single video, not a playlist (default)")
    args = parser.parse_args()

    out_dir = Path(args.output_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    info_holder = {}

    def save_info(info):
        # Keep useful study metadata while omitting bulky/temporary fields.
        keys = (
            "id", "title", "description", "duration", "upload_date", "uploader",
            "channel", "webpage_url", "original_url", "view_count", "like_count",
            "categories", "tags", "language", "resolution", "width", "height",
            "fps", "filesize", "ext", "thumbnail"
        )
        clean = {key: info.get(key) for key in keys if info.get(key) is not None}
        info_path = out_dir / f"{info.get('id', 'video')}.info.json"
        info_path.write_text(json.dumps(clean, ensure_ascii=False, indent=2), encoding="utf-8")
        info_holder["path"] = info_path

    options = {
        "format": args.format_id,
        "outtmpl": str(out_dir / "%(title).180B [%(id)s].%(ext)s"),
        "merge_output_format": "mp4",
        "noplaylist": args.no_playlist,
        "writeinfojson": True,
        "writedescription": True,
        "quiet": False,
        "no_warnings": False,
        "overwrites": False,
        "progress_hooks": [],
        "postprocessors": [],
    }
    if args.subtitles or args.auto_subs:
        options.update({
            "writesubtitles": args.subtitles,
            "writeautomaticsub": args.auto_subs,
            "subtitleslangs": args.sub_langs.split(","),
            "subtitlesformat": "srt/best",
        })

    try:
        with yt_dlp.YoutubeDL(options) as ydl:
            info = ydl.extract_info(args.url, download=True)
            if info:
                save_info(info)
                print(f"\nDownloaded video: {info.get('title', 'video')}")
                if info_holder.get("path"):
                    print(f"Study metadata: {info_holder['path']}")
                print(f"Output folder: {out_dir}")
    except yt_dlp.utils.DownloadError as exc:
        print(f"Download failed: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
