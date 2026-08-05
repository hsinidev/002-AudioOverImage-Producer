import os
import customtkinter as ctk
from tkinter import filedialog, colorchooser
from typing import Callable, Dict, Any, Optional
from gui.styles.theme_tokens import (
    COLOR_PALETTE,
    TYPOGRAPHY,
    ASPECT_RATIO_PRESETS,
    BACKGROUND_SCALING_MODES
)
from utils.logger import get_logger

logger = get_logger()

class SidebarControls(ctk.CTkScrollableFrame):
    """Left Sidebar containing media pickers, aspect ratio dropdowns, scaling options."""

    def __init__(
        self,
        master,
        on_audio_selected: Optional[Callable[[str], None]] = None,
        on_image_selected: Optional[Callable[[str], None]] = None,
        on_aspect_changed: Optional[Callable[[str], None]] = None,
        on_mode_changed: Optional[Callable[[str], None]] = None,
        on_pad_color_changed: Optional[Callable[[str], None]] = None,
        **kwargs
    ):
        super().__init__(
            master,
            fg_color=COLOR_PALETTE["background_secondary"],
            scrollbar_button_color=COLOR_PALETTE["border_color"],
            scrollbar_button_hover_color=COLOR_PALETTE["surface_card"],
            **kwargs
        )

        self.on_audio_selected = on_audio_selected
        self.on_image_selected = on_image_selected
        self.on_aspect_changed = on_aspect_changed
        self.on_mode_changed = on_mode_changed
        self.on_pad_color_changed = on_pad_color_changed

        self.audio_path: str = ""
        self.image_path: str = ""
        self.pad_color_hex: str = "#0A0E14"

        self._build_ui()

    def _build_ui(self):
        """Construct sidebar controls layout."""
        self.grid_columnconfigure(0, weight=1)

        # Header Title
        lbl_title = ctk.CTkLabel(
            self,
            text="🎵 AudioOverImage Producer",
            font=(TYPOGRAPHY["font_family"], 16, "bold"),
            text_color=COLOR_PALETTE["accent_primary"],
            anchor="w"
        )
        lbl_title.grid(row=0, column=0, padx=15, pady=(15, 5), sticky="w")

        lbl_sub = ctk.CTkLabel(
            self,
            text="Studio Content Generator v1.0-PROD",
            font=(TYPOGRAPHY["font_family"], 10),
            text_color=COLOR_PALETTE["text_secondary"],
            anchor="w"
        )
        lbl_sub.grid(row=1, column=0, padx=15, pady=(0, 15), sticky="w")

        # --- SECTION 1: MEDIA INPUTS ---
        sec1 = ctk.CTkFrame(self, fg_color=COLOR_PALETTE["surface_card"], corner_radius=8)
        sec1.grid(row=2, column=0, padx=10, pady=5, sticky="ew")
        sec1.grid_columnconfigure(0, weight=1)

        lbl_sec1 = ctk.CTkLabel(
            sec1,
            text="📁 Media Inputs",
            font=(TYPOGRAPHY["font_family"], 13, "bold"),
            text_color=COLOR_PALETTE["text_primary"]
        )
        lbl_sec1.grid(row=0, column=0, padx=12, pady=(10, 5), sticky="w")

        # Audio Track Picker
        self.btn_audio = ctk.CTkButton(
            sec1,
            text="Choose Audio Track...",
            fg_color=COLOR_PALETTE["background_secondary"],
            hover_color=COLOR_PALETTE["border_color"],
            text_color=COLOR_PALETTE["text_primary"],
            font=(TYPOGRAPHY["font_family"], 11),
            command=self._pick_audio_file
        )
        self.btn_audio.grid(row=1, column=0, padx=12, pady=5, sticky="ew")

        self.lbl_audio_info = ctk.CTkLabel(
            sec1,
            text="No audio selected (.mp3, .wav, .m4a, .flac)",
            font=(TYPOGRAPHY["font_family"], 10),
            text_color=COLOR_PALETTE["text_secondary"],
            anchor="w",
            wraplength=220
        )
        self.lbl_audio_info.grid(row=2, column=0, padx=12, pady=(0, 10), sticky="w")

        # Background Image Picker
        self.btn_image = ctk.CTkButton(
            sec1,
            text="Choose Background Image...",
            fg_color=COLOR_PALETTE["background_secondary"],
            hover_color=COLOR_PALETTE["border_color"],
            text_color=COLOR_PALETTE["text_primary"],
            font=(TYPOGRAPHY["font_family"], 11),
            command=self._pick_image_file
        )
        self.btn_image.grid(row=3, column=0, padx=12, pady=5, sticky="ew")

        self.lbl_image_info = ctk.CTkLabel(
            sec1,
            text="No image selected (.png, .jpg, .webp)",
            font=(TYPOGRAPHY["font_family"], 10),
            text_color=COLOR_PALETTE["text_secondary"],
            anchor="w",
            wraplength=220
        )
        self.lbl_image_info.grid(row=4, column=0, padx=12, pady=(0, 10), sticky="w")

        # --- SECTION 2: CANVAS & ASPECT RATIO ---
        sec2 = ctk.CTkFrame(self, fg_color=COLOR_PALETTE["surface_card"], corner_radius=8)
        sec2.grid(row=3, column=0, padx=10, pady=10, sticky="ew")
        sec2.grid_columnconfigure(0, weight=1)

        lbl_sec2 = ctk.CTkLabel(
            sec2,
            text="📐 Aspect Ratio Presets",
            font=(TYPOGRAPHY["font_family"], 13, "bold"),
            text_color=COLOR_PALETTE["text_primary"]
        )
        lbl_sec2.grid(row=0, column=0, padx=12, pady=(10, 5), sticky="w")

        aspect_options = [f"{k} - {v['label']}" for k, v in ASPECT_RATIO_PRESETS.items()]
        self.combo_aspect = ctk.CTkOptionMenu(
            sec2,
            values=aspect_options,
            fg_color=COLOR_PALETTE["background_secondary"],
            button_color=COLOR_PALETTE["border_color"],
            button_hover_color=COLOR_PALETTE["accent_hover"],
            text_color=COLOR_PALETTE["text_primary"],
            font=(TYPOGRAPHY["font_family"], 11),
            command=self._on_aspect_selected
        )
        self.combo_aspect.grid(row=1, column=0, padx=12, pady=(5, 10), sticky="ew")

        # --- SECTION 3: BACKGROUND SCALING MODE ---
        sec3 = ctk.CTkFrame(self, fg_color=COLOR_PALETTE["surface_card"], corner_radius=8)
        sec3.grid(row=4, column=0, padx=10, pady=5, sticky="ew")
        sec3.grid_columnconfigure(0, weight=1)

        lbl_sec3 = ctk.CTkLabel(
            sec3,
            text="🖼️ Background Fitting Mode",
            font=(TYPOGRAPHY["font_family"], 13, "bold"),
            text_color=COLOR_PALETTE["text_primary"]
        )
        lbl_sec3.grid(row=0, column=0, padx=12, pady=(10, 5), sticky="w")

        self.combo_mode = ctk.CTkOptionMenu(
            sec3,
            values=BACKGROUND_SCALING_MODES,
            fg_color=COLOR_PALETTE["background_secondary"],
            button_color=COLOR_PALETTE["border_color"],
            button_hover_color=COLOR_PALETTE["accent_hover"],
            text_color=COLOR_PALETTE["text_primary"],
            font=(TYPOGRAPHY["font_family"], 11),
            command=self._on_mode_selected
        )
        self.combo_mode.grid(row=1, column=0, padx=12, pady=5, sticky="ew")

        # Solid Padding Color Trigger Button
        self.btn_color_picker = ctk.CTkButton(
            sec3,
            text="Contain Border Color (#0A0E14)",
            fg_color=self.pad_color_hex,
            hover_color=COLOR_PALETTE["border_color"],
            text_color=COLOR_PALETTE["text_primary"],
            font=(TYPOGRAPHY["font_family"], 11),
            command=self._choose_pad_color
        )
        self.btn_color_picker.grid(row=2, column=0, padx=12, pady=(5, 10), sticky="ew")

        # --- SECTION 4: SYSTEM BINARY DIAGNOSTICS ---
        sec4 = ctk.CTkFrame(self, fg_color=COLOR_PALETTE["surface_card"], corner_radius=8)
        sec4.grid(row=5, column=0, padx=10, pady=10, sticky="ew")
        sec4.grid_columnconfigure(0, weight=1)

        lbl_sec4 = ctk.CTkLabel(
            sec4,
            text="⚙️ Engine Status",
            font=(TYPOGRAPHY["font_family"], 13, "bold"),
            text_color=COLOR_PALETTE["text_primary"]
        )
        lbl_sec4.grid(row=0, column=0, padx=12, pady=(10, 5), sticky="w")

        self.lbl_binary_status = ctk.CTkLabel(
            sec4,
            text="FFmpeg: Checking...",
            font=(TYPOGRAPHY["font_family"], 10),
            text_color=COLOR_PALETTE["warning_amber"],
            anchor="w"
        )
        self.lbl_binary_status.grid(row=1, column=0, padx=12, pady=(0, 10), sticky="w")

    def set_binary_status(self, ffmpeg_ok: bool, ffprobe_ok: bool, encoder: str):
        """Update system binary status text."""
        if ffmpeg_ok and ffprobe_ok:
            txt = f"✓ FFmpeg Engine Ready\n✓ Codec: {encoder}"
            color = COLOR_PALETTE["accent_primary"]
        else:
            txt = "⚠ FFmpeg Binaries Not Found!"
            color = COLOR_PALETTE["danger_red"]

        self.lbl_binary_status.configure(text=txt, text_color=color)

    def _pick_audio_file(self):
        """Open audio file picker dialog."""
        filepath = filedialog.askopenfilename(
            title="Select Audio Track",
            filetypes=[
                ("Audio Files", "*.mp3 *.wav *.m4a *.flac *.aac *.ogg *.wma"),
                ("All Files", "*.*")
            ]
        )
        if filepath:
            self.audio_path = filepath
            filename = os.path.basename(filepath)
            self.lbl_audio_info.configure(text=f"Selected: {filename}", text_color=COLOR_PALETTE["accent_primary"])
            if self.on_audio_selected:
                self.on_audio_selected(filepath)

    def _pick_image_file(self):
        """Open image file picker dialog."""
        filepath = filedialog.askopenfilename(
            title="Select Background Image",
            filetypes=[
                ("Image Files", "*.png *.jpg *.jpeg *.webp *.bmp *.tiff"),
                ("All Files", "*.*")
            ]
        )
        if filepath:
            self.image_path = filepath
            filename = os.path.basename(filepath)
            self.lbl_image_info.configure(text=f"Selected: {filename}", text_color=COLOR_PALETTE["accent_primary"])
            if self.on_image_selected:
                self.on_image_selected(filepath)

    def _on_aspect_selected(self, val: str):
        """Handle aspect ratio dropdown change."""
        key = val.split(" ")[0]
        if self.on_aspect_changed:
            self.on_aspect_changed(key)

    def _on_mode_selected(self, val: str):
        """Handle scaling mode dropdown change."""
        if self.on_mode_changed:
            self.on_mode_changed(val)

    def _choose_pad_color(self):
        """Open color picker for border color."""
        color = colorchooser.askcolor(color=self.pad_color_hex, title="Select Border Padding Color")
        if color and color[1]:
            self.pad_color_hex = color[1]
            self.btn_color_picker.configure(
                text=f"Contain Border Color ({self.pad_color_hex})",
                fg_color=self.pad_color_hex
            )
            if self.on_pad_color_changed:
                self.on_pad_color_changed(self.pad_color_hex)
