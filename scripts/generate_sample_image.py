"""
Generate a sample image with text for testing OCR.

Usage:
  python scripts/generate_sample_image.py

Creates: samples/hello_ocr.png
"""

from __future__ import annotations

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


def main() -> None:
    out_dir = Path("samples")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "hello_ocr.png"

    # Create a white canvas
    width, height = 900, 240
    img = Image.new("RGB", (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)

    # Use a default bitmap font to avoid external font dependencies
    font_title = ImageFont.load_default()

    # Draw text with good contrast
    draw.text((40, 60), "Hello OCR 123", fill=(0, 0, 0), font=font_title)
    draw.text((40, 120), "This is a test image.", fill=(0, 0, 0), font=font_title)

    img.save(out_path)
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()

