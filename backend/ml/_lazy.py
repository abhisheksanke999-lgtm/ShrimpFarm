"""Load joblib/sklearn artifacts on first use (keeps Render 512MB boot under limit)."""

from __future__ import annotations

from pathlib import Path

import joblib

_cache: dict[tuple[str, str], object] = {}


def load_pkl(base_dir: Path, filename: str):
    key = (str(base_dir.resolve()), filename)
    if key not in _cache:
        _cache[key] = joblib.load(base_dir / filename)
    return _cache[key]
