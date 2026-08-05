"""
Design system visual tokens for Studio Emerald & Cyber Slate theme.
"""
from typing import Dict, Any

COLOR_PALETTE: Dict[str, str] = {
    "background_primary": "#0A0E14",
    "background_secondary": "#131B26",
    "surface_card": "#1A2332",
    "accent_primary": "#00E676",
    "accent_secondary": "#1DE9B6",
    "accent_hover": "#00C853",
    "text_primary": "#E0E6ED",
    "text_secondary": "#90A4AE",
    "danger_red": "#FF5252",
    "warning_amber": "#FFD700",
    "border_color": "#263238"
}

TYPOGRAPHY: Dict[str, Any] = {
    "font_family": "Segoe UI",
    "font_family_mono": "Consolas",
    "heading_size": 18,
    "subheading_size": 14,
    "body_size": 12,
    "caption_size": 10
}

ASPECT_RATIO_PRESETS: Dict[str, Dict[str, Any]] = {
    "16:9": {"width": 1920, "height": 1080, "label": "YouTube Standard (16:9)"},
    "9:16": {"width": 1080, "height": 1920, "label": "Shorts / Reels / TikTok (9:16)"},
    "1:1": {"width": 1080, "height": 1080, "label": "Instagram Square (1:1)"},
    "21:9": {"width": 2560, "height": 1080, "label": "Cinematic Ultrawide (21:9)"}
}

BACKGROUND_SCALING_MODES = ["Cover", "Contain", "Stretch", "Dual-Layer Blur"]

WAVEFORM_RENDER_MODES = [
    "Line Waveform",
    "Solid Bars",
    "Audio Frequency Histogram",
    "Circular Spectrum",
    "None"
]
