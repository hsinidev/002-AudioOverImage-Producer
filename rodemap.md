🚀 Production Implementation Roadmap: AudioOverImage Producer

Project ID: 002

Category: Media Engine & Content Generators

Target OS: Windows 10 / Windows 11 (x64)

Design Theme: Studio Emerald & Cyber Slate (#0A0E14 / #00E676 / #1DE9B6)

Core Stack: Python 3.10+, CustomTkinter, Pillow (PIL), NumPy, FFmpeg/FFprobe Subprocesses, threading, queue.Queue

📌 Project Overview

AudioOverImage Producer is an ultra-performant content generation desktop engine built for audio creators, podcasters, and musicians. It merges audio streams with static or processed background images and dynamic real-time audio waveform/spectrum overlays, outputting YouTube-, Reels-, and TikTok-ready MP4 video files. Utilizing zero-waste static frame looping (-loop 1), Pillow compositing, NumPy RMS frequency spectrum binning, and a interactive WYSIWYG preview canvas, it ensures sub-150MB memory utilization and zero UI responsiveness locks.

🗓️ Implementation Phases & Task Breakdown

Phase 1: Environment Setup & Project Foundation

[ ] Virtual Environment & Dependency Manifest

Initialize isolated Python 3.10+ 64-bit environment (python -m venv venv).

Formulate requirements.txt with strict production version constraints:

customtkinter>=5.2.0 (High-DPI UI framework)

Pillow>=10.0.0 (Lanczos image resampling and Gaussian blur engine)

numpy>=1.24.0 (RMS audio vector analysis & FFT spectrum binning)

pyinstaller>=6.0.0 (Single-file executable packager)

[ ] Directory Architecture Initializer

Scaffold modular directory tree (gui/components/, gui/styles/, engine/, utils/, bin/, assets/).

Create explicit __init__.py module exports to enforce clean imports across components.

[ ] Static Binary & Asset Staging

Stage 64-bit static Windows builds of ffmpeg.exe and ffprobe.exe (v6.0+) inside ./bin/.

Establish visual identity assets (assets/icon.ico, default preview thumbnails).

Phase 2: Core Processing Engine & Filtergraph Engineering

[ ] 4-Tier Binary Auto-Resolver (engine/binary_resolver.py)

Implement dynamic discovery path hierarchy: PyInstaller runtime (sys._MEIPASS) $\rightarrow$ Application working directory $\rightarrow$ Relative ./bin/ subfolder $\rightarrow$ System environment PATH (shutil.which).

Implement executable version validation runner using sub-millisecond subprocess execution (ffmpeg -version).

[ ] Hardware Acceleration Prober (engine/hw_accel.py)

Query FFmpeg encoder registry (ffmpeg -hide_banner -encoders) to detect GPU availability.

Establish automatic encoder fallback hierarchy: h264_nvenc (NVIDIA) $\rightarrow$ h264_qsv (Intel) $\rightarrow$ h264_amf (AMD) $\rightarrow$ libx264 (Software CPU).

[ ] FFprobe Metadata & Audio Analyzer (engine/audio_analyzer.py)

Probe audio streams via JSON output mode (ffprobe -v quiet -print_format json -show_format -show_streams).

Extract exact duration down to fractional milliseconds, sample rate, bit rate, and channel topology.

Build NumPy vectorizer for RMS amplitude analysis and normalized frequency matrix binning for visualizers.

[ ] Pillow Background Composite Scaler (engine/image_processor.py)

Build background scaling engine supporting four distinct modes:

Cover (Crop to Fit): Scales image to fill canvas dimensions, cropping overflowing axes.

Contain (Pillarbox/Letterbox): Scales image within canvas bounds, filling borders with custom solid color.

Stretch: Fits image to target resolution explicitly.

Dual-Layer Blur Padding: Renders heavy Gaussian blur ($Radius = 30px$) background layer under an aspect-preserved original foreground image.

[ ] Dynamic Visualizer Filtergraph Builder (engine/ffmpeg_filtergraph.py)

Construct complex FFmpeg -filter_complex chains for audio visualization overlays:

showwaves: Modeled as dynamic line or solid bar overlays.

showfreqs: Logarithmic frequency histogram bars with dual-color visual gradients (#00E676 to #1DE9B6).

Support normalized positioning mapping ($X_{pixel}, Y_{pixel}, W_{pixel}, H_{pixel}$) for WYSIWYG overlay placement.

[ ] Asynchronous Transcode Engine (engine/transcode_worker.py)

Implement zero-waste static frame looping using -loop 1 combined with -tune stillimage and -shortest.

Spawn non-blocking process in isolated process group (creationflags=subprocess.CREATE_NEW_PROCESS_GROUP).

Parse continuous stderr stream with compiled regex pattern to extract frame count, timecode, encoding FPS, and speed multiplier.

Compute real-time progress percentage:

$$
\text{Progress \%} = \left( \frac{\text{Current Processed Seconds}}{\text{Total Audio Seconds}} \right) \times 100
$$

Calculate Estimated Time Remaining (ETA) based on active encoding speed multiplier.

Phase 3: Modern Desktop GUI & WYSIWYG Viewport

[ ] Theme Token System & Application Host (gui/app.py & gui/styles/theme_tokens.py)

Implement Studio Emerald & Cyber Slate dark visual theme (#0A0E14 primary background, #131B26 secondary containers, #00E676 neon emerald highlights).

Build non-blocking event loop queue consumer executing at 25 Hz (root.after(40, self.poll_event_queue)).

[ ] Interactive WYSIWYG Viewport (gui/canvas_preview.py)

Construct real-time Tkinter Canvas component with dynamic aspect-ratio bounding box fitting (16:9 YouTube, 9:16 Shorts/Reels, 1:1 Square, 21:9 Ultrawide).

Render interactive visual overlay bounding box allowing users to click and drag to position the waveform overlay directly on the canvas.

[ ] Sidebar Control Panels (gui/components/sidebar_controls.py & waveform_settings.py)

Audio & Image asset pickers with file validation badges.

Target aspect ratio selection dropdowns and background scaling mode toggles.

Visualizer style selectors (Line Waveform, Solid Bars, Frequency Histogram), custom color pickers, and opacity sliders.

[ ] Render Panel Footer (gui/components/render_panel.py)

Export destination picker with auto-generated filename suggestions based on input audio.

Visual progress bar, percentage readout, FPS monitor, and calculated ETA counter.

High-visibility Render Video action button and Abort Job danger button.

[ ] Collapsible Terminal Console (gui/components/terminal_console.py)

Build thread-safe, auto-scrolling log console capturing raw FFmpeg stderr telemetry and diagnostic messages.

Phase 4: Resilience, Process Lifecycle & Edge Cases

[ ] Targeted Process Termination Engine

Implement clean job cancellation using Windows taskkill against process group IDs (taskkill /F /T /PID <pid></pid>).

Ensure zero background ffmpeg.exe process leaks or locked temporary files upon application exit or cancellation.

[ ] Automated Temp Artifact Sweeper

Build safe cleanup routines to remove partially encoded .mp4 outputs or intermediate background .png composite frames upon cancellation or error.

[ ] Defensive File & Path Validation

Handle special characters, spaces, non-ASCII Unicode strings, and long Windows path prefixes (\\?\).

Pre-validate file permissions and available disk space prior to triggering rendering jobs.

Phase 5: Verification & Production Executable Packaging

[ ] End-to-End Functional Validation

Validate rendering performance across all aspect ratio presets (1080p, 4K, 9:16, 1:1).

Verify memory footprint stability (maintaining < 150 MB RAM usage throughout continuous HD/4K exports).

Test hardware encoder auto-detection and CPU fallback on NVIDIA, Intel, and AMD test hardware.

[ ] PyInstaller Standalone Packaging (AudioOverImageProducer.spec)

Author custom PyInstaller spec file embedding assets, binaries, and dynamic hooks for customtkinter, PIL, and numpy.

Compile single-file executable: pyinstaller --noconfirm AudioOverImageProducer.spec.

[ ] Clean-System Verification

Test standalone binary dist/AudioOverImageProducer.exe on clean Windows 10 and 11 environments without pre-installed Python runtime or FFmpeg paths.
