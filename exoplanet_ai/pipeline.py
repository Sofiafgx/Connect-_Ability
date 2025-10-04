from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import classification_report, f1_score
from sklearn.model_selection import StratifiedKFold, train_test_split
from sklearn.pipeline import Pipeline

from .physics import (
    compute_semi_major_axis_au,
    compute_impact_parameter,
    estimate_planet_radius_earth,
)


FEATURE_COLUMNS_BASE = [
    "orbital_period_days",
    "transit_depth_fraction",
    "transit_duration_hours",
    "stellar_radius_solar",
    "stellar_mass_solar",
    "stellar_temperature_k",
    "snr",
    "stellar_magnitude",
]


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()

    # Derived geometric/physical features
    out["a_au"] = df.apply(
        lambda r: compute_semi_major_axis_au(r["orbital_period_days"], r["stellar_mass_solar"]),
        axis=1,
    )
    out["impact_parameter"] = df.apply(
        lambda r: compute_impact_parameter(
            r["orbital_period_days"],
            r["transit_duration_hours"],
            r["transit_depth_fraction"],
            r["stellar_radius_solar"],
            r["stellar_mass_solar"],
        ),
        axis=1,
    )
    out["planet_radius_earth"] = df.apply(
        lambda r: estimate_planet_radius_earth(r["transit_depth_fraction"], r["stellar_radius_solar"]),
        axis=1,
    )
    # Stellar density proxy (solar units). Avoid div by zero
    out["stellar_density_solar"] = out["stellar_mass_solar"] / (out["stellar_radius_solar"] ** 3)

    # Replace inf/nan from any numeric mishaps
    out = out.replace([np.inf, -np.inf], np.nan)

    return out


def build_model_pipeline(feature_names: List[str]) -> Pipeline:
    numeric_transformer = SimpleImputer(strategy="median")

    preprocessor = ColumnTransformer(
        transformers=[("num", numeric_transformer, feature_names)],
        remainder="drop",
    )

    model = HistGradientBoostingClassifier(
        loss="log_loss",
        learning_rate=0.06,
        max_depth=None,
        max_iter=600,
        min_samples_leaf=25,
        l2_regularization=0.0,
        random_state=42,
        early_stopping=True,
        validation_fraction=0.1,
        n_iter_no_change=20,
    )

    pipe = Pipeline(steps=[("pre", preprocessor), ("clf", model)])
    return pipe


def compute_class_weights(y: pd.Series) -> Dict[str, float]:
    values, counts = np.unique(y, return_counts=True)
    total = counts.sum()
    weights = {v: total / (len(values) * c) for v, c in zip(values, counts)}
    return weights


def train_evaluate(df: pd.DataFrame) -> Tuple[Pipeline, Dict[str, float], Dict[str, float], List[str]]:
    df = engineer_features(df)

    # Feature set
    feature_names = FEATURE_COLUMNS_BASE + [
        "a_au",
        "impact_parameter",
        "planet_radius_earth",
        "stellar_density_solar",
    ]

    X = df[feature_names]
    y = df["label"].astype(str)

    # Train/val/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    pipe = build_model_pipeline(feature_names)

    # Sample weights for imbalance
    cw = compute_class_weights(y_train)
    sample_weight = y_train.map(cw).to_numpy()

    pipe.fit(X_train, y_train, clf__sample_weight=sample_weight)

    y_pred = pipe.predict(X_test)
    report = classification_report(y_test, y_pred, output_dict=True, zero_division=0)

    # Macro F1 is a robust overall summary for imbalanced data
    macro_f1 = f1_score(y_test, y_pred, average="macro")

    metrics = {
        "macro_f1": float(macro_f1),
        "per_class_f1": {k: float(v.get("f1-score", 0.0)) for k, v in report.items() if k in set(y.unique())},
        "support": {k: int(v.get("support", 0)) for k, v in report.items() if k in set(y.unique())},
    }

    return pipe, metrics, cw, feature_names
