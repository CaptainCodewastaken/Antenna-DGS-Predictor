"""
Impedance and bandwidth model for rectangular microstrip patch antenna.

Computes the input impedance for an inset-fed patch and the impedance
bandwidth based on the total Q-factor.

All internal computations in SI units.

References:
    [1] Balanis, C.A. (2016). "Antenna Theory: Analysis and Design."
        4th Edition, Chapter 14.
"""
import logging
import numpy as np

from backend.physics_engine.constants import c, eta_0
from backend.physics_engine.cavity_model import effective_permittivity
from backend.physics_engine.gain_model import radiation_efficiency

logger = logging.getLogger(__name__)


def input_impedance_edge(w: float, f: float) -> float:
    """
    Compute input resistance at the radiating edge of the patch (y=0 or y=L).

    Args:
        w: Patch width in meters.
        f: Operating frequency in Hz.

    Returns:
        Edge input resistance R_in(0) in ohms.

    Reference:
        Balanis (2016), Eq. 14-17: R_in = 1 / (2 * G1) (approx, ignoring mutual)
        More accurately with mutual conductance G12.
    """
    wavelength = c / f
    # Radiation conductance of a single slot
    g1 = w / (120 * wavelength)
    
    # R_in at the edge is approximately 1 / (2 * G1) if G12 is neglected.
    # We use a standard approximation for standard patches:
    # R_in ≈ 90 * (ε_r^2 / (ε_r - 1)) * (L / W)^2 ... no, that's transmission line model.
    # Cavity model: R_in(y=0) = 1 / (2 * G1) = 60 * λ0 / W
    
    r_edge = 60.0 * wavelength / w if w > 0 else 1e6
    
    # Typical edge resistance is 150 - 300 ohms.
    r_edge = float(np.clip(r_edge, 50.0, 1000.0))
    
    return r_edge


def input_impedance_inset(
    r_edge: float, 
    patch_l: float, 
    inset_distance: float
) -> float:
    """
    Compute input resistance at a given inset distance from the edge.

    The resistance follows a cosine-squared distribution from the edge
    to the center of the patch.

    Args:
        r_edge: Input resistance at the edge in ohms.
        patch_l: Patch length in meters.
        inset_distance: Distance from the radiating edge in meters (y₀).

    Returns:
        Input resistance at the inset feed point in ohms.

    Reference:
        Balanis (2016), Eq. 14-20:
        R_in(y₀) = R_in(0) * cos²(π * y₀ / L)
    """
    if patch_l <= 0:
        raise ValueError("Patch length must be positive")
        
    if not (0 <= inset_distance <= patch_l / 2.0):
        # Allow slight overshoot for numerical reasons, but conceptually 
        # it only makes sense up to center
        pass
        
    # The inset is often denoted as y0.
    arg = np.pi * inset_distance / patch_l
    r_in = r_edge * (np.cos(arg) ** 2)
    
    return float(max(r_in, 0.0))


def compute_optimal_inset(r_edge: float, patch_l: float, target_z: float = 50.0) -> float:
    """
    Compute the inset distance required to achieve a target input impedance.

    Args:
        r_edge: Edge resistance in ohms.
        patch_l: Patch length in meters.
        target_z: Target impedance in ohms (default 50).

    Returns:
        Optimal inset distance y₀ in meters.
    """
    if target_z > r_edge:
        logger.warning(
            f"Target impedance ({target_z}Ω) > edge impedance ({r_edge}Ω). "
            f"Matching impossible. Returning inset=0."
        )
        return 0.0
        
    # R_in(y0) = R_edge * cos²(π * y0 / L)
    # y0 = (L / π) * arccos(sqrt(target_z / R_edge))
    
    ratio = np.sqrt(target_z / r_edge)
    y0 = (patch_l / np.pi) * np.arccos(ratio)
    
    return float(y0)


def impedance_bandwidth(
    f_r: float,
    sub_h: float,
    patch_w: float,
    epsilon_r: float,
    tan_delta: float,
    vswr_max: float = 2.0
) -> float:
    """
    Compute the fractional impedance bandwidth.

    Bandwidth is inversely proportional to the total Q-factor.

    Args:
        f_r: Resonant frequency in Hz.
        sub_h: Substrate height in meters.
        patch_w: Patch width in meters.
        epsilon_r: Substrate relative permittivity.
        tan_delta: Substrate loss tangent.
        vswr_max: Maximum acceptable VSWR (default 2.0, equivalent to -10dB S11).

    Returns:
        Fractional bandwidth (dimensionless). Multiply by 100 for percentage.
        BW = Δf / f_r

    Reference:
        Balanis (2016), Eq. 14-38.
        BW = (VSWR - 1) / (Q_total * √VSWR)
    """
    # 1. We need the total Q factor. We computed this inside radiation_efficiency,
    # but let's recompute Q_total from efficiency and Q_rad.
    # η = Q_total / Q_rad => Q_total = η * Q_rad
    
    eps_eff = effective_permittivity(epsilon_r, sub_h, patch_w)
    # Q_rad ≈ c * √ε_eff / (4 * f * h)
    q_rad = c * np.sqrt(eps_eff) / (4 * f_r * sub_h)
    
    eta = radiation_efficiency(f_r, sub_h, epsilon_r, tan_delta, patch_w)
    
    q_total = eta * q_rad
    
    if q_total <= 0:
        return 0.0
        
    # Bandwidth formula based on VSWR
    bw_fractional = (vswr_max - 1.0) / (q_total * np.sqrt(vswr_max))
    
    # Typical patch bandwidth is 1% to 5%
    bw_fractional = float(np.clip(bw_fractional, 0.0, 0.20))
    
    logger.debug(
        "Bandwidth: Q_rad=%.1f, Q_tot=%.1f, BW=%.2f%%",
        q_rad, q_total, bw_fractional * 100,
    )
    
    return bw_fractional
