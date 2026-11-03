"""Convert trained scikit-learn forests (model.pkl + encoders) into compact model.npz files.
Run from the backend folder after retraining any model:
    python -m ml.export_compact
"""
from __future__ import annotations
from pathlib import Path
import joblib
import numpy as np

ML_DIR = Path(__file__).resolve().parent

# model dir -> (feature encoders {feature: pkl}, target encoder pkl or None)
SPECS = {
    "feed": ({"water_quality": "water_encoder.pkl", "disease_risk": "disease_encoder.pkl"}, None),
    "mortality": ({"water_quality": "water_encoder.pkl", "disease_risk": "disease_encoder.pkl"}, "encoder.pkl"),
    "harvest": (
        {
            "water_quality": "water_encoder.pkl",
            "disease_risk": "disease_encoder.pkl",
            "mortality_risk": "mortality_encoder.pkl",
        },
        None,
    ),
    "profit": ({}, None),
    "disease": ({"water_color": "water_encoder.pkl"}, "encoder.pkl"),
}

def export(name: str) -> Path:
    model_dir = ML_DIR / name
    feature_encoders, target_encoder = SPECS[name]
    model = joblib.load(model_dir / "model.pkl")

    lefts, rights, features, thresholds, values, roots = [], [], [], [], [], []
    offset = 0
    for estimator in model.estimators_:
        tree = estimator.tree_
        left = tree.children_left.astype(np.int32)
        right = tree.children_right.astype(np.int32)
        is_leaf = left == -1
        lefts.append(np.where(is_leaf, -1, left + offset))
        rights.append(np.where(is_leaf, -1, right + offset))
        features.append(tree.feature.astype(np.int16))
        thresholds.append(tree.threshold.astype(np.float64))
        value = tree.value[:, 0, :].astype(np.float64)
        if target_encoder:
            value = value / value.sum(axis=1, keepdims=True)
        values.append(value)
        roots.append(offset)
        offset += tree.node_count

    arrays = {
        "left": np.concatenate(lefts),
        "right": np.concatenate(rights),
        "feature": np.concatenate(features),
        "threshold": np.concatenate(thresholds),
        "value": np.concatenate(values),
        "roots": np.asarray(roots, dtype=np.int32),
        "feature_names": np.asarray(list(model.feature_names_in_), dtype=str),
    }
    for feature, filename in feature_encoders.items():
        arrays[f"enc_{feature}"] = np.asarray(joblib.load(model_dir / filename).classes_, dtype=str)
    if target_encoder:
        labels = joblib.load(model_dir / target_encoder).inverse_transform(model.classes_)
        arrays["classes"] = np.asarray(labels, dtype=str)

    out = model_dir / "model.npz"
    np.savez_compressed(out, **arrays)
    print(f"{name}: {offset} nodes -> {out.name} ({out.stat().st_size / 1e6:.1f} MB)")
    return out


if __name__ == "__main__":
    for model_name in SPECS:
        export(model_name)
