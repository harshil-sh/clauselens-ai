from __future__ import annotations

import re
from pathlib import Path


def build_safe_filename(filename: str) -> str:
    source = Path(filename.replace("\\", "/")).name
    suffix = Path(source).suffix.lower()
    stem = Path(source).stem
    normalized_stem = re.sub(r"[^A-Za-z0-9._-]+", "-", stem).strip("._-")
    if not normalized_stem:
        normalized_stem = "upload"
    return f"{normalized_stem}{suffix}"
