"""Week 1 reinforcement learning and simulation practice."""
import os
from pathlib import Path

_cache = Path(__file__).resolve().parents[1] / ".cache"
os.environ.setdefault("MPLCONFIGDIR", str(_cache / "matplotlib"))
os.environ.setdefault("HF_HOME", str(_cache / "huggingface"))
