import tkinter as tk
import customtkinter as ctk
from PIL import Image, ImageTk
from typing import Tuple, Optional, Callable
from gui.styles.theme_tokens import COLOR_PALETTE, TYPOGRAPHY
from utils.helpers import calculate_aspect_fit_bounds, hex_to_rgb
from utils.logger import get_logger

logger = get_logger()

class CanvasPreview(ctk.CTkFrame):
    """
    WYSIWYG Live Canvas Preview Viewport Component.
    - Scales processed background image into fitting aspect bounds.
    - Draws interactive visualizer bounding box for dragging & positioning.
    - Maps normalized coordinates (x, y, w, h) in [0.0, 1.0] range.
    """

    def __init__(
        self,
        master,
        on_bounds_changed: Optional[Callable[[Tuple[float, float, float, float]], None]] = None,
        **kwargs
    ):
        super().__init__(master, fg_color=COLOR_PALETTE["background_primary"], **kwargs)
        self.on_bounds_changed = on_bounds_changed

        self.target_export_w = 1920
        self.target_export_h = 1080

        # Normalized waveform box coords (x_norm, y_norm, w_norm, h_norm) in [0.0 - 1.0]
        # Default: centered near bottom
        self.norm_x = 0.15
        self.norm_y = 0.70
        self.norm_w = 0.70
        self.norm_h = 0.20

        self.pil_bg_image: Optional[Image.Image] = None
        self.tk_bg_image: Optional[ImageTk.PhotoImage] = None
        self.sample_pcm_waveform = None

        self.waveform_mode = "Line Waveform"
        self.waveform_color = COLOR_PALETTE["accent_primary"]

        # Canvas drag tracking
        self.is_dragging = False
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.drag_orig_norm_x = 0.15
        self.drag_orig_norm_y = 0.70

        # Build UI layout
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.canvas = tk.Canvas(
            self,
            bg=COLOR_PALETTE["background_primary"],
            highlightthickness=1,
            highlightbackground=COLOR_PALETTE["border_color"]
        )
        self.canvas.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # Bind events
        self.canvas.bind("<Configure>", self._on_canvas_resize)
        self.canvas.bind("<ButtonPress-1>", self._on_drag_start)
        self.canvas.bind("<B1-Motion>", self._on_drag_motion)
        self.canvas.bind("<ButtonRelease-1>", self._on_drag_release)

    def set_export_resolution(self, width: int, height: int):
        """Set export resolution preset (e.g. 1920x1080 or 1080x1920)."""
        self.target_export_w = width
        self.target_export_h = height
        self.redraw_preview()

    def update_background_image(self, pil_image: Image.Image):
        """Update preview background image."""
        self.pil_bg_image = pil_image
        self.redraw_preview()

    def update_waveform_style(self, mode: str, color: str):
        """Update preview waveform style & color."""
        self.waveform_mode = mode
        self.waveform_color = color
        self.redraw_preview()

    def set_sample_pcm(self, pcm_array):
        """Set PCM sample array for interactive waveform preview line drawing."""
        self.sample_pcm_waveform = pcm_array
        self.redraw_preview()

    def get_normalized_bounds(self) -> Tuple[float, float, float, float]:
        """Return normalized bounding box tuple (x, y, w, h)."""
        return self.norm_x, self.norm_y, self.norm_w, self.norm_h

    def set_normalized_bounds(self, x: float, y: float, w: float, h: float):
        """Set normalized bounding box manually from slider inputs."""
        self.norm_x = max(0.0, min(1.0 - w, x))
        self.norm_y = max(0.0, min(1.0 - h, y))
        self.norm_w = max(0.05, min(1.0, w))
        self.norm_h = max(0.05, min(1.0, h))
        self.redraw_preview()
        if self.on_bounds_changed:
            self.on_bounds_changed((self.norm_x, self.norm_y, self.norm_w, self.norm_h))

    def _on_canvas_resize(self, event):
        """Redraw when canvas viewport resizes."""
        self.redraw_preview()

    def redraw_preview(self):
        """Redraw canvas content (background, aspect frame guide, draggable overlay box)."""
        self.canvas.delete("all")

        canvas_w = self.canvas.winfo_width()
        canvas_h = self.canvas.winfo_height()

        if canvas_w <= 20 or canvas_h <= 20:
            return

        # 1. Calculate fitting bounds for aspect ratio box inside canvas
        frame_x, frame_y, frame_w, frame_h = calculate_aspect_fit_bounds(
            self.target_export_w, self.target_export_h, canvas_w, canvas_h
        )

        # 2. Draw background image inside frame bounds if available
        if self.pil_bg_image:
            try:
                scaled_bg = self.pil_bg_image.resize((max(1, frame_w), max(1, frame_h)), Image.Resampling.LANCZOS)
                self.tk_bg_image = ImageTk.PhotoImage(scaled_bg)
                self.canvas.create_image(frame_x, frame_y, anchor="nw", image=self.tk_bg_image)
            except Exception as e:
                logger.error(f"Failed to render preview background frame: {e}")
        else:
            # Draw placeholder background
            self.canvas.create_rectangle(
                frame_x, frame_y, frame_x + frame_w, frame_y + frame_h,
                fill=COLOR_PALETTE["background_secondary"], outline=""
            )

        # 3. Draw outer dark dimming overlay outside aspect ratio frame
        # Top bar
        if frame_y > 0:
            self.canvas.create_rectangle(0, 0, canvas_w, frame_y, fill="#000000", outline="")
        # Bottom bar
        if (frame_y + frame_h) < canvas_h:
            self.canvas.create_rectangle(0, frame_y + frame_h, canvas_w, canvas_h, fill="#000000", outline="")
        # Left bar
        if frame_x > 0:
            self.canvas.create_rectangle(0, frame_y, frame_x, frame_y + frame_h, fill="#000000", outline="")
        # Right bar
        if (frame_x + frame_w) < canvas_w:
            self.canvas.create_rectangle(frame_x + frame_w, frame_y, canvas_w, frame_y + frame_h, fill="#000000", outline="")

        # 4. Draw aspect ratio guide outline
        self.canvas.create_rectangle(
            frame_x, frame_y, frame_x + frame_w, frame_y + frame_h,
            outline=COLOR_PALETTE["accent_secondary"], width=2
        )

        # Resolution label badge
        res_label = f"{self.target_export_w}x{self.target_export_h}"
        self.canvas.create_text(
            frame_x + 10, frame_y + 15,
            text=res_label, anchor="w",
            fill=COLOR_PALETTE["text_secondary"], font=(TYPOGRAPHY["font_family"], 10, "bold")
        )

        # 5. Draw visualizer overlay bounding box if enabled
        if self.waveform_mode != "None":
            box_x = frame_x + (self.norm_x * frame_w)
            box_y = frame_y + (self.norm_y * frame_h)
            box_w = self.norm_w * frame_w
            box_h = self.norm_h * frame_h

            # Interactive outline box
            self.canvas.create_rectangle(
                box_x, box_y, box_x + box_w, box_y + box_h,
                outline=COLOR_PALETTE["accent_primary"], width=2, dash=(4, 4),
                tags="wave_box"
            )

            # Draw preview waveform lines inside box
            self._draw_preview_waveform(box_x, box_y, box_w, box_h)

            # Handle corner drag indicators
            self.canvas.create_rectangle(box_x - 3, box_y - 3, box_x + 3, box_y + 3, fill=COLOR_PALETTE["accent_primary"])
            self.canvas.create_rectangle(box_x + box_w - 3, box_y + box_h - 3, box_x + box_w + 3, box_y + box_h + 3, fill=COLOR_PALETTE["accent_primary"])

            # Tag text label
            tag_text = f"Visualizer ({self.waveform_mode}) [Drag to reposition]"
            self.canvas.create_text(
                box_x + 5, box_y - 12,
                text=tag_text, anchor="w",
                fill=COLOR_PALETTE["accent_primary"], font=(TYPOGRAPHY["font_family"], 9, "bold")
            )

    def _draw_preview_waveform(self, x: float, y: float, w: float, h: float):
        """Draw interactive preview waveform amplitude bars/lines inside bounding box."""
        if w <= 10 or h <= 10:
            return

        points_count = min(60, int(w // 6))
        mid_y = y + (h / 2.0)

        if self.sample_pcm_waveform is not None and len(self.sample_pcm_waveform) > 0:
            step = max(1, len(self.sample_pcm_waveform) // points_count)
            amps = self.sample_pcm_waveform[::step][:points_count]
        else:
            # Fallback wave math pattern
            import math
            amps = [abs(math.sin(i * 0.2)) * 0.8 + 0.1 for i in range(points_count)]

        color = self.waveform_color if not self.waveform_color.startswith("#") else self.waveform_color

        if "Histogram" in self.waveform_mode or "Bar" in self.waveform_mode:
            bar_w = max(2, (w / points_count) * 0.7)
            for i, amp in enumerate(amps):
                bx = x + (i * (w / points_count))
                bh = amp * (h * 0.8)
                by = y + h - bh
                self.canvas.create_rectangle(bx, by, bx + bar_w, y + h, fill=color, outline="")
        else: # Line Waveform
            line_pts = []
            for i, amp in enumerate(amps):
                lx = x + (i * (w / (points_count - 1)))
                ly = mid_y + ((amp - 0.5) * (h * 0.7))
                line_pts.extend([lx, ly])
            if len(line_pts) >= 4:
                self.canvas.create_line(line_pts, fill=color, width=2, smooth=True)

    def _on_drag_start(self, event):
        """Handle canvas drag start event."""
        canvas_w = self.canvas.winfo_width()
        canvas_h = self.canvas.winfo_height()
        frame_x, frame_y, frame_w, frame_h = calculate_aspect_fit_bounds(
            self.target_export_w, self.target_export_h, canvas_w, canvas_h
        )

        box_x = frame_x + (self.norm_x * frame_w)
        box_y = frame_y + (self.norm_y * frame_h)
        box_w = self.norm_w * frame_w
        box_h = self.norm_h * frame_h

        # Check if click is inside waveform box
        if box_x <= event.x <= box_x + box_w and box_y <= event.y <= box_y + box_h:
            self.is_dragging = True
            self.drag_start_x = event.x
            self.drag_start_y = event.y
            self.drag_orig_norm_x = self.norm_x
            self.drag_orig_norm_y = self.norm_y

    def _on_drag_motion(self, event):
        """Handle continuous dragging of waveform bounding box."""
        if not self.is_dragging:
            return

        canvas_w = self.canvas.winfo_width()
        canvas_h = self.canvas.winfo_height()
        frame_x, frame_y, frame_w, frame_h = calculate_aspect_fit_bounds(
            self.target_export_w, self.target_export_h, canvas_w, canvas_h
        )

        dx = event.x - self.drag_start_x
        dy = event.y - self.drag_start_y

        d_norm_x = dx / max(1, frame_w)
        d_norm_y = dy / max(1, frame_h)

        new_norm_x = max(0.0, min(1.0 - self.norm_w, self.drag_orig_norm_x + d_norm_x))
        new_norm_y = max(0.0, min(1.0 - self.norm_h, self.drag_orig_norm_y + d_norm_y))

        self.norm_x = new_norm_x
        self.norm_y = new_norm_y

        self.redraw_preview()
        if self.on_bounds_changed:
            self.on_bounds_changed((self.norm_x, self.norm_y, self.norm_w, self.norm_h))

    def _on_drag_release(self, event):
        """Handle drag end."""
        self.is_dragging = False
