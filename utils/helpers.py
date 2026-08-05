import os
import re
from typing import Tuple, Dict, Any

def format_seconds_to_timecode(seconds: float) -> str:
    """Format floating seconds into HH:MM:SS.mmm string."""
    if seconds < 0:
        seconds = 0
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int(round((seconds - int(seconds)) * 1000))
    if millis >= 1000:
        secs += 1
        millis -= 1000
    return f"{hrs:02d}:{mins:02d}:{secs:02d}.{millis:03d}"

def format_bytes_to_human(bytes_num: int) -> str:
    """Format raw byte counts to human readable KB/MB/GB string."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if abs(bytes_num) < 1024.0:
            return f"{bytes_num:3.1f} {unit}"
        bytes_num /= 1024.0
    return f"{bytes_num:.1f} TB"

def sanitize_filepath(path: str) -> str:
    """Normalize path separators and resolve absolute paths."""
    if not path:
        return ""
    normalized = os.path.abspath(path.strip().strip('"').strip("'"))
    return normalized

def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    """Convert hex string (e.g. #00E676) to RGB tuple (0-255)."""
    hex_color = hex_color.lstrip("#")
    if len(hex_color) == 3:
        hex_color = "".join([c * 2 for c in hex_color])
    if len(hex_color) != 6:
        return (0, 230, 118) # Default emerald
    return int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)

def rgb_to_hex(rgb: Tuple[int, int, int]) -> str:
    """Convert RGB tuple (0-255) to hex string."""
    return f"#{rgb[0]:02X}{rgb[1]:02X}{rgb[2]:02X}"

def calculate_aspect_fit_bounds(
    src_width: int, 
    src_height: int, 
    container_width: int, 
    container_height: int
) -> Tuple[int, int, int, int]:
    """
    Calculate (x, y, w, h) to fit src aspect ratio inside container bounds centered.
    """
    if src_width <= 0 or src_height <= 0 or container_width <= 0 or container_height <= 0:
        return 0, 0, container_width, container_height

    src_aspect = src_width / src_height
    container_aspect = container_width / container_height

    if src_aspect > container_aspect:
        # Width constrained
        w = container_width
        h = int(round(w / src_aspect))
        x = 0
        y = (container_height - h) // 2
    else:
        # Height constrained
        h = container_height
        w = int(round(h * src_aspect))
        x = (container_width - w) // 2
        y = 0

    return x, y, w, h
