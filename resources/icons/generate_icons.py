#!/usr/bin/env python3
"""Generate icon files from SVG - pure PIL version (no cairosvg dependency)."""

import io
from pathlib import Path

try:
    from PIL import Image, ImageDraw
except ImportError:
    print("Installing required packages...")
    import subprocess
    subprocess.check_call(["pip", "install", "pillow"])
    from PIL import Image, ImageDraw


def draw_duck_icon(draw: ImageDraw.ImageDraw, size: int):
    """Draw the duck with crosshair icon at the given size."""
    cx = size // 2
    cy = size // 2
    scale = size / 256.0  # SVG was 256x256

    # Colors
    GREEN_BG = (76, 175, 80, 38)      # #4CAF50 with 0.15 opacity
    YELLOW_BODY = (255, 215, 0)       # #FFD700
    LIGHT_YELLOW = (255, 224, 102)    # #FFE066
    ORANGE_BILL = (255, 140, 0)       # #FF8C00
    LIGHT_ORANGE = (255, 159, 28)     # #FF9F1C
    DARK_ORANGE = (204, 102, 0)       # #CC6600
    DARK_GRAY = (45, 45, 45)          # #2D2D2D
    WHITE = (255, 255, 255)
    AMBER = (255, 193, 7)             # #FFC107

    # Background circle
    r_bg = int(120 * scale)
    draw.ellipse(
        [cx - r_bg, cy - r_bg, cx + r_bg, cy + r_bg],
        fill=GREEN_BG
    )

    # Duck body
    rx_body = int(60 * scale)
    ry_body = int(50 * scale)
    body_cy = cy + int(22 * scale)
    draw.ellipse(
        [cx - rx_body, body_cy - ry_body, cx + rx_body, body_cy + ry_body],
        fill=YELLOW_BODY
    )
    rx_body2 = int(58 * scale)
    ry_body2 = int(48 * scale)
    draw.ellipse(
        [cx - rx_body2, body_cy - ry_body2, cx + rx_body2, body_cy + ry_body2],
        fill=LIGHT_YELLOW
    )

    # Duck head
    head_cx = cx + int(47 * scale)
    head_cy = cy - int(40 * scale)
    r_head = int(35 * scale)
    draw.ellipse(
        [head_cx - r_head, head_cy - r_head, head_cx + r_head, head_cy + r_head],
        fill=YELLOW_BODY
    )
    r_head2 = int(33 * scale)
    draw.ellipse(
        [head_cx - r_head2, head_cy - r_head2, head_cx + r_head2, head_cy + r_head2],
        fill=LIGHT_YELLOW
    )

    # Duck bill
    bill_cx = head_cx + int(25 * scale)
    bill_cy = head_cy
    rx_bill = int(20 * scale)
    ry_bill = int(12 * scale)
    draw.ellipse(
        [bill_cx - rx_bill, bill_cy - ry_bill, bill_cx + rx_bill, bill_cy + ry_bill],
        fill=ORANGE_BILL
    )
    rx_bill2 = int(18 * scale)
    ry_bill2 = int(10 * scale)
    draw.ellipse(
        [bill_cx - rx_bill2, bill_cy - ry_bill2, bill_cx + rx_bill2, bill_cy + ry_bill2],
        fill=LIGHT_ORANGE
    )

    # Nostril
    nostril_cx = bill_cx + int(5 * scale)
    nostril_cy = bill_cy - int(2 * scale)
    r_nostril = max(1, int(2 * scale))
    draw.ellipse(
        [nostril_cx - r_nostril, nostril_cy - r_nostril,
         nostril_cx + r_nostril, nostril_cy + r_nostril],
        fill=DARK_ORANGE
    )

    # Eye
    eye_cx = head_cx - int(10 * scale)
    eye_cy = head_cy - int(10 * scale)
    r_eye = max(1, int(8 * scale))
    draw.ellipse(
        [eye_cx - r_eye, eye_cy - r_eye, eye_cx + r_eye, eye_cy + r_eye],
        fill=DARK_GRAY
    )
    # Eye highlight
    hl_cx = eye_cx + int(2 * scale)
    hl_cy = eye_cy - int(2 * scale)
    r_hl = max(1, int(3 * scale))
    draw.ellipse(
        [hl_cx - r_hl, hl_cy - r_hl, hl_cx + r_hl, hl_cy + r_hl],
        fill=WHITE
    )

    # Wing
    wing_cx = cx
    wing_cy = body_cy - int(5 * scale)
    rx_wing = int(40 * scale)
    ry_wing = int(30 * scale)
    draw.ellipse(
        [wing_cx - rx_wing, wing_cy - ry_wing, wing_cx + rx_wing, wing_cy + ry_wing],
        fill=AMBER
    )
    rx_wing2 = int(35 * scale)
    ry_wing2 = int(25 * scale)
    draw.ellipse(
        [wing_cx - rx_wing2, wing_cy - ry_wing2, wing_cx + rx_wing2, wing_cy + ry_wing2],
        fill=YELLOW_BODY
    )

    # Crosshair overlay on duck
    crosshair_cx = cx
    crosshair_cy = body_cy
    line_width = max(1, int(3 * scale))

    # Horizontal line
    x1 = crosshair_cx - int(48 * scale)
    x2 = crosshair_cx - int(18 * scale)
    draw.line([x1, crosshair_cy, x2, crosshair_cy], fill=DARK_GRAY, width=line_width)

    x3 = crosshair_cx + int(18 * scale)
    x4 = crosshair_cx + int(48 * scale)
    draw.line([x3, crosshair_cy, x4, crosshair_cy], fill=DARK_GRAY, width=line_width)

    # Vertical line
    y1 = crosshair_cy - int(40 * scale)
    y2 = crosshair_cy - int(70 * scale)
    draw.line([crosshair_cx, y1, crosshair_cx, y2], fill=DARK_GRAY, width=line_width)

    y3 = crosshair_cy + int(30 * scale)
    y4 = crosshair_cy + int(60 * scale)
    draw.line([crosshair_cx, y3, crosshair_cx, y4], fill=DARK_GRAY, width=line_width)

    # Center dot
    r_dot = max(1, int(4 * scale))
    draw.ellipse(
        [crosshair_cx - r_dot, crosshair_cy - r_dot,
         crosshair_cx + r_dot, crosshair_cy + r_dot],
        fill=DARK_GRAY
    )

    # Duck feet
    foot1_cx = cx - int(23 * scale)
    foot1_cy = body_cy + int(45 * scale)
    rx_foot = int(12 * scale)
    ry_foot = int(6 * scale)
    # Simple ellipse for feet (no rotation in PIL basic)
    draw.ellipse(
        [foot1_cx - rx_foot, foot1_cy - ry_foot,
         foot1_cx + rx_foot, foot1_cy + ry_foot],
        fill=ORANGE_BILL
    )

    foot2_cx = cx + int(22 * scale)
    foot2_cy = body_cy + int(45 * scale)
    draw.ellipse(
        [foot2_cx - rx_foot, foot2_cy - ry_foot,
         foot2_cx + rx_foot, foot2_cy + ry_foot],
        fill=ORANGE_BILL
    )


def generate_icons():
    """Generate ICO and PNG icons from SVG."""
    icons_dir = Path(__file__).parent
    ico_path = icons_dir / "duck_icon.ico"
    png_path = icons_dir / "duck_icon.png"

    # Generate PNG at 256x256 (main size)
    size = 256
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw_duck_icon(draw, size)

    # Save main PNG
    img.save(png_path)
    print(f"Generated {png_path}")

    # Generate ICO with multiple sizes
    sizes = [16, 24, 32, 48, 64, 128, 256]
    ico_images = []
    for s in sizes:
        ico_img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
        ico_draw = ImageDraw.Draw(ico_img)
        draw_duck_icon(ico_draw, s)
        ico_images.append(ico_img)

    ico_images[0].save(
        ico_path,
        format='ICO',
        sizes=[(s, s) for s in sizes],
        append_images=ico_images[1:]
    )
    print(f"Generated {ico_path}")


if __name__ == "__main__":
    generate_icons()
