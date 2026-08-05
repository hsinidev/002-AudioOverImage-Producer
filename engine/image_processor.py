import os
from PIL import Image, ImageFilter, ImageOps, ImageDraw
from typing import Tuple, Dict, Any, Optional
from utils.helpers import hex_to_rgb
from utils.logger import get_logger

logger = get_logger()

class ImageProcessor:
    """High-performance Pillow image compositor supporting 4 scaling modes."""

    @staticmethod
    def process_background(
        image_path: Optional[str],
        target_w: int,
        target_h: int,
        mode: str = "Cover",
        pad_color_hex: str = "#0A0E14",
        blur_radius: float = 30.0
    ) -> Image.Image:
        """
        Process or generate background image matching target dimensions (target_w, target_h).
        Modes: 'Cover', 'Contain', 'Stretch', 'Dual-Layer Blur'
        """
        # If no image path provided or invalid, generate solid canvas with gradient
        if not image_path or not os.path.isfile(image_path):
            return ImageProcessor._create_default_gradient_canvas(target_w, target_h, pad_color_hex)

        try:
            with Image.open(image_path) as img:
                img = img.convert("RGBA")
                
                if mode == "Cover":
                    # Crop to fill container exactly while preserving aspect ratio
                    return ImageOps.fit(img, (target_w, target_h), method=Image.Resampling.LANCZOS)

                elif mode == "Contain":
                    # Aspect fit inside target_w x target_h, padded with pad_color_hex
                    canvas = Image.new("RGBA", (target_w, target_h), hex_to_rgb(pad_color_hex) + (255,))
                    img_ratio = img.width / img.height
                    target_ratio = target_w / target_h

                    if img_ratio > target_ratio:
                        w = target_w
                        h = int(round(w / img_ratio))
                    else:
                        h = target_h
                        w = int(round(h * img_ratio))

                    resized = img.resize((max(1, w), max(1, h)), Image.Resampling.LANCZOS)
                    x = (target_w - w) // 2
                    y = (target_h - h) // 2
                    canvas.paste(resized, (x, y), resized if resized.mode == "RGBA" else None)
                    return canvas

                elif mode == "Stretch":
                    # Direct resize
                    return img.resize((target_w, target_h), Image.Resampling.LANCZOS)

                elif mode == "Dual-Layer Blur":
                    # Layer 1: Heavily blurred stretched background
                    bg_layer = img.resize((target_w, target_h), Image.Resampling.LANCZOS)
                    bg_layer = bg_layer.filter(ImageFilter.GaussianBlur(radius=blur_radius))
                    
                    # Optional subtle dark tint over blurred background for contrast
                    dark_overlay = Image.new("RGBA", (target_w, target_h), (0, 0, 0, 80))
                    bg_layer = Image.alpha_composite(bg_layer, dark_overlay)

                    # Layer 2: Aspect-fitted foreground image
                    img_ratio = img.width / img.height
                    target_ratio = target_w / target_h

                    if img_ratio > target_ratio:
                        w = target_w
                        h = int(round(w / img_ratio))
                    else:
                        h = target_h
                        w = int(round(h * img_ratio))

                    fg_layer = img.resize((max(1, w), max(1, h)), Image.Resampling.LANCZOS)
                    x = (target_w - w) // 2
                    y = (target_h - h) // 2

                    bg_layer.paste(fg_layer, (x, y), fg_layer if fg_layer.mode == "RGBA" else None)
                    return bg_layer

                else:
                    # Default Fallback to Cover
                    return ImageOps.fit(img, (target_w, target_h), method=Image.Resampling.LANCZOS)

        except Exception as e:
            logger.error(f"Error processing background image ({image_path}): {e}")
            return ImageProcessor._create_default_gradient_canvas(target_w, target_h, pad_color_hex)

    @staticmethod
    def _create_default_gradient_canvas(width: int, height: int, hex_bg: str = "#0A0E14") -> Image.Image:
        """Generate a sleek Studio Emerald dark gradient background image when no file is supplied."""
        base_rgb = hex_to_rgb(hex_bg)
        accent_rgb = (0, 230, 118) # Neon Emerald
        secondary_rgb = (19, 27, 38) # Dark Secondary

        img = Image.new("RGBA", (width, height), base_rgb + (255,))
        draw = ImageDraw.Draw(img)

        # Subtle vertical linear gradient
        for y in range(height):
            ratio = y / max(1, height)
            r = int(base_rgb[0] * (1 - ratio) + secondary_rgb[0] * ratio)
            g = int(base_rgb[1] * (1 - ratio) + secondary_rgb[1] * ratio)
            b = int(base_rgb[2] * (1 - ratio) + secondary_rgb[2] * ratio)
            draw.line([(0, y), (width, y)], fill=(r, g, b, 255))

        # Add decorative dark studio grid pattern
        grid_step = max(40, width // 20)
        grid_color = (0, 230, 118, 15) # Subtle emerald transparent grid
        grid_img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        grid_draw = ImageDraw.Draw(grid_img)
        
        for x in range(0, width, grid_step):
            grid_draw.line([(x, 0), (x, height)], fill=grid_color, width=1)
        for y in range(0, height, grid_step):
            grid_draw.line([(0, y), (width, y)], fill=grid_color, width=1)

        img = Image.alpha_composite(img, grid_img)
        return img
