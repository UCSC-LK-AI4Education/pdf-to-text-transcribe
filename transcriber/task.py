"""
Load the task at hand from a given file in the tasks folder
"""

from pathlib import Path
import yaml

REQUIRED_KEYS = ["name", "document", "item", "fields"]

def load_task(path: Path) -> dict:
    task = yaml.safe_load(path.read_text(encoding="utf-8"))
    missing = [key for key in REQUIRED_KEYS if key not in task]
    if missing:
        raise ValueError(f"{path}: task file is missing {missing}")

    task.setdefault("input", {})
    task["input"].setdefault("pages", None)   # None = take every page from the pdf
    task["input"].setdefault("dpi", 200)
    task.setdefault("task_rules", "")
    task.setdefault("checks", [])
    return task