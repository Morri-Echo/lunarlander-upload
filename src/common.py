import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def portable_path(path):
    resolved = Path(path).resolve()
    try:
        return resolved.relative_to(ROOT).as_posix()
    except ValueError:
        return str(resolved)


def save_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False), encoding="utf-8")


def positive_int(value):
    value = int(value)
    if value <= 0:
        raise ValueError("Expected a positive integer")
    return value
