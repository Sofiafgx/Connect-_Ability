"""Physical constants and unit conversions in SI, plus solar/Earth units."""

from __future__ import annotations

import math

# SI constants
G_SI = 6.67430e-11  # m^3 kg^-1 s^-2
M_SUN_KG = 1.98847e30  # kg
R_SUN_M = 6.957e8  # m
AU_M = 1.495978707e11  # m
R_EARTH_M = 6.371e6  # m
SIGMA_SB = 5.670374419e-8  # W m^-2 K^-4 (not used directly but kept)
PI = math.pi

# Common numeric helpers
SECONDS_PER_DAY = 86400.0
HOURS_PER_DAY = 24.0
