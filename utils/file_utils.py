from __future__ import annotations

from pathlib import Path
from typing import BinaryIO

from config import Config


def ensure_runtime_dirs() -> None:
    """Create runtime data directories when they do not exist."""
    Path(Config.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
    Path(Config.OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
    Path(Config.CHROMA_PERSIST_DIR).mkdir(parents=True, exist_ok=True)


def save_uploaded_file(uploaded_file: BinaryIO, target_dir: str | None = None) -> Path:
    """Persist a Streamlit uploaded file and return the absolute path."""
    directory = Path(target_dir or Config.UPLOAD_DIR)
    directory.mkdir(parents=True, exist_ok=True)

    file_name = getattr(uploaded_file, "name", "upload.bin")
    output_path = directory / file_name

    content = uploaded_file.getbuffer() if hasattr(uploaded_file, "getbuffer") else uploaded_file.read()
    output_path.write_bytes(bytes(content))
    return output_path


def build_output_path(source_name: str, suffix: str | None = None) -> Path:
    """Build an output filename with a deterministic prefix."""
    stem = Path(source_name).stem
    ext = suffix or Path(source_name).suffix or ".out"
    output_file = f"filled_{stem}{ext}"
    output_path = Path(Config.OUTPUT_DIR) / output_file
    output_path.parent.mkdir(parents=True, exist_ok=True)
    return output_path
