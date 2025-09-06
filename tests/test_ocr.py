import os
import shutil
from pathlib import Path

import pytest
import importlib.util


def _load_ocr_module():
    ocr_path = Path(__file__).resolve().parent.parent / "ocr.py"
    spec = importlib.util.spec_from_file_location("ocr", ocr_path)
    assert spec and spec.loader, "Failed to create import spec for ocr.py"
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[attr-defined]
    return module


@pytest.mark.skipif(shutil.which("tesseract") is None, reason="Tesseract binary not found")
def test_ocr_on_generated_sample(tmp_path: Path) -> None:
    # Generate sample image using the script (importing the file keeps deps minimal)
    samples_dir = Path("samples")
    image_path = samples_dir / "hello_ocr.png"

    # If the sample does not exist, create it by executing the generator script
    if not image_path.exists():
        import runpy

        runpy.run_path(str(Path("scripts") / "generate_sample_image.py"), run_name="__main__")
        assert image_path.exists(), "Sample image was not generated"

    ocr = _load_ocr_module()
    text = ocr.ocr_image(
        image_path,
        lang="eng",
        psm=6,
        threshold=None,
        grayscale=True,
        sharpen=True,
        denoise="median",
        deskew=True,
    )

    # Normalize whitespace for robust assertions
    norm = " ".join(text.split())
    assert "Hello OCR 123" in norm
    assert "This is a test image." in norm
