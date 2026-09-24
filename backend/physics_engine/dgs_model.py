"""
DGS (Defected Ground Structure) perturbation model.

Calculates the effect of etching slots in the ground plane on the
antenna's resonant frequency, gain, and bandwidth.
Modeled using an equivalent LC circuit where the DGS adds series inductance
and shunt capacitance to the transmission line model of the patch.

References:
    [1] Guha, D. et al. (2011). "Microstrip and Printed Antennas: New Trends,
        Techniques and Applications." Wiley.
    [2] Arya, A.K. et al. (2010). "Defected Ground Structure in the perspective
        of Microstrip antenna: A review."
"""
import logging
import numpy as np

from backend.physics_engine.constants import mu_0, epsilon_0
from backend.physics_engine.types import DGSSlot

logger = logging.getLogger(__name__)


def dgs_lc_equivalent(
    slot: DGSSlot,
    sub_h: float,
    epsilon_r: float
) -> tuple[float, float]:
    """
    Compute the equivalent inductance and capacitance of a DGS slot.

    Args:
        slot: DGSSlot configuration.
        sub_h: Substrate height in meters.
        epsilon_r: Substrate relative permittivity.

    Returns:
        Tuple of (Inductance in Henrys, Capacitance in Farads).

    Reference:
        Approximations based on transmission line equivalents of defected grounds.
    """
    # L_dgs is roughly proportional to the slot length orthogonal to current flow
    # and inversely proportional to slot width.
    # C_dgs depends on the gap width and substrate.
    
    # Very rough closed-form empirical approximations:
    # L = μ₀ * (sub_h / slot_w) * slot_l * K (where K is a geometry factor)
    
    # We will use simplified empirical forms for rectangular slots.
    slot_l = slot.length_mm * 1e-3
    slot_w = slot.width_mm * 1e-3
    
    if slot_w <= 0 or slot_l <= 0:
        return 0.0, 0.0
        
    # Length of slot (orthogonal to current) increases path length -> Inductance
    l_dgs = mu_0 * (slot_l * sub_h / slot_w) * 0.1 
    
    # Gap width -> Capacitance (fringe effect across gap)
    c_dgs = epsilon_0 * epsilon_r * (slot_l / slot_w) * sub_h * 0.5
        
    return l_dgs, c_dgs


def dgs_frequency_shift(
    f_r_original: float,
    slots: list[DGSSlot],
    sub_h: float,
    epsilon_r: float
) -> float:
    """
    Compute the new resonant frequency when DGS slots are added.

    DGS typically increases the effective inductance (and sometimes capacitance),
    which lowers the resonant frequency: f_new = f_old / sqrt(1 + L_dgs/L_eq).

    Args:
        f_r_original: Resonant frequency without DGS in Hz.
        slots: List of DGS slots.
        sub_h: Substrate height in meters.
        epsilon_r: Substrate relative permittivity.

    Returns:
        New resonant frequency in Hz.
    """
    if not slots:
        return f_r_original
        
    total_l_dgs = 0.0
    for slot in slots:
        l, c = dgs_lc_equivalent(slot, sub_h, epsilon_r)
        total_l_dgs += l
        
    # L_eq of the patch itself is roughly:
    # L_eq = 1 / ( (2π f_r)² * C_eq )
    # Very roughly, L_eq ~ 1 nH for typical patches.
    # We use an empirical shift formula:
    # Δf/f ≈ - k * (Total Area of DGS) / (Area of Patch)
    # But using L is more physically grounded.
    
    # We calibrate L_eq so that typical DGS gives 5-15% frequency reduction.
    l_eq_patch = 2e-9  # 2 nH baseline
    
    frequency_ratio = 1.0 / np.sqrt(1.0 + total_l_dgs / l_eq_patch)
    
    # Maximum physical frequency reduction is usually around 30%
    frequency_ratio = max(frequency_ratio, 0.70)
    
    new_f_r = f_r_original * frequency_ratio
    
    logger.debug(
        "DGS Shift: L_dgs=%.2f nH, f_ratio=%.3f, f_new=%.4f GHz",
        total_l_dgs * 1e9, frequency_ratio, new_f_r / 1e9,
    )
    
    return float(new_f_r)


def dgs_gain_penalty(
    slots: list[DGSSlot],
    patch_w: float,
    patch_l: float
) -> float:
    """
    Compute the gain penalty (in dB) due to back-radiation from DGS.

    Slots in the ground plane leak energy to the backside, increasing the
    back-lobe and reducing broadside gain.

    Args:
        slots: List of DGS slots.
        patch_w: Patch width in meters.
        patch_l: Patch length in meters.

    Returns:
        Gain penalty in dB (always a non-positive number, e.g., -1.5).
    """
    if not slots:
        return 0.0
        
    patch_area = patch_w * patch_l
    total_slot_area = sum((s.length_mm * 1e-3) * (s.width_mm * 1e-3) for s in slots)
    
    # If slot area is larger than patch, it's physically invalid for standard models
    area_ratio = min(total_slot_area / patch_area, 0.8)
    
    # Empirical penalty: roughly -3 dB if half the ground is missing under the patch.
    # dB penalty = -5.0 * area_ratio
    penalty = -5.0 * area_ratio
    
    return float(penalty)


def dgs_bandwidth_multiplier(
    slots: list[DGSSlot],
    patch_w: float,
    patch_l: float
) -> float:
    """
    Compute the bandwidth multiplier due to DGS.

    DGS often increases the Q-factor slightly by storing reactive energy,
    but it can also decrease Q by increasing radiation losses.
    Usually, single band DGS *decreases* bandwidth, while specific shapes
    can increase it. For our closed-form baseline, we assume a slight decrease
    based on the added reactive energy (L).

    Args:
        slots: List of DGS slots.
        patch_w: Patch width in meters.
        patch_l: Patch length in meters.

    Returns:
        Multiplier for the bandwidth (e.g., 0.9 means 10% reduction).
    """
    if not slots:
        return 1.0
        
    patch_area = patch_w * patch_l
    total_slot_area = sum((s.length_mm * 1e-3) * (s.width_mm * 1e-3) for s in slots)
    
    area_ratio = min(total_slot_area / patch_area, 0.8)
    
    # Added inductance dominates, lowering resonant frequency but keeping R_in
    # similar -> Q increases -> BW decreases.
    # Multiplier: 1.0 down to 0.7
    multiplier = 1.0 - (0.4 * area_ratio)
    
    return float(max(multiplier, 0.5))
