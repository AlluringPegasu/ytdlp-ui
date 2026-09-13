# Third-Party Licenses

This project uses and/or bundles the following third-party software. This project's own source code is licensed separately under the MIT License (see [LICENSE](LICENSE)) — the notices below apply only to the components listed.

---

## yt-dlp

- **Project:** https://github.com/yt-dlp/yt-dlp
- **License:** Unlicense (public domain equivalent)
- Used as a Python library dependency (`pip install yt-dlp`), not modified or redistributed as a binary by this project.

---

## FFmpeg / FFprobe

- **Project:** https://ffmpeg.org / https://github.com/FFmpeg/FFmpeg
- **Build used:** Static Windows build from gyan.dev (https://www.gyan.dev/ffmpeg/builds/)
- **License:** GPL v3.0 (this specific static build is licensed GPLv3; FFmpeg itself is LGPL v2.1+ by default, but becomes GPL when built with certain optional components enabled, as this build is)

Because this build is GPL-licensed and its binaries (`ffmpeg.exe`, `ffprobe.exe`) are distributed alongside this project's packaged releases:

- A full copy of the GPLv3 license is included in this repository as [`GPLv3-LICENSE.txt`](GPLv3-LICENSE.txt) — this is the same license file that ships inside the gyan.dev build download; copy it in as-is.
- FFmpeg's corresponding source code can be obtained from the official repository: https://github.com/FFmpeg/FFmpeg
- The exact build/version used can be found by running `ffmpeg -version` on the bundled binary, or by checking the version noted on the [gyan.dev builds page](https://www.gyan.dev/ffmpeg/builds/) at the time of download.
- No modifications were made to the FFmpeg/FFprobe binaries themselves — they are redistributed unmodified.

**Note:** If you'd prefer to avoid GPL source-disclosure obligations entirely, consider swapping in an LGPL-licensed build instead (e.g. the `lgpl` variants from https://github.com/BtbN/FFmpeg-Builds/releases), which cover the merge/extract-audio functionality this app uses without requiring GPL compliance steps.

---

## CustomTkinter

- **Project:** https://github.com/TomSchimansky/CustomTkinter
- **License:** MIT License
- Used as a Python library dependency (`pip install customtkinter`), not modified or redistributed.
