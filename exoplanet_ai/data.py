from __future__ import annotations

import io
import os
import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import pandas as pd
import requests


KOI_CUMULATIVE_URLS = [
    # TAP endpoint (preferred)
    "https://exoplanetarchive.ipac.caltech.edu/TAP/sync?query=select+*+from+kepler.koi&format=csv",
    # Legacy NStED API fallback
    "https://exoplanetarchive.ipac.caltech.edu/cgi-bin/nstedAPI/nph-nstedAPI?table=cumulative&select=*",
]


@dataclass
class DatasetPaths:
    data_dir: str = "data"
    raw_dir: str = os.path.join("data", "raw")
    processed_dir: str = os.path.join("data", "processed")

    def ensure(self) -> None:
        os.makedirs(self.raw_dir, exist_ok=True)
        os.makedirs(self.processed_dir, exist_ok=True)


def _download_csv_with_fallback(urls: List[str], timeout: int = 120) -> pd.DataFrame:
    last_error: Optional[Exception] = None
    for url in urls:
        try:
            resp = requests.get(url, timeout=timeout)
            resp.raise_for_status()
            # Heuristic: some endpoints return text/csv; others text/plain
            content = resp.content
            return pd.read_csv(io.BytesIO(content))
        except Exception as e:  # noqa: BLE001
            last_error = e
            time.sleep(1.0)
            continue
    if last_error is not None:
        raise RuntimeError(f"Failed to download CSV from any URL: {last_error}")
    raise RuntimeError("Failed to download CSV from any URL")


def download_kepler_koi(paths: DatasetPaths) -> str:
    paths.ensure()
    out_path = os.path.join(paths.raw_dir, "kepler_koi_cumulative.csv")
    if os.path.exists(out_path) and os.path.getsize(out_path) > 1024:
        return out_path
    df = _download_csv_with_fallback(KOI_CUMULATIVE_URLS)
    df.to_csv(out_path, index=False)
    return out_path


def load_kepler_training_frame(paths: DatasetPaths) -> pd.DataFrame:
    csv_path = download_kepler_koi(paths)
    df = pd.read_csv(csv_path)

    # Choose SNR column robustly (schema varies across exports)
    snr_candidates = [
        "koi_model_snr",  # common in KOI cumulative
        "koi_snr",        # sometimes present
        "koi_max_sngle_ev",  # single event SNR as a fallback proxy
    ]
    snr_col = next((c for c in snr_candidates if c in df.columns), None)
    if snr_col is None:
        raise RuntimeError("Could not locate an SNR-like column in KOI table")

    # Map to unified schema (populate SNR dynamically)
    rename_map = {
        # Features
        "koi_period": "orbital_period_days",
        "koi_depth": "transit_depth_ppm",
        "koi_duration": "transit_duration_hours",
        "koi_srad": "stellar_radius_solar",
        "koi_smass": "stellar_mass_solar",
        "koi_steff": "stellar_temperature_k",
        snr_col: "snr",
        "koi_kepmag": "stellar_magnitude",
        # Label
        "koi_disposition": "disposition",
    }

    # Ensure required columns exist
    keep_cols = list(rename_map.keys())
    missing = [c for c in keep_cols if c not in df.columns]
    if missing:
        raise RuntimeError(f"Unexpected KOI columns missing: {missing}")

    df = df[keep_cols].rename(columns=rename_map)
    # Convert depth ppm -> fraction
    df["transit_depth_fraction"] = df["transit_depth_ppm"] / 1_000_000.0

    # Normalize labels to 3 classes
    df["label"] = (
        df["disposition"].str.upper().map({
            "CONFIRMED": "confirmed exoplanet",
            "CANDIDATE": "planetary candidate",
            "FALSE POSITIVE": "false positive",
        })
    )

    df = df.dropna(subset=[
        "orbital_period_days",
        "transit_depth_fraction",
        "transit_duration_hours",
        "stellar_radius_solar",
        "stellar_mass_solar",
        "stellar_temperature_k",
        "snr",
        "stellar_magnitude",
        "label",
    ])

    # Basic plausibility filters to remove obvious artefacts/outliers
    df = df[(df["orbital_period_days"] > 0) & (df["orbital_period_days"] < 1000)]
    df = df[(df["transit_duration_hours"] > 0) & (df["transit_duration_hours"] < 50)]
    df = df[(df["transit_depth_fraction"] > 1e-7) & (df["transit_depth_fraction"] < 0.2)]
    df = df[(df["stellar_radius_solar"] > 0.05) & (df["stellar_radius_solar"] < 100)]
    df = df[(df["stellar_mass_solar"] > 0.05) & (df["stellar_mass_solar"] < 100)]
    df = df[(df["stellar_temperature_k"] > 2000) & (df["stellar_temperature_k"] < 20000)]
    df = df[(df["snr"] > 0) & (df["snr"] < 1e6)]

    # Drop rows where label mapping failed
    df = df[df["label"].notna()]

    return df.reset_index(drop=True)
