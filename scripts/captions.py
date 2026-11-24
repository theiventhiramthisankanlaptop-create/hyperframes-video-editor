#!/usr/bin/env python3
"""Generate SRT subtitles from video/audio with faster-whisper."""
import argparse
import subprocess
import sys
from pathlib import Path

from faster_whisper import WhisperModel


def srt_time(seconds: float) -> str:
    ms = max(0, round(seconds * 1000))
    hours, ms = divmod(ms, 3_600_000)
    minutes, ms = divmod(ms, 60_000)
    secs, ms = divmod(ms, 1000)
    return f"{hours:02}:{minutes:02}:{secs:02},{ms:03}"


def main():
    parser = argparse.ArgumentParser(description="Transcribe media and create SRT captions.")
    parser.add_argument("input", help="Input audio/video file")
    parser.add_argument("-o", "--output", help="Output .srt path (default: input filename.srt)")
    parser.add_argument("--model", default="small", help="Whisper model: tiny, base, small, medium, large-v3")
    parser.add_argument("--language", default=None, help="Language code such as en, si, ta; omit for auto-detect")
    parser.add_argument("--device", default="auto", choices=["auto", "cpu", "cuda"])
    parser.add_argument("--compute-type", default="default", help="e.g. int8 for CPU or float16 for CUDA")
    parser.add_argument("--burn", help="Optional output video path to burn captions into")
    args = parser.parse_args()

    source = Path(args.input)
    if not source.is_file():
        parser.error(f"Input file does not exist: {source}")
    output = Path(args.output) if args.output else source.with_suffix(".srt")

    print(f"Loading Whisper model '{args.model}' on {args.device}...")
    model = WhisperModel(args.model, device=args.device, compute_type=args.compute_type)
    segments, info = model.transcribe(
        str(source), language=args.language, vad_filter=True,
        word_timestamps=True, beam_size=5
    )
    print(f"Detected language: {info.language} (probability {info.language_probability:.2f})")

    count = 0
    with output.open("w", encoding="utf-8", newline="\n") as f:
        for count, segment in enumerate(segments, start=1):
            text = segment.text.strip()
            if not text:
                continue
            f.write(f"{count}\n{srt_time(segment.start)} --> {srt_time(segment.end)}\n{text}\n\n")
    print(f"Wrote captions: {output}")

    if args.burn:
        # Use an absolute, POSIX-style path and escape characters for FFmpeg's filter parser.
        subtitle_path = str(output.resolve()).replace("\\", "/")
        for char in ("\\", ":", "'", ",", "[", "]"):
            subtitle_path = subtitle_path.replace(char, "\\" + char)
        command = [
            "ffmpeg", "-hide_banner", "-y", "-i", str(source),
            "-vf", f"subtitles='{subtitle_path}':force_style='FontName=Arial,FontSize=16,Outline=2,Shadow=1,Alignment=2,MarginV=100'",
            "-c:v", "libx264", "-preset", "medium", "-crf", "18",
            "-c:a", "copy", "-movflags", "+faststart", args.burn
        ]
        print("Burning captions into video...")
        subprocess.run(command, check=True)
        print(f"Wrote captioned video: {args.burn}")


if __name__ == "__main__":
    try:
        main()
    except FileNotFoundError as exc:
        print(f"Missing executable or file: {exc}. Install FFmpeg and ensure it is on PATH.", file=sys.stderr)
        sys.exit(1)
    except subprocess.CalledProcessError as exc:
        print(f"FFmpeg failed with exit code {exc.returncode}.", file=sys.stderr)
        sys.exit(exc.returncode or 1)
