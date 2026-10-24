from __future__ import annotations

import argparse
import json
import os
from typing import Any, Dict

import joblib
import numpy as np
import pandas as pd

from .physics import (
    compute_semi_major_axis_au,
    compute_impact_parameter,
    estimate_planet_radius_earth,
    estimate_equilibrium_temperature_k,
)


DEFAULT_MODEL_PATH = os.path.join("models", "model.joblib")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Predict exoplanet disposition and physical estimates from tabular features",
    )

    p.add_argument("--model", type=str, default=DEFAULT_MODEL_PATH, help="Path to trained model.joblib")

    p.add_argument("--orbital_period", type=float, required=False, help="Orbital period in days")
    p.add_argument("--transit_depth", type=float, required=False, help="Transit depth; fractional (e.g., 0.01) or ppm if --depth_ppm")
    p.add_argument("--depth_ppm", action="store_true", help="Interpret transit depth as ppm (default: fractional)")
    p.add_argument("--transit_duration", type=float, required=False, help="Transit duration in hours")
    p.add_argument("--stellar_radius", type=float, required=False, help="Stellar radius in solar radii")
    p.add_argument("--stellar_mass", type=float, required=False, help="Stellar mass in solar masses")
    p.add_argument("--stellar_temp", type=float, required=False, help="Stellar effective temperature in K")
    p.add_argument("--snr", type=float, required=False, help="Signal-to-noise ratio of detection")
    p.add_argument("--stellar_magnitude", type=float, required=False, help="Stellar magnitude (Kepler/TESS mag)")

    return p.parse_args()


def prompt_if_missing(args: argparse.Namespace) -> Dict[str, float]:
    def get(name: str, prompt: str) -> float:
        val = getattr(args, name)
        if val is None or (isinstance(val, float) and np.isnan(val)):
            while True:
                try:
                    return float(input(prompt))
                except Exception:
                    print("Please enter a number.")
        return float(val)

    depth = args.transit_depth
    if depth is None:
        raw = float(input("Transit depth (fraction, e.g., 0.01) or ppm if you will set depth_ppm later: "))
        depth = raw

    if args.depth_ppm:
        transit_depth_fraction = depth / 1_000_000.0
    else:
        transit_depth_fraction = depth

    values = {
        "orbital_period_days": get("orbital_period", "Orbital period (days): "),
        "transit_depth_fraction": transit_depth_fraction,
        "transit_duration_hours": get("transit_duration", "Transit duration (hours): "),
        "stellar_radius_solar": get("stellar_radius", "Stellar radius (R_sun): "),
        "stellar_mass_solar": get("stellar_mass", "Stellar mass (M_sun): "),
        "stellar_temperature_k": get("stellar_temp", "Stellar effective temperature (K): "),
        "snr": get("snr", "Detection SNR: "),
        "stellar_magnitude": get("stellar_magnitude", "Stellar magnitude: "),
    }
    return values


def load_model(path: str):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Model not found at {path}. Train it first via: python -m exoplanet_ai.train")
    return joblib.load(path)


def main() -> None:
    args = parse_args()
    model = load_model(args.model)

    input_values = prompt_if_missing(args)

    # Derived physics
    a_au = compute_semi_major_axis_au(
        input_values["orbital_period_days"], input_values["stellar_mass_solar"]
    )
    impact_b = compute_impact_parameter(
        input_values["orbital_period_days"],
        input_values["transit_duration_hours"],
        input_values["transit_depth_fraction"],
        input_values["stellar_radius_solar"],
        input_values["stellar_mass_solar"],
    )
    r_earth = estimate_planet_radius_earth(
        input_values["transit_depth_fraction"], input_values["stellar_radius_solar"]
    )

    t_eq = estimate_equilibrium_temperature_k(
        input_values["stellar_temperature_k"], input_values["stellar_radius_solar"], a_au
    )

    # Build feature vector as training did
    feature_row = {
        **input_values,
        "a_au": a_au,
        "impact_parameter": impact_b,
        "planet_radius_earth": r_earth,
        "stellar_density_solar": input_values["stellar_mass_solar"]
        / (input_values["stellar_radius_solar"] ** 3),
    }

    X = pd.DataFrame([feature_row])

    proba = None
    if hasattr(model, "predict_proba"):
        proba = model.predict_proba(X)[0]
        classes = list(model.classes_)
        best_idx = int(np.argmax(proba))
        label = str(classes[best_idx])
        confidence = float(proba[best_idx])
    else:
        label = str(model.predict(X)[0])
        confidence = float("nan")

    result: Dict[str, Any] = {
        "prediction": label,
        "confidence": confidence,
        "inputs": input_values,
        "derived": {
            "impact_parameter": float(impact_b),
            "semi_major_axis_au": float(a_au),
            "planet_radius_earth": float(r_earth),
            "equilibrium_temperature_k": float(t_eq),
        },
    }

    if label == "confirmed exoplanet":
        result["exoplanet"] = {
            "radius_earth": float(r_earth),
            "equilibrium_temperature_k": float(t_eq),
            "semi_major_axis_au": float(a_au),
        }

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
