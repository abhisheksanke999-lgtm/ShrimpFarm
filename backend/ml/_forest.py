"""RandomForest inference from compact .npz exports.

Runtime never imports scikit-learn/scipy/joblib, which keeps the Render
512MB instance well under its memory limit. Create the .npz files with
``python -m ml.export_compact`` after retraining.
"""

from __future__ import annotations
from pathlib import Path
import numpy as np

_cache: dict[str, "CompactForest"] = {}


class CompactForest:
    def __init__(self, path: Path):
        with np.load(path, allow_pickle=False) as data:
            self.left = data["left"]
            self.right = data["right"]
            self.feature = data["feature"]
            self.threshold = data["threshold"]
            self.value = data["value"]
            self.roots = data["roots"]
            self.feature_names = [str(n) for n in data["feature_names"]]
            self.classes = (
                [str(c) for c in data["classes"]] if "classes" in data.files else None
            )
            self.encoders = {
                key[len("enc_"):]: [str(c) for c in data[key]]
                for key in data.files
                if key.startswith("enc_")
            }

    def encode(self, encoder: str, label: str) -> int:
        classes = self.encoders[encoder]
        try:
            return classes.index(label)
        except ValueError:
            raise ValueError(
                f"Unknown {encoder} '{label}'. Allowed: {', '.join(classes)}"
            ) from None

    def _mean_leaf_value(self, row) -> np.ndarray:
        # scikit-learn compares float32 inputs against float64 thresholds
        x = np.asarray(row, dtype=np.float32).ravel()
        left, right, feature, threshold = self.left, self.right, self.feature, self.threshold
        total = np.zeros(self.value.shape[1], dtype=np.float64)
        for node in self.roots:
            while left[node] != -1:
                node = left[node] if x[feature[node]] <= threshold[node] else right[node]
            total += self.value[node]
        return total / len(self.roots)

    def predict_value(self, row) -> float:
        return float(self._mean_leaf_value(row)[0])

    def predict_proba(self, row) -> np.ndarray:
        return self._mean_leaf_value(row)

    def predict_class(self, row) -> tuple[str, float]:
        proba = self.predict_proba(row)
        best = int(np.argmax(proba))
        return self.classes[best], float(proba[best])


def load_forest(base_dir: Path, filename: str = "model.npz") -> CompactForest:
    key = str((base_dir / filename).resolve())
    if key not in _cache:
        _cache[key] = CompactForest(base_dir / filename)
    return _cache[key]
