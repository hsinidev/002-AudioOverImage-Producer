🛠️ Required Technical Skills & Competencies: AudioOverImage Producer

Project ID: 002

Category: Media Engine & Content Generators

Target OS: Windows 10 / Windows 11 (x64)

Design Theme: Studio Emerald & Cyber Slate (#0A0E14 / #00E676 / #1DE9B6)

Core Stack: Python 3.10+, CustomTkinter, Pillow (PIL), NumPy, FFmpeg/FFprobe Subprocesses, threading, queue.Queue

🎯 Technical Competencies & Mastery Matrix

This document defines the core engineering capabilities, architectural patterns, and domain expertise required to build, maintain, and package the AudioOverImage Producer desktop engine.

1. Modern Desktop GUI & WYSIWYG Viewport Engineering

[ ] Advanced GUI Architecture (CustomTkinter):

Implementation of custom dark-mode theme token systems (Studio Emerald & Cyber Slate: #0A0E14 primary dark background, #131B26 secondary container, #00E676 neon emerald primary accent, #1DE9B6 teal secondary accent).

Responsive layout grids with dynamic row and column weight allocations for dual-pane sidebar/canvas viewports.

Encapsulation of custom compound controls (e.g., color picker triggers, opacity sliders, position drag targets, aspect ratio dropdowns).

[ ] Interactive Interactive WYSIWYG Preview Viewport:

Construction of a live Tkinter.Canvas preview engine supporting target aspect ratio bounding box constraints ($16:9$, $9:16$, $1:1$, $21:9$).

Implementation of real-time coordinate translation mapping user canvas drag events ($X_{\text{canvas}}, Y_{\text{canvas}}$) into normalized export coordinates ($X_{\text{export}}, Y_{\text{export}}$) for FFmpeg overlay positioning.

2. High-Performance Image Processing & Canvas Compositing (Pillow)

[ ] Image Resampling & Aspect Ratio Fitting:

Execution of high-quality Lanczos resampling routines (Image.Resampling.LANCZOS) for zero-aliasing image scaling.

Engineering four distinct background scaling algorithms:

Cover (Crop to Fit): Math-based cropping and scaling to completely fill target display bounds.

Contain (Pillarbox/Letterbox): Aspect-preserved scaling with customizable solid color border padding (#0A0E14 default).

Stretch: Direct dimension fitting to export target resolutions.

Dual-Layer Blur Padding: Multi-stage compositing rendering a heavily blurred ($Radius = 30\text{px}$) background layer underneath an aspect-preserved original foreground image.

[ ] Alpha Channel Compositing:

RGBA layer blending for dynamic overlay bounding boxes and real-time canvas preview updating.

3. Mathematical Audio Analysis & Spectrum Processing (NumPy)

[ ] Audio Data Vectorization:

Decoding uncompressed or compressed audio streams into normalized NumPy floating-point arrays ($\left[-1.0, 1.0\right]$).

[ ] RMS Amplitude & FFT Frequency Binning:

Vectorized Root-Mean-Square (RMS) calculations for dynamic amplitude waveform rendering.

Application of Fast Fourier Transform (numpy.fft.rfft) algorithms with logarithmic frequency binning to generate smooth frequency histogram data matrices for visualizers.

4. Media Transcoding Core & FFmpeg Filtergraph Pipeline

[ ] FFprobe Metadata Extraction:

Non-blocking JSON metadata probing (ffprobe -v quiet -print_format json -show_format -show_streams).

Extraction of exact audio stream duration down to fractional milliseconds, sample rate, bitrate, and channel configurations.

[ ] Zero-Waste Static Frame Looping:

Formulating single-pass video encoding commands leveraging -loop 1 combined with -tune stillimage and -shortest flags to eliminate repetitive re-encoding CPU overhead.

[ ] Complex Overlay Filtergraph Formulation:

Dynamic assembly of FFmpeg -filter_complex chains:

showwaves: Dynamic amplitude line or solid bar visualizer overlays.

showfreqs: Logarithmic frequency histogram bars with visual gradient transitions (#00E676 to #1DE9B6).

Exact coordinate overlay mapping (overlay=x=X_pixel:y=Y_pixel).

[ ] Hardware Acceleration Auto-Probing:

Querying FFmpeg encoder registries (ffmpeg -encoders) to auto-select optimal GPU acceleration (h264_nvenc $\rightarrow$ h264_qsv $\rightarrow$ h264_amf $\rightarrow$ libx264).

5. Concurrency, Telemetry Parsing & Non-Blocking Architecture

[ ] Asynchronous Task Architecture:

Complete decoupling of heavy I/O, image processing, and FFmpeg subprocess execution from the main GUI thread using threading.Thread.

Thread-safe message passing via queue.Queue operating at a 25 Hz polling frequency (root.after(40, self.poll_event_queue)).

[ ] Real-Time Stderr Telemetry Stream Parsing:

Constructing regex matchers to continuously parse FFmpeg stderr telemetry lines:

Frame count extraction (frame=\s*(\d+))

Timecode extraction (time=(\d{2}):(\d{2}):(\d{2})\.(\d{2}))

Encoding speed factor (speed=\s*([0-9.]+)x)

Real-time calculation of percentage completion:

$$
\text{Progress \%} = \left( \frac{\text{Current Processed Seconds}}{\text{Total Audio Seconds}} \right) \times 100
$$

Dynamic calculation of Estimated Time Remaining (ETA) based on active rendering speed.

6. Systems Programming, OS Resilience & Build Engineering

[ ] 4-Tier External Binary Auto-Resolution:

Implementation of dynamic path discovery for ffmpeg.exe and ffprobe.exe:

PyInstaller frozen runtime root (sys._MEIPASS).

Working script execution directory.

Application local ./bin/ subfolder.

System environment PATH (shutil.which).

[ ] Process Group Safety & Cancellation Management:

Launching subprocesses inside an isolated process group (creationflags=subprocess.CREATE_NEW_PROCESS_GROUP).

Executing clean job cancellations using Windows process tree termination (taskkill /F /T /PID <pid></pid>) to prevent background process leaks.

Automatic cleanup of partial .mp4 video files or intermediate pre-rendered .png background layers upon cancellation or error.

[ ] Standalone Production Packaging (PyInstaller):

Authoring robust PyInstaller specifications (AudioOverImageProducer.spec) embedding custom assets, static binaries, and dynamic module hooks for customtkinter, PIL, and numpy.
