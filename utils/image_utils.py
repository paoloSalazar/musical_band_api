"""
Image utilities for PDF generation.

Provides function to convert image files to base64 data URIs.
"""

import base64
from pathlib import Path


def image_to_base64(image_path: str) -> str:
    """Convert a local image file to a base64 data URI."""
    path = Path(image_path)
    mime_types = {".png": "image/png", ".jpg": "image/jpeg", ".svg": "image/svg+xml"}
    mime = mime_types.get(path.suffix.lower(), "image/png")
    encoded = base64.b64encode(path.read_bytes()).decode("utf-8")
    return f"data:{mime};base64,{encoded}"