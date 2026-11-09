"""
Load the PDF file and create the necessary images.
To add a new file format, add the necessary loader, ex. load_html, and add it to the LOADERS dictionary.
Each loader follows a simple signature:
    def load_file(path: Path, task: dict) -> list[Image.Image]:
        pass
"""

from pathlib import Path
from PIL import Image


def parse_page_range(text):
    """'1-5' -> (1, 5), '3' -> (3, 3), None -> None (all pages)."""
    if not text:
        return None
    parts = str(text).split("-")
    return int(parts[0]), int(parts[-1])


def load_pdf(path: Path, task: dict) -> list[Image.Image]:
    from pdf2image import convert_from_path
    options = {"dpi": task["input"]["dpi"]}
    page_range = parse_page_range(task["input"]["pages"])
    if page_range:
        options["first_page"], options["last_page"] = page_range
    return convert_from_path(str(path), **options)


def load_image(path: Path, task: dict) -> list[Image.Image]:
    return [Image.open(path).convert("RGB")]


LOADERS = {".pdf": load_pdf, ".png": load_image, ".jpg": load_image, ".jpeg": load_image}


def load_pages(path: Path, task: dict) -> list[Image.Image]:
    loader = LOADERS.get(path.suffix.lower())
    if loader is None:
        raise ValueError(f"No loader for {path.suffix} files")
    pages = loader(path, task)
    if not pages:
        raise RuntimeError(f"No pages loaded from {path}")
    return pages