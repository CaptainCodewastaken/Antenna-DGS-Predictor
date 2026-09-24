"""
Physical constants used throughout the physics engine.

All values in SI units. Do NOT approximate — use precise values
from scipy.constants or CODATA where applicable.

Reference:
    CODATA 2018 recommended values.
    https://physics.nist.gov/cuu/Constants/
"""
import numpy as np


# Speed of light in vacuum (m/s)
c: float = 2.998e8

# Permittivity of free space (F/m)
epsilon_0: float = 8.854e-12

# Permeability of free space (H/m)
mu_0: float = 4 * np.pi * 1e-7

# Conductivity of copper (S/m)
sigma_copper: float = 5.8e7

# Impedance of free space (Ω)
eta_0: float = np.sqrt(mu_0 / epsilon_0)  # ≈ 376.73 Ω
