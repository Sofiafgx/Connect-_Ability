from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from typing import Any, Dict

import joblib

from .data import DatasetPaths, load_kepler_training_frame
from .pipeline import train_evaluate


@dataclass
class ModelBundle:
    feature_names: list[str]
    class_weights: dict[str, float]
    metrics: dict[str, Any]


def main() -> None:
    paths = DatasetPaths()
    os.makedirs("models", exist_ok=True)

    df = load_kepler_training_frame(paths)

    pipeline, metrics, class_weights, feature_names = train_evaluate(df)

    # Persist model and metadata
    joblib.dump(pipeline, os.path.join("models", "model.joblib"))
    bundle = ModelBundle(
        feature_names=feature_names,
        class_weights=class_weights,
        metrics=metrics,
    )
    with open(os.path.join("models", "model_meta.json"), "w", encoding="utf-8") as f:
        json.dump(asdict(bundle), f, indent=2)

    print("Saved model to models/model.joblib")
    print("Metrics:")
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
