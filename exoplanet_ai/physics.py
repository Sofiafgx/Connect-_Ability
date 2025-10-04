from __future__ import annotations

import math
from dataclasses import dataclass

from .constants import (
    G_SI,
    M_SUN_KG,
    R_SUN_M,
    AU_M,
    R_EARTH_M,
    PI,
    SECONDS_PER_DAY,
)


@dataclass
class OrbitOutputs:
    semi_major_axis_au: float
    impact_parameter: float


def compute_semi_major_axis_au(orbital_period_days: float, stellar_mass_solar: float) -> float:
    """Compute semi-major axis in AU via Kepler's third law (circular orbit, M_p << M_*).

    a = (G M_* P^2 / (4 pi^2))^(1/3)
    """
    if orbital_period_days <= 0 or stellar_mass_solar <= 0:
        return float("nan")
    period_seconds = orbital_period_days * SECONDS_PER_DAY
    m_star_kg = stellar_mass_solar * M_SUN_KG
    a_meters = (G_SI * m_star_kg * period_seconds**2 / (4.0 * PI**2)) ** (1.0 / 3.0)
    return a_meters / AU_M


def estimate_planet_radius_earth(transit_depth_fraction: float, stellar_radius_solar: float) -> float:
    """Estimate planet radius from transit depth assuming depth ≈ (R_p/R_*)^2.

    Returns radius in Earth radii.
    """
    if transit_depth_fraction <= 0 or stellar_radius_solar <= 0:
        return float("nan")
    k = math.sqrt(max(transit_depth_fraction, 0.0))
    r_planet_m = k * stellar_radius_solar * R_SUN_M
    return r_planet_m / R_EARTH_M


def compute_impact_parameter(
    orbital_period_days: float,
    transit_duration_hours: float,
    transit_depth_fraction: float,
    stellar_radius_solar: float,
    stellar_mass_solar: float,
) -> float:
    """Approximate impact parameter using transit duration and Kepler's law.

    Assumptions: circular orbit, sin(i)≈1 for transiting systems, small planet.

    Using: sin(pi T/P) ≈ (R_*/a) sqrt((1+k)^2 - b^2)
    => b ≈ sqrt((1+k)^2 - (a/R_*)^2 sin^2(pi T/P))
    where k = R_p/R_* ≈ sqrt(depth)
    """
    if (
        orbital_period_days <= 0
        or transit_duration_hours <= 0
        or transit_depth_fraction <= 0
        or stellar_radius_solar <= 0
        or stellar_mass_solar <= 0
    ):
        return float("nan")

    a_au = compute_semi_major_axis_au(orbital_period_days, stellar_mass_solar)
    a_over_rstar = (a_au * AU_M) / (stellar_radius_solar * R_SUN_M)

    # Convert duration to days to match P units
    t_days = transit_duration_hours / 24.0
    angle = PI * (t_days / orbital_period_days)
    s = math.sin(angle)

    k = math.sqrt(max(transit_depth_fraction, 0.0))
    term = (a_over_rstar * s) ** 2
    inside = (1.0 + k) ** 2 - term

    # Numerical safety and physical bounds: 0 <= b <= 1+k
    if inside < 0:
        b = 0.0
    else:
        b = math.sqrt(inside)
    return min(max(b, 0.0), 1.0 + k)


def estimate_equilibrium_temperature_k(
    stellar_temperature_k: float,
    stellar_radius_solar: float,
    semi_major_axis_au: float,
    bond_albedo: float = 0.3,
    full_redistribution: bool = True,
) -> float:
    """Estimate planetary equilibrium temperature.

    For full heat redistribution: T_eq = T_* (1 - A)^{1/4} sqrt(R_*/(2 a))
    For no redistribution (dayside): T_eq = T_* (1 - A)^{1/4} sqrt(R_*/a)
    """
    if (
        stellar_temperature_k <= 0
        or stellar_radius_solar <= 0
        or semi_major_axis_au <= 0
    ):
        return float("nan")
    factor = 2.0 if full_redistribution else 1.0
    ratio = (stellar_radius_solar * R_SUN_M) / (factor * semi_major_axis_au * AU_M)
    return stellar_temperature_k * (max(1.0 - bond_albedo, 0.0) ** 0.25) * math.sqrt(ratio)
