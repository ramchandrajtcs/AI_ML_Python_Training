"""
Simple OCR CLI: extract text from images using Tesseract OCR.

Usage examples:
  - Basic:      python ocr.py image.jpg
  - Language:   python ocr.py image.jpg -l eng
  - PSM mode:   python ocr.py image.jpg --psm 6
  - To file:    python ocr.py image.jpg -o output.txt

Dependencies:
  - Python packages: Pillow, pytesseract
  - System binary: Tesseract OCR (required at runtime)

Install Tesseract:
  - macOS (Homebrew):   brew install tesseract
  - Ubuntu/Debian:      sudo apt-get update && sudo apt-get install -y tesseract-ocr
  - Windows:            https://github.com/tesseract-ocr/tesseract

After installing Tesseract, ensure it's on your PATH or set
the Tesseract command path via the environment variable TESSERACT_CMD.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import Optional

from PIL import Image, ImageOps, ImageFilter

try:
    import pytesseract
except Exception as e:  # pragma: no cover
    print(
        "Error: pytesseract not installed. Add 'pytesseract' to requirements and pip install.",
        file=sys.stderr,
    )
    raise


def _ensure_tesseract_available() -> None:
    try:
        _ = pytesseract.get_tesseract_version()
    except Exception as exc:
        msg = (
            "Tesseract OCR not found.\n"
            "Install it and ensure it's on PATH, e.g.:\n"
            "  - macOS:  brew install tesseract\n"
            "  - Ubuntu: sudo apt-get install -y tesseract-ocr\n"
            "Or set environment variable 'TESSERACT_CMD' to the binary path.\n"
            f"Original error: {exc}"
        )
        raise RuntimeError(msg) from exc


def load_image(path: Path) -> Image.Image:
    with Image.open(path) as im:
        return im.convert("RGB")


def preprocess_image(
    img: Image.Image,
    grayscale: bool = True,
    sharpen: bool = True,
    threshold: Optional[int] = None,
    denoise: Optional[str] = None,
) -> Image.Image:
    if grayscale:
        img = ImageOps.grayscale(img)
    if sharpen:
        img = img.filter(ImageFilter.SHARPEN)
    if denoise:
        if denoise == "median":
            img = img.filter(ImageFilter.MedianFilter(size=3))
        elif denoise == "blur":
            img = img.filter(ImageFilter.GaussianBlur(radius=0.8))
    if threshold is not None:
        threshold = max(0, min(255, threshold))
        img = img.point(lambda p: 255 if p > threshold else 0)
    return img


def _deskew_with_tesseract(img: Image.Image) -> Image.Image:
    """Estimate rotation via Tesseract OSD and rotate to deskew.

    Falls back to original image on failure.
    """
    try:
        osd = pytesseract.image_to_osd(img)
        # OSD output often contains a line like: "Rotate: 90"
        angle = None
        for line in osd.splitlines():
            if "Rotate:" in line:
                try:
                    angle = int(line.split(":", 1)[1].strip())
                except Exception:
                    pass
                break
        if angle is not None and angle % 360 != 0:
            # Rotate in opposite direction to deskew
            return img.rotate(-angle, expand=True, fillcolor=255)
    except Exception:
        pass
    return img


def ocr_image(
    image_path: Path,
    lang: str = "eng",
    psm: Optional[int] = None,
    oem: Optional[int] = None,
    threshold: Optional[int] = None,
    grayscale: bool = True,
    sharpen: bool = True,
    denoise: Optional[str] = None,
    deskew: bool = False,
) -> str:
    _ensure_tesseract_available()
    img = load_image(image_path)
    if deskew:
        img = _deskew_with_tesseract(img)
    img = preprocess_image(
        img,
        grayscale=grayscale,
        sharpen=sharpen,
        threshold=threshold,
        denoise=denoise,
    )

    config_parts = []
    if psm is not None:
        config_parts.append(f"--psm {psm}")
    if oem is not None:
        config_parts.append(f"--oem {oem}")
    config = " ".join(config_parts) if config_parts else None

    return pytesseract.image_to_string(img, lang=lang, config=config)


def parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Extract text from an image using Tesseract OCR.")
    p.add_argument("image", type=Path, help="Path to the input image file")
    p.add_argument("-l", "--lang", default="eng", help="Language(s), e.g., 'eng', 'eng+deu'")
    p.add_argument("--psm", type=int, default=None, help="Tesseract Page Segmentation Mode (e.g., 6)")
    p.add_argument("--oem", type=int, default=None, help="Tesseract OCR Engine Mode (0-3)")
    p.add_argument("--no-grayscale", action="store_true", help="Disable grayscale preprocessing")
    p.add_argument("--no-sharpen", action="store_true", help="Disable sharpen filter")
    p.add_argument(
        "--threshold",
        type=int,
        default=None,
        help="Binarization threshold 0-255 (omit for auto/none)",
    )
    p.add_argument(
        "--denoise",
        choices=["median", "blur"],
        default=None,
        help="Optional denoise filter before thresholding",
    )
    p.add_argument(
        "--deskew",
        action="store_true",
        help="Auto-rotate using Tesseract OSD to correct skew",
    )
    p.add_argument("-o", "--output", type=Path, default=None, help="Optional output .txt path")
    return p.parse_args(argv)


def main(argv: Optional[list[str]] = None) -> int:
    args = parse_args(argv or sys.argv[1:])

    if not args.image.exists():
        print(f"Error: File not found: {args.image}", file=sys.stderr)
        return 2

    try:
        text = ocr_image(
            args.image,
            lang=args.lang,
            psm=args.psm,
            oem=args.oem,
            threshold=args.threshold,
            grayscale=not args.no_grayscale,
            sharpen=not args.no_sharpen,
            denoise=args.denoise,
            deskew=args.deskew,
        )
    except Exception as exc:
        print(f"OCR failed: {exc}", file=sys.stderr)
        return 1

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
        print(f"Wrote: {args.output}")
    else:
        # Print to stdout
        sys.stdout.write(text)

    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
