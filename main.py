import sys
import os
import re
import time
import threading
from tkinter import filedialog
import customtkinter as ctk
import yt_dlp
import yt_dlp.utils

# Detect bundle directory (when frozen with PyInstaller)
BUNDLE_DIR = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
if BUNDLE_DIR not in os.environ.get("PATH", ""):
    os.environ["PATH"] = BUNDLE_DIR + os.pathsep + os.environ.get("PATH", "")

FFMPEG_PATH = os.path.join(BUNDLE_DIR, "ffmpeg.exe")

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("yt-dlp UI")
app.geometry("540x620")

# Keep track of the chosen save folder
save_folder = os.path.expanduser("~/Downloads")

# Preset options
VIDEO_RESOLUTIONS = ["Best", "2160p (4K)", "1440p (2K)", "1080p", "720p", "480p", "360p"]
VIDEO_FORMATS = ["mp4", "mkv", "webm"]

AUDIO_QUALITIES = ["320 kbps (Best)", "256 kbps", "192 kbps", "128 kbps"]
AUDIO_FORMATS = ["mp3", "m4a", "wav", "flac", "opus"]

# --- URL input ---
url_label = ctk.CTkLabel(app, text="Video URL:")
url_label.pack(pady=(15, 3))

url_entry = ctk.CTkEntry(app, width=440, placeholder_text="Paste a YouTube link here")
url_entry.pack(pady=5)

# --- Media Mode Selector (Video+Audio vs Audio Only) ---
mode_label = ctk.CTkLabel(app, text="Download Mode:")
mode_label.pack(pady=(8, 3))

mode_var = ctk.StringVar(value="Video + Audio")
mode_selector = ctk.CTkSegmentedButton(
    app,
    values=["Video + Audio", "Audio Only"],
    variable=mode_var,
    command=lambda val: on_mode_change(val)
)
mode_selector.pack(pady=5)

# --- Options Frame (Resolution/Quality and Format side-by-side) ---
options_frame = ctk.CTkFrame(app, fg_color="transparent")
options_frame.pack(pady=8)

# Left: Quality / Resolution column
quality_col = ctk.CTkFrame(options_frame, fg_color="transparent")
quality_col.pack(side="left", padx=15)

quality_label = ctk.CTkLabel(quality_col, text="Resolution:")
quality_label.pack(pady=(0, 3))

quality_var = ctk.StringVar(value=VIDEO_RESOLUTIONS[0])
quality_menu = ctk.CTkOptionMenu(quality_col, values=VIDEO_RESOLUTIONS, variable=quality_var, width=170)
quality_menu.pack()

# Right: Format column
format_col = ctk.CTkFrame(options_frame, fg_color="transparent")
format_col.pack(side="left", padx=15)

format_label = ctk.CTkLabel(format_col, text="Format:")
format_label.pack(pady=(0, 3))

format_var = ctk.StringVar(value=VIDEO_FORMATS[0])
format_menu = ctk.CTkOptionMenu(format_col, values=VIDEO_FORMATS, variable=format_var, width=170)
format_menu.pack()

def on_mode_change(mode):
    """Dynamically update resolution/quality and format options based on mode."""
    if mode == "Video + Audio":
        quality_label.configure(text="Resolution:")
        quality_menu.configure(values=VIDEO_RESOLUTIONS)
        quality_var.set("Best")

        format_label.configure(text="Video Format:")
        format_menu.configure(values=VIDEO_FORMATS)
        format_var.set("mp4")
    else:
        quality_label.configure(text="Audio Quality:")
        quality_menu.configure(values=AUDIO_QUALITIES)
        quality_var.set("320 kbps (Best)")

        format_label.configure(text="Audio Format:")
        format_menu.configure(values=AUDIO_FORMATS)
        format_var.set("mp3")

# --- Helper: Parse time string into seconds ---
def parse_time_str(time_str):
    """Parses seconds (e.g. '45'), MM:SS (e.g. '1:30'), or HH:MM:SS into float seconds."""
    time_str = time_str.strip()
    if not time_str:
        return None
    parts = time_str.split(':')
    try:
        if len(parts) == 1:
            val = float(parts[0])
            return val if val >= 0 else None
        elif len(parts) == 2:
            m = int(parts[0])
            s = float(parts[1])
            if m < 0 or s < 0 or s >= 60:
                return None
            return m * 60 + s
        elif len(parts) == 3:
            h = int(parts[0])
            m = int(parts[1])
            s = float(parts[2])
            if h < 0 or m < 0 or m >= 60 or s < 0 or s >= 60:
                return None
            return h * 3600 + m * 60 + s
    except (ValueError, IndexError):
        return None
    return None

# --- Trim Section (Right under format and resolution selector) ---
trim_frame = ctk.CTkFrame(app, fg_color="transparent")
trim_frame.pack(pady=(4, 8))

trim_var = ctk.BooleanVar(value=False)

def toggle_trim():
    if trim_var.get():
        trim_inputs_frame.pack(pady=(6, 0))
    else:
        trim_inputs_frame.pack_forget()

trim_checkbox = ctk.CTkCheckBox(
    trim_frame,
    text="Trim Section (Specify time range)",
    variable=trim_var,
    command=toggle_trim,
    font=("", 12),
)
trim_checkbox.pack()

trim_inputs_frame = ctk.CTkFrame(trim_frame, fg_color="transparent")

start_col = ctk.CTkFrame(trim_inputs_frame, fg_color="transparent")
start_col.pack(side="left", padx=10)
start_label = ctk.CTkLabel(start_col, text="From (sec or mm:ss):", font=("", 11))
start_label.pack(pady=(0, 2))
start_entry = ctk.CTkEntry(start_col, width=170, placeholder_text="e.g. 00:30 or 30")
start_entry.pack()

end_col = ctk.CTkFrame(trim_inputs_frame, fg_color="transparent")
end_col.pack(side="left", padx=10)
end_label = ctk.CTkLabel(end_col, text="To (sec or mm:ss):", font=("", 11))
end_label.pack(pady=(0, 2))
end_entry = ctk.CTkEntry(end_col, width=170, placeholder_text="e.g. 01:45 or 105")
end_entry.pack()

# --- Folder picker ---
folder_label = ctk.CTkLabel(app, text=f"Save to: {save_folder}", wraplength=440)
folder_label.pack(pady=(8, 3))

def choose_folder():
    global save_folder
    chosen = filedialog.askdirectory()
    if chosen:
        save_folder = chosen
        folder_label.configure(text=f"Save to: {save_folder}")

folder_button = ctk.CTkButton(app, text="Choose Folder", command=choose_folder, width=140)
folder_button.pack(pady=5)

# --- Download Button ---
def start_download_thread():
    thread = threading.Thread(target=run_download, daemon=True)
    thread.start()

download_button = ctk.CTkButton(app, text="Download", command=start_download_thread, width=160, height=36)
download_button.pack(pady=10)

# --- Progress bar + status (Always visible with stable layout) ---
progress_bar = ctk.CTkProgressBar(app, width=440, height=12, corner_radius=6)
progress_bar.pack(pady=(10, 4))
progress_bar.set(0)

status_label = ctk.CTkLabel(app, text="", font=("", 12))
status_label.pack(pady=2)

# --- Download logic ---
last_ui_update_time = 0.0

def clean_ansi(text):
    if not text:
        return ""
    return re.sub(r'\x1b\[[0-9;]*[a-zA-Z]', '', str(text)).strip()

def progress_hook(d):
    global last_ui_update_time
    if d['status'] == 'downloading':
        total = d.get('total_bytes') or d.get('total_bytes_estimate') or 0
        downloaded = d.get('downloaded_bytes', 0)

        if total > 0:
            stream_percent = downloaded / total
        else:
            raw_percent = clean_ansi(d.get('_percent_str', ''))
            match = re.search(r'([\d.]+)%', raw_percent)
            stream_percent = (float(match.group(1)) / 100) if match else 0.0

        stream_percent = max(0.0, min(1.0, stream_percent))

        # Throttle GUI redraws to ~16 FPS (every 60ms) except when stream hits 100%
        now = time.time()
        if stream_percent < 1.0 and (now - last_ui_update_time < 0.06):
            return
        last_ui_update_time = now

        speed = clean_ansi(d.get('_speed_str', ''))
        eta = clean_ansi(d.get('_eta_str', ''))

        speed_eta = []
        if speed:
            speed_eta.append(f"at {speed}")
        if eta:
            speed_eta.append(f"(ETA {eta})")
        extra_info = (" " + " ".join(speed_eta)) if speed_eta else ""

        # Identify stream: Video stream vs Audio stream
        info = d.get('info_dict', {})
        vcodec = info.get('vcodec')
        acodec = info.get('acodec')

        selected_mode = mode_var.get()
        if selected_mode == "Video + Audio":
            if vcodec and vcodec != 'none':
                # Video stream (Step 1/2: 0% -> 85%)
                overall_progress = stream_percent * 0.85
                msg = f"Downloading Video (1/2): {stream_percent * 100:.1f}%{extra_info}"
            elif acodec and acodec != 'none' and (not vcodec or vcodec == 'none'):
                # Audio stream (Step 2/2: 85% -> 95%)
                overall_progress = 0.85 + (stream_percent * 0.10)
                msg = f"Downloading Audio (2/2): {stream_percent * 100:.1f}%{extra_info}"
            else:
                overall_progress = stream_percent * 0.90
                msg = f"Downloading: {stream_percent * 100:.1f}%{extra_info}"
        else:
            # Audio Only (0% -> 90%)
            overall_progress = stream_percent * 0.90
            msg = f"Downloading Audio: {stream_percent * 100:.1f}%{extra_info}"

        app.after(0, lambda p=overall_progress: progress_bar.set(p))
        app.after(0, lambda m=msg: status_label.configure(text=m))

    elif d['status'] == 'finished':
        pass

def postprocessor_hook(d):
    status = d.get('status')
    postprocessor = d.get('postprocessor', '')
    if status == 'started':
        app.after(0, lambda: progress_bar.set(0.95))
        if 'Merger' in postprocessor:
            app.after(0, lambda: status_label.configure(text="Merging video and audio streams..."))
        elif 'ExtractAudio' in postprocessor:
            app.after(0, lambda: status_label.configure(text="Converting audio codec..."))
        else:
            app.after(0, lambda: status_label.configure(text="Processing media with ffmpeg..."))
    elif status == 'finished':
        app.after(0, lambda: progress_bar.set(0.98))
        app.after(0, lambda: status_label.configure(text="Finalizing file..."))

def run_download():
    url = url_entry.get().strip()
    if not url:
        status_label.configure(text="Please paste a URL first.")
        return

    # Check trim settings
    download_ranges = None
    if trim_var.get():
        start_val = start_entry.get().strip()
        end_val = end_entry.get().strip()

        if not start_val and not end_val:
            status_label.configure(text="Please specify From or To time for trimming.")
            return

        start_sec = parse_time_str(start_val) if start_val else 0.0
        end_sec = parse_time_str(end_val) if end_val else float('inf')

        if start_sec is None or end_sec is None:
            status_label.configure(text="Invalid time format. Use seconds (e.g. 30) or mm:ss (e.g. 1:30)")
            return

        if start_sec >= end_sec:
            status_label.configure(text="End time must be greater than start time.")
            return

        download_ranges = yt_dlp.utils.download_range_func([], [[start_sec, end_sec]])

    # UI Setup before download triggers
    download_button.configure(state="disabled", text="Downloading...")
    if download_ranges:
        # Ffmpeg range download handles stream directly: pulse animation indicates active trimming
        app.after(0, lambda: progress_bar.configure(mode="indeterminate"))
        app.after(0, lambda: progress_bar.start())
        app.after(0, lambda: status_label.configure(text="Trimming & downloading clip with ffmpeg..."))
    else:
        app.after(0, lambda: progress_bar.configure(mode="determinate"))
        app.after(0, lambda: progress_bar.set(0))
        app.after(0, lambda: status_label.configure(text="Starting download..."))

    selected_mode = mode_var.get()
    chosen_format = format_var.get().lower()
    chosen_quality = quality_var.get()

    if selected_mode == "Audio Only":
        bitrate_match = re.search(r'\d+', chosen_quality)
        bitrate = bitrate_match.group(0) if bitrate_match else "192"

        options = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(save_folder, '%(title)s.%(ext)s'),
            'nocolor': True,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': chosen_format,
                'preferredquality': bitrate,
            }],
            'progress_hooks': [progress_hook],
            'postprocessor_hooks': [postprocessor_hook],
        }
    else:
        res_match = re.search(r'(\d+)p', chosen_quality)
        if res_match:
            max_height = res_match.group(1)
            video_format = f"bestvideo[height<={max_height}]+bestaudio/best[height<={max_height}]/best"
        else:
            video_format = "bestvideo+bestaudio/best"

        options = {
            'format': video_format,
            'outtmpl': os.path.join(save_folder, '%(title)s.%(ext)s'),
            'merge_output_format': chosen_format,
            'nocolor': True,
            'progress_hooks': [progress_hook],
            'postprocessor_hooks': [postprocessor_hook],
        }

    if download_ranges:
        options['download_ranges'] = download_ranges

    if os.path.exists(FFMPEG_PATH):
        options['ffmpeg_location'] = FFMPEG_PATH

    try:
        with yt_dlp.YoutubeDL(options) as ydl:
            ydl.download([url])
        app.after(0, lambda: progress_bar.stop())
        app.after(0, lambda: progress_bar.configure(mode="determinate"))
        app.after(0, lambda: progress_bar.set(1.0))
        app.after(0, lambda: status_label.configure(text="Download Complete!"))
    except Exception as e:
        app.after(0, lambda: progress_bar.stop())
        app.after(0, lambda: progress_bar.configure(mode="determinate"))
        app.after(0, lambda: progress_bar.set(0))
        app.after(0, lambda: status_label.configure(text=f"Error: {e}"))
    finally:
        app.after(0, lambda: download_button.configure(state="normal", text="Download"))

app.mainloop()
