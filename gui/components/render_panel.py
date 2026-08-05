import os
import customtkinter as ctk
from tkinter import filedialog
from typing import Callable, Optional, Dict, Any
from gui.styles.theme_tokens import COLOR_PALETTE, TYPOGRAPHY
from utils.helpers import format_seconds_to_timecode
from utils.logger import get_logger

logger = get_logger()

class RenderPanel(ctk.CTkFrame):
    """Render export control footer bar featuring progress meters, ETA counters, and action triggers."""

    def __init__(
        self,
        master,
        on_start_render: Optional[Callable[[], None]] = None,
        on_cancel_render: Optional[Callable[[], None]] = None,
        **kwargs
    ):
        super().__init__(master, fg_color=COLOR_PALETTE["background_secondary"], corner_radius=0, **kwargs)
        self.on_start_render = on_start_render
        self.on_cancel_render = on_cancel_render

        self.output_dir = os.path.join(os.path.expanduser("~"), "Videos")
        if not os.path.exists(self.output_dir):
            self.output_dir = os.path.expanduser("~")

        self.resolution_quality = "1080p (Standard)"
        self.is_rendering = False

        self._build_ui()

    def _build_ui(self):
        """Build render footer UI controls."""
        self.grid_columnconfigure(1, weight=1)

        # Row 0: Destination Directory Picker & Quality
        dest_frame = ctk.CTkFrame(self, fg_color="transparent")
        dest_frame.grid(row=0, column=0, columnspan=3, padx=15, pady=(10, 5), sticky="ew")
        dest_frame.grid_columnconfigure(1, weight=1)

        lbl_dest = ctk.CTkLabel(
            dest_frame, text="Output Directory:",
            font=(TYPOGRAPHY["font_family"], 11), text_color=COLOR_PALETTE["text_secondary"]
        )
        lbl_dest.grid(row=0, column=0, padx=(0, 10), sticky="w")

        self.entry_dir = ctk.CTkEntry(
            dest_frame,
            fg_color=COLOR_PALETTE["surface_card"],
            text_color=COLOR_PALETTE["text_primary"],
            font=(TYPOGRAPHY["font_family"], 11),
            border_color=COLOR_PALETTE["border_color"]
        )
        self.entry_dir.insert(0, self.output_dir)
        self.entry_dir.grid(row=0, column=1, padx=5, sticky="ew")

        btn_browse = ctk.CTkButton(
            dest_frame, text="Browse...", width=80,
            fg_color=COLOR_PALETTE["surface_card"], hover_color=COLOR_PALETTE["border_color"],
            font=(TYPOGRAPHY["font_family"], 11), command=self._browse_output_dir
        )
        btn_browse.grid(row=0, column=2, padx=5, sticky="e")

        self.combo_res = ctk.CTkOptionMenu(
            dest_frame,
            values=["1080p (Standard)", "4K (Ultra HD 3840x2160)"],
            width=160,
            fg_color=COLOR_PALETTE["surface_card"],
            button_color=COLOR_PALETTE["border_color"],
            button_hover_color=COLOR_PALETTE["accent_hover"],
            font=(TYPOGRAPHY["font_family"], 11),
            command=self._on_quality_changed
        )
        self.combo_res.grid(row=0, column=3, padx=(10, 0), sticky="e")

        # Row 1: Action Buttons & Progress Meter
        controls_frame = ctk.CTkFrame(self, fg_color="transparent")
        controls_frame.grid(row=1, column=0, columnspan=3, padx=15, pady=(5, 12), sticky="ew")
        controls_frame.grid_columnconfigure(1, weight=1)

        # Start Render Button
        self.btn_render = ctk.CTkButton(
            controls_frame,
            text="🎬 START RENDER (EXPORT MP4)",
            font=(TYPOGRAPHY["font_family"], 12, "bold"),
            fg_color=COLOR_PALETTE["accent_primary"],
            hover_color=COLOR_PALETTE["accent_hover"],
            text_color="#000000",
            height=38, width=220,
            command=self._handle_start_click
        )
        self.btn_render.grid(row=0, column=0, padx=(0, 15), sticky="w")

        # Cancel Render Button (hidden by default)
        self.btn_cancel = ctk.CTkButton(
            controls_frame,
            text="⏹ ABORT RENDER",
            font=(TYPOGRAPHY["font_family"], 12, "bold"),
            fg_color=COLOR_PALETTE["danger_red"],
            hover_color="#D32F2F",
            text_color="#FFFFFF",
            height=38, width=140,
            command=self._handle_cancel_click
        )
        self.btn_cancel.grid(row=0, column=0, padx=(0, 15), sticky="w")
        self.btn_cancel.grid_remove() # Hide initially

        # Center Progress Meter Stack
        progress_stack = ctk.CTkFrame(controls_frame, fg_color="transparent")
        progress_stack.grid(row=0, column=1, padx=10, sticky="ew")
        progress_stack.grid_columnconfigure(0, weight=1)

        # Progress Bar
        self.progress_bar = ctk.CTkProgressBar(
            progress_stack,
            progress_color=COLOR_PALETTE["accent_primary"],
            fg_color=COLOR_PALETTE["surface_card"],
            height=14
        )
        self.progress_bar.set(0.0)
        self.progress_bar.grid(row=0, column=0, sticky="ew", pady=(2, 4))

        # Telemetry Labels
        self.lbl_status = ctk.CTkLabel(
            progress_stack,
            text="Ready to export",
            font=(TYPOGRAPHY["font_family"], 10),
            text_color=COLOR_PALETTE["text_secondary"],
            anchor="w"
        )
        self.lbl_status.grid(row=1, column=0, sticky="w")

        self.lbl_percent = ctk.CTkLabel(
            controls_frame,
            text="0.0%",
            font=(TYPOGRAPHY["font_family"], 16, "bold"),
            text_color=COLOR_PALETTE["accent_primary"],
            width=70, anchor="e"
        )
        self.lbl_percent.grid(row=0, column=2, padx=(10, 0), sticky="e")

    def _browse_output_dir(self):
        """Open folder dialog to pick destination."""
        chosen = filedialog.askdirectory(title="Select Destination Folder", initialdir=self.output_dir)
        if chosen:
            self.output_dir = chosen
            self.entry_dir.delete(0, "end")
            self.entry_dir.insert(0, self.output_dir)

    def _on_quality_changed(self, val: str):
        """Handle resolution quality preset switch."""
        self.resolution_quality = val

    def get_output_directory(self) -> str:
        """Get output destination directory."""
        return self.entry_dir.get().strip() or self.output_dir

    def set_render_active(self, active: bool):
        """Toggle UI state between Idle and Rendering."""
        self.is_rendering = active
        if active:
            self.btn_render.grid_remove()
            self.btn_cancel.grid()
            self.progress_bar.set(0.0)
            self.lbl_percent.configure(text="0.0%")
            self.lbl_status.configure(text="Initializing FFmpeg engine...", text_color=COLOR_PALETTE["warning_amber"])
        else:
            self.btn_cancel.grid_remove()
            self.btn_render.grid()

    def update_telemetry(self, data: Dict[str, Any]):
        """Update progress bar, percentage label, and ETA metrics."""
        percent = data.get("percent", 0.0)
        fps = data.get("fps", 0.0)
        speed = data.get("speed", "1.0x")
        eta_sec = data.get("eta_seconds", 0.0)

        self.progress_bar.set(percent / 100.0)
        self.lbl_percent.configure(text=f"{percent:.1f}%")

        time_str = format_seconds_to_timecode(eta_sec)
        txt = f"Rendering... {fps:.1f} FPS | Speed: {speed} | ETA: {time_str}"
        self.lbl_status.configure(text=txt, text_color=COLOR_PALETTE["accent_secondary"])

    def on_render_complete(self, output_path: str):
        """Handle completion state."""
        self.set_render_active(False)
        self.progress_bar.set(1.0)
        self.lbl_percent.configure(text="100%")
        self.lbl_status.configure(text=f"✓ Export Complete: {os.path.basename(output_path)}", text_color=COLOR_PALETTE["accent_primary"])

    def on_render_error(self, error_msg: str):
        """Handle error state."""
        self.set_render_active(False)
        self.lbl_status.configure(text=f"❌ Render Error: {error_msg}", text_color=COLOR_PALETTE["danger_red"])

    def on_render_aborted(self):
        """Handle aborted state."""
        self.set_render_active(False)
        self.lbl_status.configure(text="⏹ Render cancelled by user.", text_color=COLOR_PALETTE["warning_amber"])

    def _handle_start_click(self):
        if self.on_start_render:
            self.on_start_render()

    def _handle_cancel_click(self):
        if self.on_cancel_render:
            self.on_cancel_render()
