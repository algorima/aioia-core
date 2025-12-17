from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from PIL import Image


@dataclass
class ProcessedImage:
    path: Path
    width: int
    height: int


def load_and_normalize(image_path: Path, max_side: int = 1400) -> Image.Image:
    img = Image.open(image_path).convert("RGB")
    w, h = img.size
    scale = min(1.0, max_side / max(w, h))
    if scale < 1.0:
        img = img.resize((int(w * scale), int(h * scale)))
    return img


def save_normalized(img: Image.Image, out_path: Path) -> ProcessedImage:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path, format="JPEG", quality=92)
    w, h = img.size
    return ProcessedImage(path=out_path, width=w, height=h)


def maybe_ocr_text(image_path: Path) -> str:
    """
    Optional OCR hook.

    - If pytesseract is installed, this will try OCR.
    - Otherwise returns empty string (skeleton-friendly).

    For higher quality, consider:
      - easyocr (GPU)
      - a dedicated OCR microservice
    """
    try:
        import pytesseract  # type: ignore
    except Exception:
        return ""

    try:
        img = Image.open(image_path).convert("RGB")
        text = pytesseract.image_to_string(img, lang="eng+kor")
        return (text or "").strip()
    except Exception:
        return ""
