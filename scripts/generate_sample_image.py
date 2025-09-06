"""
Generate a sample image with text for testing OCR.

Usage:
  python scripts/generate_sample_image.py

Creates: samples/hello_ocr.png
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional
from PIL import Image, ImageDraw, ImageFont


def _find_ttf_font() -> Optional[Path]:
    """Try to locate a readable TrueType font on this system.

    Checks a list of common macOS/Linux font paths. Returns first match or None.
    """
    candidates = [
        # macOS common fonts
        "/Library/Fonts/Arial.ttf",
        "/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Supplemental/Helvetica.ttc",
        "/System/Library/Fonts/Supplemental/DejaVuSans.ttf",
        "/System/Library/Fonts/Menlo.ttc",
        # Linux common fonts
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
    ]
    for p in candidates:
        path = Path(p)
        if path.exists():
            return path
    return None


def main() -> None:
    out_dir = Path("samples")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "hello_ocr.png"

    # Create a white canvas
    width, height = 1200, 320
    img = Image.new("RGB", (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)

    # Prefer a TrueType font if available for crisper OCR; fallback to default
    font_path = _find_ttf_font()
    if font_path:
        try:
            font_title = ImageFont.truetype(str(font_path), size=64)
            font_body = ImageFont.truetype(str(font_path), size=48)
        except Exception:
            font_title = ImageFont.load_default()
            font_body = ImageFont.load_default()
    else:
        font_title = ImageFont.load_default()
        font_body = ImageFont.load_default()

    # Draw text with good contrast
    draw.text((40, 60), "Hello OCR 123", fill=(0, 0, 0), font=font_title)
    draw.text((40, 160), "This is a test image.", fill=(0, 0, 0), font=font_body)

    img.save(out_path)
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
