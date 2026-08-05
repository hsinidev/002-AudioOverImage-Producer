import customtkinter as ctk
from tkinter import colorchooser
from typing import Callable, Tuple, Optional
from gui.styles.theme_tokens import (
    COLOR_PALETTE,
    TYPOGRAPHY,
    WAVEFORM_RENDER_MODES
)
from utils.logger import get_logger

logger = get_logger()

class WaveformSettings(ctk.CTkFrame):
    """Configuration panel for Waveform & Spectrum Visualizers."""

    def __init__(
        self,
        master,
        on_waveform_changed: Optional[Callable[[], None]] = None,
        on_bounds_slider_changed: Optional[Callable[[Tuple[float, float, float, float]], None]] = None,
        **kwargs
    ):
        super().__init__(master, fg_color=COLOR_PALETTE["surface_card"], corner_radius=8, **kwargs)
        self.on_waveform_changed = on_waveform_changed
        self.on_bounds_slider_changed = on_bounds_slider_changed

        self.mode = "Line Waveform"
        self.color_hex = COLOR_PALETTE["accent_primary"]
        self.norm_x = 0.15
        self.norm_y = 0.70
        self.norm_w = 0.70
        self.norm_h = 0.20

        self._build_ui()

    def _build_ui(self):
        """Construct visualizer settings UI controls."""
        self.grid_columnconfigure(1, weight=1)

        # Header Title
        lbl_title = ctk.CTkLabel(
            self,
            text="📊 Waveform & Spectrum Visualizer Controls",
            font=(TYPOGRAPHY["font_family"], 13, "bold"),
            text_color=COLOR_PALETTE["text_primary"]
        )
        lbl_title.grid(row=0, column=0, columnspan=2, padx=12, pady=(10, 5), sticky="w")

        # Row 1: Render Mode Dropdown
        lbl_mode = ctk.CTkLabel(
            self, text="Visualizer Mode:",
            font=(TYPOGRAPHY["font_family"], 11), text_color=COLOR_PALETTE["text_secondary"]
        )
        lbl_mode.grid(row=1, column=0, padx=12, pady=5, sticky="w")

        self.combo_mode = ctk.CTkOptionMenu(
            self,
            values=WAVEFORM_RENDER_MODES,
            fg_color=COLOR_PALETTE["background_secondary"],
            button_color=COLOR_PALETTE["border_color"],
            button_hover_color=COLOR_PALETTE["accent_hover"],
            text_color=COLOR_PALETTE["text_primary"],
            font=(TYPOGRAPHY["font_family"], 11),
            command=self._on_mode_changed
        )
        self.combo_mode.grid(row=1, column=1, padx=12, pady=5, sticky="ew")

        # Row 2: Color Trigger
        lbl_color = ctk.CTkLabel(
            self, text="Color Gradient:",
            font=(TYPOGRAPHY["font_family"], 11), text_color=COLOR_PALETTE["text_secondary"]
        )
        lbl_color.grid(row=2, column=0, padx=12, pady=5, sticky="w")

        self.btn_color = ctk.CTkButton(
            self,
            text=f"Waveform Color ({self.color_hex})",
            fg_color=self.color_hex,
            hover_color=COLOR_PALETTE["border_color"],
            text_color=COLOR_PALETTE["background_primary"],
            font=(TYPOGRAPHY["font_family"], 11, "bold"),
            command=self._choose_color
        )
        self.btn_color.grid(row=2, column=1, padx=12, pady=5, sticky="ew")

        # Row 3: Position Presets
        lbl_preset = ctk.CTkLabel(
            self, text="Position Presets:",
            font=(TYPOGRAPHY["font_family"], 11), text_color=COLOR_PALETTE["text_secondary"]
        )
        lbl_preset.grid(row=3, column=0, padx=12, pady=5, sticky="w")

        preset_frame = ctk.CTkFrame(self, fg_color="transparent")
        preset_frame.grid(row=3, column=1, padx=12, pady=5, sticky="ew")
        preset_frame.grid_columnconfigure((0, 1, 2), weight=1)

        btn_bottom = ctk.CTkButton(
            preset_frame, text="Bottom", font=(TYPOGRAPHY["font_family"], 10),
            fg_color=COLOR_PALETTE["background_secondary"], hover_color=COLOR_PALETTE["border_color"],
            command=lambda: self.update_bounds(0.1, 0.75, 0.8, 0.18)
        )
        btn_bottom.grid(row=0, column=0, padx=2, pady=2, sticky="ew")

        btn_center = ctk.CTkButton(
            preset_frame, text="Center", font=(TYPOGRAPHY["font_family"], 10),
            fg_color=COLOR_PALETTE["background_secondary"], hover_color=COLOR_PALETTE["border_color"],
            command=lambda: self.update_bounds(0.15, 0.40, 0.70, 0.20)
        )
        btn_center.grid(row=0, column=1, padx=2, pady=2, sticky="ew")

        btn_top = ctk.CTkButton(
            preset_frame, text="Top Bar", font=(TYPOGRAPHY["font_family"], 10),
            fg_color=COLOR_PALETTE["background_secondary"], hover_color=COLOR_PALETTE["border_color"],
            command=lambda: self.update_bounds(0.05, 0.05, 0.90, 0.15)
        )
        btn_top.grid(row=0, column=2, padx=2, pady=2, sticky="ew")

        # Row 4: Y Position Slider
        lbl_y = ctk.CTkLabel(
            self, text="Vertical Y Pos:",
            font=(TYPOGRAPHY["font_family"], 11), text_color=COLOR_PALETTE["text_secondary"]
        )
        lbl_y.grid(row=4, column=0, padx=12, pady=2, sticky="w")

        self.slider_y = ctk.CTkSlider(
            self, from_=0.0, to=0.9,
            button_color=COLOR_PALETTE["accent_primary"],
            progress_color=COLOR_PALETTE["accent_secondary"],
            command=self._on_slider_move
        )
        self.slider_y.set(self.norm_y)
        self.slider_y.grid(row=4, column=1, padx=12, pady=2, sticky="ew")

        # Row 5: Height Slider
        lbl_h = ctk.CTkLabel(
            self, text="Visualizer Height:",
            font=(TYPOGRAPHY["font_family"], 11), text_color=COLOR_PALETTE["text_secondary"]
        )
        lbl_h.grid(row=5, column=0, padx=12, pady=(2, 10), sticky="w")

        self.slider_h = ctk.CTkSlider(
            self, from_=0.05, to=0.5,
            button_color=COLOR_PALETTE["accent_primary"],
            progress_color=COLOR_PALETTE["accent_secondary"],
            command=self._on_slider_move
        )
        self.slider_h.set(self.norm_h)
        self.slider_h.grid(row=5, column=1, padx=12, pady=(2, 10), sticky="ew")

    def _on_mode_changed(self, val: str):
        """Handle visualizer mode change."""
        self.mode = val
        if self.on_waveform_changed:
            self.on_waveform_changed()

    def _choose_color(self):
        """Color picker for waveform line/bar gradient."""
        color = colorchooser.askcolor(color=self.color_hex, title="Select Waveform Accent Color")
        if color and color[1]:
            self.color_hex = color[1]
            self.btn_color.configure(text=f"Waveform Color ({self.color_hex})", fg_color=self.color_hex)
            if self.on_waveform_changed:
                self.on_waveform_changed()

    def update_bounds(self, x: float, y: float, w: float, h: float):
        """Update slider bounds programmatically from canvas drag or preset button."""
        self.norm_x = x
        self.norm_y = y
        self.norm_w = w
        self.norm_h = h

        self.slider_y.set(self.norm_y)
        self.slider_h.set(self.norm_h)

        if self.on_bounds_slider_changed:
            self.on_bounds_slider_changed((self.norm_x, self.norm_y, self.norm_w, self.norm_h))

    def _on_slider_move(self, _val):
        """Handle manual slider adjustments."""
        self.norm_y = float(self.slider_y.get())
        self.norm_h = float(self.slider_h.get())
        if self.on_bounds_slider_changed:
            self.on_bounds_slider_changed((self.norm_x, self.norm_y, self.norm_w, self.norm_h))
