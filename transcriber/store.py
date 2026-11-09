"""
For storing the results
"""

import hashlib
import json
from pathlib import Path


def fingerprint(doc_path: Path, *settings: str) -> str:
    """Changes whenever the file, the prompt, the schema or the model changes."""
    h = hashlib.sha256(doc_path.read_bytes())
    for s in settings:
        h.update(s.encode("utf-8"))
    return h.hexdigest()[:16]


def load_result(result_path: Path) -> dict | None:
    if not result_path.exists():
        return None
    return json.loads(result_path.read_text(encoding="utf-8"))


def save_result(result_path: Path, record: dict):
    result_path.parent.mkdir(parents=True, exist_ok=True)
    result_path.write_text(json.dumps(record, indent=2, ensure_ascii=False), encoding="utf-8")