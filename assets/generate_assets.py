import os
from PIL import Image, ImageDraw

def generate_assets():
    assets_dir = os.path.join(os.path.dirname(__file__))
    os.makedirs(assets_dir, exist_ok=True)

    # 1. Create icon.ico (256x256 modern emerald studio icon)
    icon_size = (256, 256)
    icon_img = Image.new("RGBA", icon_size, (10, 14, 20, 255))
    draw = ImageDraw.Draw(icon_img)

    # Draw neon emerald play circle & waveform bars
    center_x, center_y = 128, 128
    radius = 100
    draw.ellipse(
        [center_x - radius, center_y - radius, center_x + radius, center_y + radius],
        outline=(0, 230, 118, 255), width=8
    )

    # Draw synthetic waveform bars inside icon
    bar_heights = [30, 55, 85, 45, 95, 65, 35]
    start_x = 78
    for i, h in enumerate(bar_heights):
        x = start_x + (i * 15)
        draw.rectangle([x, center_y - (h // 2), x + 8, center_y + (h // 2)], fill=(29, 233, 182, 255))

    icon_path = os.path.join(assets_dir, "icon.ico")
    icon_img.save(icon_path, format="ICO", sizes=[(256, 256), (64, 64), (32, 32), (16, 16)])
    print(f"Generated asset icon: {icon_path}")

    # 2. Create sample_bg.png (1920x1080)
    bg_img = Image.new("RGBA", (1920, 1080), (10, 14, 20, 255))
    bg_draw = ImageDraw.Draw(bg_img)
    for y in range(1080):
        ratio = y / 1080.0
        r = int(10 * (1 - ratio) + 19 * ratio)
        g = int(14 * (1 - ratio) + 27 * ratio)
        b = int(20 * (1 - ratio) + 38 * ratio)
        bg_draw.line([(0, y), (1920, y)], fill=(r, g, b, 255))

    bg_path = os.path.join(assets_dir, "sample_bg.png")
    bg_img.save(bg_path, format="PNG")
    print(f"Generated sample background: {bg_path}")

if __name__ == "__main__":
    generate_assets()
