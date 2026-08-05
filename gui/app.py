import os
import queue
import tempfile
import customtkinter as ctk
from PIL import Image
from typing import Optional, Dict, Any, Tuple

from gui.styles.theme_tokens import COLOR_PALETTE, ASPECT_RATIO_PRESETS
from gui.canvas_preview import CanvasPreview
from gui.components.sidebar_controls import SidebarControls
from gui.components.waveform_settings import WaveformSettings
from gui.components.render_panel import RenderPanel
from gui.components.terminal_console import TerminalConsole

from engine.binary_resolver import BinaryResolver
from engine.hw_accel import HWAccelDetector
from engine.audio_analyzer import AudioAnalyzer
from engine.image_processor import ImageProcessor
from engine.ffmpeg_filtergraph import FiltergraphBuilder
from engine.transcode_worker import TranscodeWorker

from utils.logger import get_logger

logger = get_logger()

class App(ctk.CTk):
    """
    AudioOverImage Producer Main Application Window.
    Manages CustomTkinter 60 FPS UI loop, 40ms event queue polling,
    background image compositing, and non-blocking FFmpeg transcoding.
    """

    def __init__(self):
        super().__init__()

        self.title("AudioOverImage Producer - Studio Content Generator")
        self.geometry("1280x840")
        self.minsize(1024, 700)

        # Set CustomTkinter theme
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("green")
        self.configure(fg_color=COLOR_PALETTE["background_primary"])

        # Thread-Safe Event Queue
        self.event_queue = queue.Queue()

        # Engine State
        self.ffmpeg_path: Optional[str] = None
        self.ffprobe_path: Optional[str] = None
        self.best_encoder: str = "libx264"

        self.audio_metadata: Optional[Dict[str, Any]] = None
        self.current_aspect_key: str = "16:9"
        self.current_export_w: int = 1920
        self.current_export_h: int = 1080

        self.background_mode: str = "Cover"
        self.pad_color_hex: str = "#0A0E14"

        self.processed_bg_image: Optional[Image.Image] = None
        self.active_transcode_worker: Optional[TranscodeWorker] = None
        self.temp_bg_file: Optional[str] = None

        # Build UI layout
        self._build_layout()

        # Initialize Binaries & Hardware Accel Engine in background
        self._initialize_engine()

        # Start 40ms Queue Event Polling Loop
        self.after(40, self.poll_event_queue)

    def _build_layout(self):
        """Construct main window grid layout."""
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)
        self.grid_columnconfigure(0, weight=0) # Sidebar
        self.grid_columnconfigure(1, weight=1) # Main Viewport & Controls

        # 1. Left Sidebar Panel
        self.sidebar = SidebarControls(
            self,
            width=280,
            on_audio_selected=self._on_audio_selected,
            on_image_selected=self._on_image_selected,
            on_aspect_changed=self._on_aspect_changed,
            on_mode_changed=self._on_mode_changed,
            on_pad_color_changed=self._on_pad_color_changed
        )
        self.sidebar.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=0, pady=0)

        # 2. Center Viewport Area
        center_frame = ctk.CTkFrame(self, fg_color=COLOR_PALETTE["background_primary"], corner_radius=0)
        center_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        center_frame.grid_rowconfigure(0, weight=1) # Canvas Preview Viewport
        center_frame.grid_rowconfigure(1, weight=0) # Waveform Settings
        center_frame.grid_rowconfigure(2, weight=0) # Log Console
        center_frame.grid_columnconfigure(0, weight=1)

        # Canvas Preview
        self.canvas_preview = CanvasPreview(
            center_frame,
            on_bounds_changed=self._on_canvas_drag_bounds
        )
        self.canvas_preview.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        # Waveform Settings
        self.waveform_settings = WaveformSettings(
            center_frame,
            on_waveform_changed=self._on_waveform_style_changed,
            on_bounds_slider_changed=self._on_slider_bounds_changed
        )
        self.waveform_settings.grid(row=1, column=0, sticky="ew", padx=5, pady=5)

        # Terminal Log Console
        self.terminal_console = TerminalConsole(center_frame)
        self.terminal_console.grid(row=2, column=0, sticky="ew", padx=5, pady=5)

        # 3. Render Control Panel Footer
        self.render_panel = RenderPanel(
            self,
            on_start_render=self._start_rendering,
            on_cancel_render=self._cancel_rendering
        )
        self.render_panel.grid(row=1, column=1, sticky="ew", padx=0, pady=0)

    def _initialize_engine(self):
        """Resolve system binaries & detect hardware acceleration."""
        self.terminal_console.append_log("Initializing AudioOverImage Producer engine...")
        self.ffmpeg_path, self.ffprobe_path = BinaryResolver.resolve_ffmpeg_and_ffprobe()

        ffmpeg_ok = self.ffmpeg_path is not None and os.path.isfile(self.ffmpeg_path)
        ffprobe_ok = self.ffprobe_path is not None and os.path.isfile(self.ffprobe_path)

        if ffmpeg_ok:
            self.best_encoder = HWAccelDetector.detect_best_encoder(self.ffmpeg_path)
            self.terminal_console.append_log(f"FFmpeg binary: {self.ffmpeg_path}")
            self.terminal_console.append_log(f"Hardware Acceleration Encoder: {self.best_encoder}")
        else:
            self.terminal_console.append_log("WARNING: FFmpeg binary not found!")

        self.sidebar.set_binary_status(ffmpeg_ok, ffprobe_ok, self.best_encoder)

        # Render initial preview background
        self._update_preview_background()

    def poll_event_queue(self):
        """Poll thread-safe event queue every 40ms (25 Hz refresh rate)."""
        try:
            while True:
                payload = self.event_queue.get_nowait()
                event_type = payload.get("event")

                if event_type == "TELEMETRY":
                    self.render_panel.update_telemetry(payload)
                    if "log_line" in payload:
                        self.terminal_console.append_log(payload["log_line"])

                elif event_type == "LOG":
                    self.terminal_console.append_log(payload.get("text", ""))

                elif event_type == "COMPLETE":
                    output_path = payload.get("output_path", "")
                    self.render_panel.on_render_complete(output_path)
                    self.terminal_console.append_log(f"✓ RENDER COMPLETE: {output_path}")

                elif event_type == "ERROR":
                    err = payload.get("error_msg", "Unknown error")
                    self.render_panel.on_render_error(err)
                    self.terminal_console.append_log(f"❌ RENDER ERROR: {err}")

                elif event_type == "ABORTED":
                    msg = payload.get("message", "Job aborted")
                    self.render_panel.on_render_aborted()
                    self.terminal_console.append_log(f"⏹ {msg}")

                self.event_queue.task_done()
        except queue.Empty:
            pass
        finally:
            self.after(40, self.poll_event_queue)

    def _on_audio_selected(self, audio_path: str):
        """Handle audio file selection & probe metadata."""
        if not self.ffprobe_path or not os.path.isfile(self.ffprobe_path):
            self.terminal_console.append_log(f"Selected audio file: {audio_path}")
            return

        def probe_task():
            try:
                info = AudioAnalyzer.probe_audio_metadata(self.ffprobe_path, audio_path)
                pcm = AudioAnalyzer.extract_pcm_samples(self.ffmpeg_path, audio_path, max_samples=600)
                self.event_queue.put({"event": "AUDIO_PROBED", "info": info, "pcm": pcm})
            except Exception as e:
                logger.error(f"Failed to probe audio: {e}")

        import threading
        threading.Thread(target=probe_task, daemon=True).start()

    def _on_image_selected(self, image_path: str):
        """Handle background image selection."""
        self._update_preview_background()

    def _on_aspect_changed(self, aspect_key: str):
        """Handle aspect ratio preset change."""
        self.current_aspect_key = aspect_key
        preset = ASPECT_RATIO_PRESETS.get(aspect_key, {"width": 1920, "height": 1080})
        self.current_export_w = preset["width"]
        self.current_export_h = preset["height"]

        self.canvas_preview.set_export_resolution(self.current_export_w, self.current_export_h)
        self._update_preview_background()

    def _on_mode_changed(self, mode: str):
        """Handle background fitting mode change."""
        self.background_mode = mode
        self._update_preview_background()

    def _on_pad_color_changed(self, color_hex: str):
        """Handle solid padding color change."""
        self.pad_color_hex = color_hex
        self._update_preview_background()

    def _on_waveform_style_changed(self):
        """Update canvas preview waveform mode & colors."""
        mode = self.waveform_settings.mode
        color = self.waveform_settings.color_hex
        self.canvas_preview.update_waveform_style(mode, color)

    def _on_canvas_drag_bounds(self, bounds: Tuple[float, float, float, float]):
        """Update waveform settings sliders when canvas preview box is dragged."""
        x, y, w, h = bounds
        self.waveform_settings.update_bounds(x, y, w, h)

    def _on_slider_bounds_changed(self, bounds: Tuple[float, float, float, float]):
        """Update canvas preview box when sliders are moved."""
        x, y, w, h = bounds
        self.canvas_preview.set_normalized_bounds(x, y, w, h)

    def _update_preview_background(self):
        """Re-process composite background image and update canvas preview."""
        img_path = self.sidebar.image_path
        mode = self.sidebar.combo_mode.get()
        pad_color = self.sidebar.pad_color_hex

        processed = ImageProcessor.process_background(
            img_path,
            self.current_export_w,
            self.current_export_h,
            mode=mode,
            pad_color_hex=pad_color
        )
        self.processed_bg_image = processed
        self.canvas_preview.update_background_image(processed)

    def _start_rendering(self):
        """Validate inputs and launch non-blocking FFmpeg transcoding worker thread."""
        audio_path = self.sidebar.audio_path
        if not audio_path or not os.path.isfile(audio_path):
            self.terminal_console.append_log("ERROR: Please select a valid audio file before rendering.")
            return

        if not self.ffmpeg_path or not os.path.isfile(self.ffmpeg_path):
            self.terminal_console.append_log("ERROR: FFmpeg binary path is missing!")
            return

        # 1. Save pre-processed background image to temp file
        temp_dir = tempfile.gettempdir()
        self.temp_bg_file = os.path.join(temp_dir, f"audiooverimage_bg_{os.getpid()}.png")
        if self.processed_bg_image:
            self.processed_bg_image.save(self.temp_bg_file, "PNG")

        # 2. Determine output destination filename
        output_dir = self.render_panel.get_output_directory()
        if not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)

        audio_name = os.path.splitext(os.path.basename(audio_path))[0]
        out_filename = f"{audio_name}_{self.current_aspect_key.replace(':', 'x')}.mp4"
        output_path = os.path.join(output_dir, out_filename)

        # 3. Probe audio duration
        duration_sec = 60.0
        try:
            if self.ffprobe_path:
                info = AudioAnalyzer.probe_audio_metadata(self.ffprobe_path, audio_path)
                duration_sec = info.get("duration", 60.0)
        except Exception as e:
            logger.warning(f"Using estimated audio duration: {e}")

        # 4. Build Filtergraph formula
        mode = self.waveform_settings.mode
        color = self.waveform_settings.color_hex
        norm_bounds = self.canvas_preview.get_normalized_bounds()

        filtergraph_str, output_label = FiltergraphBuilder.build_filtergraph(
            self.current_export_w,
            self.current_export_h,
            mode,
            color,
            norm_bounds
        )

        # 5. Determine encoder preset flags
        codec_flags = HWAccelDetector.get_encoder_preset_flags(self.best_encoder)

        self.terminal_console.append_log(f"Starting transcode: {audio_name} -> {out_filename}")
        self.render_panel.set_render_active(True)

        # 6. Launch Worker Thread
        self.active_transcode_worker = TranscodeWorker(
            ffmpeg_path=self.ffmpeg_path,
            audio_path=audio_path,
            bg_image_path=self.temp_bg_file,
            output_path=output_path,
            duration_sec=duration_sec,
            codec=self.best_encoder,
            codec_flags=codec_flags,
            filtergraph_str=filtergraph_str,
            output_label=output_label,
            fps=30,
            event_queue=self.event_queue
        )
        self.active_transcode_worker.start()

    def _cancel_rendering(self):
        """Cancel active rendering job."""
        if self.active_transcode_worker:
            self.terminal_console.append_log("Cancelling rendering job...")
            self.active_transcode_worker.cancel()
            self.active_transcode_worker = None
