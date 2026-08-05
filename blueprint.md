🏗️ Technical Architecture Blueprint: AudioOverImage Producer

Category: Media Engine & Content Generators

Application ID: 002

Target OS: Windows 10 / Windows 11 (x64)

Design Theme: Studio Emerald & Cyber Slate (#0A0E14 / #00E676 / #1DE9B6)

Primary Stack: Python 3.10+, CustomTkinter, Pillow (PIL), NumPy, FFmpeg/FFprobe Subprocesses, threading, queue.Queue

📐 1. System Architecture & WYSIWYG Preview Pipeline

The application employs an Event-Driven Reactive Model-View-Controller (MVC) architecture. A dedicated 60 FPS CustomTkinter main thread handles interactive UI controls and a dynamic WYSIWYG canvas preview viewport. Heavy media processes—including FFprobe JSON probing, Pillow image scaling/blur pre-compositing, NumPy spectrum binning, and FFmpeg transcoding—are executed on background worker threads. Inter-thread communication is managed using typed event payloads passed through a thread-safe queue.Queue polled at 25 Hz (40ms interval).

+---------------------------------------------------------------------------------------+
|                               GUI LAYER (Main Thread - 60 FPS)                        |
|  - Theme: Studio Emerald & Cyber Slate (#0A0E14 Primary / #00E676 Emerald Accent)    |
|  - Interactive WYSIWYG Canvas Viewport (Dynamic Aspect Ratio Box & Drag Overlay)      |
|  - Queue Event Loop Routine (root.after(40, poll_event_queue))                        |
+---------------------------------------------------------------------------------------+
                                           ^
                                           |  Thread-Safe Event Payloads (queue.Queue)
                                           |  - STATUS: Idle | Probing | Rendering | Aborted
                                           |  - METRICS: Progress %, Time Code, Speed, ETA
                                           |  - CANVAS: Scaled Composite Preview Frames
                                           v
+---------------------------------------------------------------------------------------+
|                             THREAD-SAFE MESSAGE QUEUE BUFFER                          |
|  - Decouples continuous stderr telemetry and image processing from UI thread          |
+---------------------------------------------------------------------------------------+
                                           ^
                                           |  Non-Blocking Background Dispatch
                                           v
+---------------------------------------------------------------------------------------+
|                            BACKGROUND ENGINE WORKERS                                  |
|  - FFprobe Metadata Prober (Fractional second duration & audio stream parameters)     |
|  - Pillow Composite Scaler (Cover, Contain, Stretch, Dual-Layer Blur Padding)         |
|  - NumPy Spectrum Analyzer (RMS vector binning & frequency matrix normalization)       |
|  - Transcode Thread Manager (threading.Thread)                                        |
+---------------------------------------------------------------------------------------+
                                           |
                                           |  subprocess.Popen (CREATE_NEW_PROCESS_GROUP)
                                           v
+---------------------------------------------------------------------------------------+
|                           EMBEDDED FFMPEG TRANSCODING ENGINE                          |
|  - Zero-Waste Static Image Stream Loop (-loop 1 -tune stillimage)                     |
|  - Dynamic Visualizer Filtergraphs (showwaves / showfreqs overlay composition)       |
|  - Hardware Encoder Auto-Fallback (NVENC -> QSV -> AMF -> libx264)                     |
|  - Process Group Task-Kill Handle for Clean Cancellation                              |
+---------------------------------------------------------------------------------------+

📁 2. Project Directory Layout & Architectural File Roles

002-AudioOverImage-Producer/
├── prompt.json                   # AI Agent Core Engineering Specification
├── roadmap.md                    # Production Execution Roadmap
├── blueprint.md                  # Technical Architecture Blueprint (This Document)
├── skills.md                     # Required Competencies & Engineering Checklist
├── requirements.txt              # Standardized Python Dependency Manifest
├── AudioOverImageProducer.spec   # Production PyInstaller Build Specification
├── main.py                       # Application Entry Point & Exception Host
├── gui/
│   ├── __init__.py
│   ├── app.py                    # Root Window Layout, Theme Engine & Queue Loop
│   ├── canvas_preview.py         # Dynamic Interactive WYSIWYG Viewport Component
│   ├── components/
│   │   ├── __init__.py
│   │   ├── sidebar_controls.py   # Audio/Image Pickers, Aspect Ratio & Scaling Options
│   │   ├── waveform_settings.py  # Visualizer Style, Color Gradient & Position Controls
│   │   ├── render_panel.py       # Export Bar, Progress Bar & ETA Counter
│   │   └── terminal_console.py   # Collapsible Thread-Safe Stderr Log Terminal
│   └── styles/
│       ├── __init__.py
│       └── theme_tokens.py       # Studio Emerald Visual Token Definitions
├── engine/
│   ├── __init__.py
│   ├── binary_resolver.py        # 4-Tier Executable Path Resolution Helper
│   ├── hw_accel.py               # GPU Encoder Prober (NVENC, QSV, AMF, CPU)
│   ├── audio_analyzer.py         # FFprobe JSON Extractor & NumPy RMS Waveform Processor
│   ├── image_processor.py        # Pillow Scaling, Aspect Fitting & Gaussian Blur Engine
│   ├── ffmpeg_filtergraph.py     # Complex Filtergraph Builder (showwaves/showfreqs)
│   └── transcode_worker.py       # Non-Blocking Transcode Manager & Stderr Telemetry
└── utils/
    ├── __init__.py
    ├── logger.py                 # Thread-Safe System Diagnostic Logging
    └── helpers.py                # Coordinate Scaler, Time Formatter & Path Sanitizer

🛠️ 3. Technology Stack & Design System Matrix

3.1 Stack Breakdown

Technology Layer

Component / Package

Architectural Purpose & Responsibility

GUI Framework

CustomTkinter (>= 5.2.0)

Modern high-DPI desktop controls, dark mode panels, interactive sliders.

Image Processing

Pillow (PIL) (>= 10.0.0)

High-quality Lanczos image resampling, aspect padding, and dual-layer blur.

Math & Audio Processing

NumPy (>= 1.24.0)

Vectorized RMS amplitude calculation, FFT frequency binning, matrix normalization.

Media Transcoding Engine

FFmpeg & FFprobe (Static Build 6.0+)

Audio probing, zero-waste image looping, stream overlay filtergraphs, video encoding.

Concurrency Core

threading.Thread & queue.Queue

Thread isolation for background processing, preventing UI lockups.

Subprocess Execution

subprocess.Popen

Silent execution using creationflags=subprocess.CREATE_NEW_PROCESS_GROUP.

Executable Packaging

PyInstaller (>= 6.0)

Single-file Windows .exe executable generation.

3.2 Visual Theme Token Definition (Studio Emerald & Cyber Slate)

# gui/styles/theme_tokens.py

COLOR_PALETTE = {
    "background_primary": "#0A0E14",    # Main Window & Viewport Canvas Background
    "background_secondary": "#131B26",  # Sidebar Control Panels & Section Headers
    "surface_card": "#1A2332",          # Interactive Cards & Input Groups
    "accent_primary": "#00E676",        # Primary Action Buttons & Progress Meters (Neon Emerald)
    "accent_secondary": "#1DE9B6",      # Secondary Accent, Mode Badges & Waveform Lines (Teal)
    "accent_hover": "#00C853",          # Hover Highlight State for Primary Controls
    "text_primary": "#E0E6ED",          # High-Contrast Heading & Text Display
    "text_secondary": "#90A4AE",        # Subheadings, Captions & Inactive Labels
    "danger_red": "#FF5252",            # Job Abort Buttons & Error Warnings
    "warning_amber": "#FFD700",         # Non-Fatal Warnings & Hardware Fallback Alerts
    "border_color": "#263238"           # Panel Divider Lines & Card Outlines
}

🖼️ 4. WYSIWYG Interactive Canvas & Aspect Ratio Engine

4.1 Aspect Ratio Viewport Specifications

The canvas component automatically calculates the maximum fitting display bounding box within the UI viewport while maintaining target export aspect ratios:

Target Template

Export Resolution ($W \times H$)

Aspect Ratio

Target Platform

YouTube Standard

$1920 \times 1080$ (4K: $3840 \times 2160$)

$16:9$

YouTube Main, Vimeo, Web Portals

Vertical Shorts / Reels

$1080 \times 1920$

$9:16$

YouTube Shorts, TikTok, Instagram Reels

Instagram Square

$1080 \times 1080$

$1:1$

Instagram Post, Spotify Canvas

Cinematic Ultrawide

$2560 \times 1080$

$21:9$

Widescreen Displays, Film Teasers

4.2 Interactive Waveform Positioning Logic

Users can drag or scale the waveform visualizer box directly on the live preview canvas. The normalized bounding box coordinates $(X_{norm}, Y_{norm}, W_{norm}, H_{norm})$ are mapped dynamically to the target FFmpeg filtergraph:

$$
X_{pixel} = \text{round}(X_{norm} \times W_{export}), \quad Y_{pixel} = \text{round}(Y_{norm} \times H_{export})
$$

$$
W_{pixel} = \text{round}(W_{norm} \times W_{export}), \quad H_{pixel} = \text{round}(H_{norm} \times H_{export})
$$

4.3 Background Image Pre-Processing Modes (image_processor.py)

Cover (Crop to Fit): Scales the image to fill the canvas completely, cropping overflowing edges.

Contain (Pillarbox/Letterbox): Fits the full image inside the frame, filling empty borders with a user-selected solid color (#0A0E14 default).

Stretch: Stretches the image dimensions to match target resolution exactly.

Dual-Layer Blur Padding: Renders a heavily blurred ($Radius = 30px$) stretched version of the image as the background layer, placing the aspect-preserved original image in the foreground.

⚡ 5. FFmpeg Zero-Waste Transcoding & Filtergraph Pipeline

5.1 Zero-Waste Static Frame Looping

To eliminate CPU overhead during video encoding, static background images are looped as a single static frame pointer using -loop 1 combined with -tune stillimage:

ffmpeg -y -loop 1 -framerate 30 -i "temp_background.png" 
    -i "input_audio.mp3"
    -c:v h264_nvenc -preset p4 -tune hq -crf 18
    -c:a aac -b:a 192k -pix_fmt yuv420p -shortest "output_video.mp4"

5.2 Dynamic Visualizer Overlay Filtergraphs

When dynamic waveforms or frequency visualizers are enabled, ffmpeg_filtergraph.py constructs a complex multi-stage filtergraph:

Line Waveform Filtergraph (showwaves)

[0:v]scale=1920:1080[bg]; 
[1:a]showwaves=s=1200x200:mode=line:colors=#00E676:scale=lin[wave]; 
[bg][wave]overlay=x=360:y=780:format=auto[outv]

Audio Frequency Histogram Filtergraph (showfreqs)

[0:v]scale=1080:1920[bg]; 
[1:a]showfreqs=s=900x300:mode=bar:ascale=log:fscale=log:colors=#00E676|#1DE9B6[freq]; 
[bg][freq]overlay=x=90:y=1200:format=auto[outv]

5.3 Hardware Acceleration Fallback Hierarchy

The system auto-queries available hardware encoders on boot and dynamically selects the optimal pipeline:

    +-----------------------------------+
                  | 1. Probe h264_nvenc (NVIDIA GPU) |
                  +-----------------------------------+
                                    | Fail
                                    v
                  +-----------------------------------+
                  | 2. Probe h264_qsv (Intel QuickSync)|
                  +-----------------------------------+
                                    | Fail
                                    v
                  +-----------------------------------+
                  | 3. Probe h264_amf (AMD GPU)       |
                  +-----------------------------------+
                                    | Fail
                                    v
                  +-----------------------------------+
                  | 4. Fallback to CPU (libx264)      |
                  +-----------------------------------+

🔄 6. Concurrency Protocol & Telemetry Telemetry Schema

6.1 Telemetry Payload Structure

Structured dictionaries are pushed to queue.Queue from background threads and processed during the main thread polling tick:

# Payload Example: Rendering Telemetry Update

{
    "event": "TELEMETRY",
    "percent": 64.2,                 # Normalized render progress (0.0 - 100.0%)
    "current_frame": 1926,           # Processed video frames
    "current_time_sec": 64.2,        # Processed audio duration in seconds
    "total_duration_sec": 100.0,     # Total audio length in seconds
    "fps": 142.5,                    # Current rendering frames per second
    "speed": "4.75x",                # Encoding speed factor
    "eta_seconds": 7.5,              # Calculated estimated time remaining
    "log_line": "frame= 1926 fps=142.5 q=21.0 size= 18432kB time=00:01:04.20 bitr..."
}

6.2 Main Thread Queue Polling Implementation

# gui/app.py

def poll_event_queue(self):
    try:
        while True:
            payload = self.event_queue.get_nowait()
            event_type = payload.get("event")

    if event_type == "TELEMETRY":
                self.render_panel.update_progress(payload)
                self.terminal_console.append_log(payload["log_line"])
            elif event_type == "CANVAS_UPDATE":
                self.canvas_preview.update_frame(payload["image"])
            elif event_type == "COMPLETE":
                self.render_panel.on_render_complete(payload["output_path"])
            elif event_type == "ERROR":
                self.render_panel.on_render_error(payload["error_msg"])

    self.event_queue.task_done()
    except queue.Empty:
        pass
    finally:
        # Schedule next poll in 40ms (25 Hz refresh rate)
        self.root.after(40, self.poll_event_queue)

🛡️ 7. Process Lifecycle & Job Cancellation Safety

To prevent orphan background ffmpeg.exe processes or locked temporary files when a user cancels an in-progress export:

Subprocess Group Isolation:
Subprocesses are launched with flags: creationflags=subprocess.CREATE_NEW_PROCESS_GROUP.

Targeted Process Termination:
When job cancellation is triggered, the worker sends a process group kill command using Windows taskkill:

import subprocess
subprocess.run(["taskkill", "/F", "/T", "/PID", str(process.pid)], capture_output=True)

Artifact Cleanup Routine:
The engine automatically sweeps and removes any partial output .mp4 or pre-rendered temporary .png files generated during the aborted session.

📦 8. Production Packaging Blueprint (AudioOverImageProducer.spec)

# AudioOverImageProducer.spec

import sys
import os
from PyInstaller.utils.hooks import collect_all

block_cipher = None

datas = [
    ('assets', 'assets'),
    ('bin/ffmpeg.exe', '.'),
    ('bin/ffprobe.exe', '.')
]
binaries = []
hiddenimports = [
    'customtkinter',
    'PIL',
    'PIL.Image',
    'PIL.ImageFilter',
    'PIL.ImageDraw',
    'numpy',
    'queue',
    'json',
    're'
]

# Collect dynamic dependencies for CustomTkinter and Pillow

for pkg in ['customtkinter', 'PIL', 'numpy']:
    tmp = collect_all(pkg)
    datas += tmp[0]
    binaries += tmp[1]
    hiddenimports += tmp[2]

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='AudioOverImageProducer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon='assets/icon.ico'
)
