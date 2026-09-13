# ytdlp-ui

A simple desktop GUI for [yt-dlp](https://github.com/yt-dlp/yt-dlp), built with Python and CustomTkinter. Paste a link, pick your format and quality, choose a folder, and download — no command line needed.

![screenshot](screenshot.png)

## Features

- Download video (with audio) or audio-only
- Choose resolution (up to 4K) and output format (MP4, MKV, WebM for video; MP3, M4A, WAV, FLAC, Opus for audio)
- Trim a section of a video/audio by start and end time before downloading
- Pick your save folder
- Live progress bar with speed and ETA
- Packaged as a standalone Windows `.exe` — no Python installation required for end users

## Download

Grab the latest standalone `.exe` from the [Releases](../../releases) page. No installation needed — just download and run.

> **Note:** Windows SmartScreen may show a warning on first run since the app isn't code-signed. Click "More info" → "Run anyway" to proceed.

## Running from source

If you'd rather run it from source instead of the packaged exe:

```bash
git clone https://github.com/yourusername/ytdlp-ui.git
cd ytdlp-ui
pip install -r requirements.txt
python main.py
```

You'll also need `ffmpeg` and `ffprobe` available — either installed system-wide and on your PATH, or placed in the project folder next to `main.py`.

## Building your own exe

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --add-binary "ffmpeg.exe;." --add-binary "ffprobe.exe;." --name "yt-dlp UI" main.py
```

The output exe will be in the `dist/` folder.

## Third-party components

This project bundles and depends on third-party software with their own licenses. See [THIRD_PARTY_LICENSES.md](THIRD_PARTY_LICENSES.md) for details.

## Disclaimer

This tool is a GUI wrapper around yt-dlp and does not host, distribute, or provide access to any copyrighted content itself. Downloading content you don't have the rights to may violate the terms of service of the platform you're downloading from, and/or copyright law in your jurisdiction. Use responsibly and at your own discretion.

## License

This project's own code is licensed under the MIT License — see [LICENSE](LICENSE).
