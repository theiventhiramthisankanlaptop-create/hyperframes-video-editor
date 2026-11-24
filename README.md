# HyperFrames Video Editor

A starter toolkit for short-form video editing with FFmpeg, faster-whisper captions, yt-dlp downloads, and HyperFrames.

## Requirements

- Node.js 22+
- Python 3.10+
- FFmpeg (includes ffprobe; the FFmpeg build must include the `subtitles` filter / libass to burn captions)

## Setup

```bash
npm install
python -m venv .venv
# Windows:
.venv\\Scripts\\activate
# macOS / Linux:
source .venv/bin/activate
pip install -r requirements.txt
```

## Download a video for study

Download a video you own or are authorized to download. Respect copyright, platform terms, and access restrictions.

```bash
npm run download -- "https://www.youtube.com/watch?v=VIDEO_ID"
```

Files are saved in `downloads/`. yt-dlp also saves an info JSON and description alongside the media, which can help inspect title, uploader, duration, tags, dimensions, and other available metadata.

Download available subtitles:

```bash
npm run download -- "VIDEO_URL" --subtitles --auto-subs --sub-langs "en.*,si.*,ta.*"
```

If the source provides captions, they are saved beside the video. If not, use faster-whisper below to create your own transcript from the downloaded media. Some sites may require a supported sign-in or other access configuration; this project does not bypass DRM, paywalls, or access controls.

## Generate Whisper captions

Create an SRT subtitle file (Whisper downloads the selected model the first time):

```bash
npm run captions -- input.mp4
```

Choose a model and language (language is auto-detected when omitted):

```bash
npm run captions -- input.mp4 --model small --language en
npm run captions -- input.mp4 --model medium --language si
npm run captions -- input.mp4 --model medium --language ta
```

Available model sizes include `tiny`, `base`, `small`, `medium`, and `large-v3`. Larger models are generally more accurate but need more memory and run slower. CPU users can try `--compute-type int8`; CUDA users can try `--device cuda --compute-type float16`.

Generate captions and burn them into a new MP4:

```bash
npm run captions -- input.mp4 --model small --burn output-captioned.mp4
```

The generated `.srt` remains editable. Review names, numbers, punctuation, and Sinhala/Tamil/English wording before publishing. For animated word-by-word captions, use the SRT/transcript as the timing source for a HyperFrames composition; this command creates standard timed subtitles.

## FFmpeg utilities

```bash
npm run cut -- input.mp4 00:00:05 12 output.mp4
npm run concat -- clip1.mp4 clip2.mp4 output.mp4
npm run probe -- input.mp4
```

Generated clips and renders should be kept locally; large media files are excluded by `.gitignore`.
