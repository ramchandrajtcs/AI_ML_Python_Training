# OCR CLI

Extract text from images using Tesseract OCR via a simple Python script.

## Quick Start

1) Install system Tesseract

- macOS (Homebrew): `brew install tesseract`
- Ubuntu/Debian: `sudo apt-get update && sudo apt-get install -y tesseract-ocr`
- Windows: https://github.com/tesseract-ocr/tesseract

2) Install Python dependencies

```bash
pip install -r requirements.txt
```

3) Generate a sample image and run OCR

```bash
python scripts/generate_sample_image.py
python ocr.py samples/hello_ocr.png
```

You should see text similar to:

```
Hello OCR 123
This is a test image.
```

## Usage

```bash
python ocr.py <image_path> [options]
```

- `-l, --lang`: Language(s), e.g., `eng`, or `eng+deu`.
- `--psm`: Page Segmentation Mode (e.g., `6`).
- `--oem`: OCR Engine Mode (`0`–`3`).
- `--no-grayscale`: Disable grayscale preprocessing.
- `--no-sharpen`: Disable sharpen filter.
- `--threshold`: Binarization threshold `0–255` (omit for none).
- `-o, --output`: Write output text to a file.

Examples:

```bash
python ocr.py samples/hello_ocr.png -l eng --psm 6
python ocr.py image.jpg -o output.txt
```

If Tesseract is not on your PATH, set `TESSERACT_CMD` to its binary path.

