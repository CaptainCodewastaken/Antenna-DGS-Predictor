"""
Cavity model for rectangular microstrip patch antenna.

Computes the resonant frequency of the dominant TM₀₁₀ mode using
Hammerstad's formulas for effective permittivity and fringing extension.

All internal computations in SI units (meters, Hz).

References:
    [1] Hammerstad, E.O. (1975). "Equations for Microstrip Circuit Design."
        Proc. 5th European Microwave Conference, pp. 268-272.
    [2] Balanis, C.A. (2016). "Antenna Theory: Analysis and Design."
        4th Edition, Chapter 14.
"""
import logging

import numpy as np

from backend.physics_engine.constants import c

logger = logging.getLogger(__name__)


def effective_permittivity(epsilon_r: float, h: float, w: float) -> float:
    """
    Compute effective dielectric constant using Hammerstad's formula.

    The fringing fields extend partly through the substrate and partly
    through air, so the wave sees an effective permittivity between
    1 and ε_r.

    Args:
        epsilon_r: Substrate relative permittivity (dimensionless).
        h: Substrate height in meters.
        w: Patch width in meters.

    Returns:
        Effective dielectric constant (dimensionless).

    Reference:
        Hammerstad (1975), Eq. 1. Balanis (2016), Eq. 14-1.
    """
    if w <= 0 or h <= 0:
        raise ValueError(f"Width and height must be positive: w={w}, h={h}")
    if epsilon_r <= 1.0:
        raise ValueError(f"epsilon_r must be > 1: got {epsilon_r}")

    ratio = w / h
    eps_eff = (
        (epsilon_r + 1) / 2
        + (epsilon_r - 1) / 2 * (1 + 12 / ratio) ** (-0.5)
    )
    return float(eps_eff)


def fringing_extension(epsilon_eff: float, h: float, w: float) -> float:
    """
    Compute the fringing length extension ΔL using Hammerstad's formula.

    The electric field fringes beyond the physical patch edge, making
    the antenna appear electrically longer than its physical length.

    Args:
        epsilon_eff: Effective dielectric constant (from effective_permittivity).
        h: Substrate height in meters.
        w: Patch width in meters.

    Returns:
        Fringing extension ΔL in meters (added to each radiating edge).

    Reference:
        Hammerstad (1975). Balanis (2016), Eq. 14-2.
    """
    if w <= 0 or h <= 0:
        raise ValueError(f"Width and height must be positive: w={w}, h={h}")

    ratio = w / h
    delta_l = (
        0.412 * h
        * ((epsilon_eff + 0.3) * (ratio + 0.264))
        / ((epsilon_eff - 0.258) * (ratio + 0.8))
    )
    return float(delta_l)


def resonant_frequency_hz(
    patch_l: float,
    patch_w: float,
    sub_h: float,
    epsilon_r: float,
) -> float:
    """
    Compute the resonant frequency of the dominant TM₀₁₀ mode.

    Uses the cavity model with Hammerstad corrections for fringing.

    Args:
        patch_l: Patch length in meters.
        patch_w: Patch width in meters.
        sub_h: Substrate height in meters.
        epsilon_r: Substrate relative permittivity.

    Returns:
        Resonant frequency in Hz.

    Reference:
        Balanis (2016), Eq. 14-5:
            f_r = c / (2 * L_eff * sqrt(ε_eff))
        where L_eff = L + 2*ΔL.
    """
    if patch_l <= 0 or patch_w <= 0 or sub_h <= 0:
        raise ValueError("All dimensions must be positive")

    eps_eff = effective_permittivity(epsilon_r, sub_h, patch_w)
    delta_l = fringing_extension(eps_eff, sub_h, patch_w)
    l_eff = patch_l + 2 * delta_l

    f_r = c / (2 * l_eff * np.sqrt(eps_eff))

    logger.debug(
        "Cavity model: ε_eff=%.3f, ΔL=%.4f mm, L_eff=%.4f mm, f_r=%.4f GHz",
        eps_eff, delta_l * 1e3, l_eff * 1e3, f_r / 1e9,
    )

    return float(f_r)
