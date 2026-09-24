"""
Physics Engine Facade.

Provides the high-level `calculate_antenna_metrics` function that integrates
the cavity model, gain model, impedance model, and DGS perturbation model
to compute end-to-end antenna performance.
"""
from typing import Dict, Any

from backend.physics_engine.types import AntennaConfig
from backend.physics_engine.cavity_model import resonant_frequency_hz
from backend.physics_engine.gain_model import gain_dbi
from backend.physics_engine.impedance_model import (
    input_impedance_edge,
    input_impedance_inset,
    impedance_bandwidth,
)
from backend.physics_engine.dgs_model import (
    dgs_frequency_shift,
    dgs_gain_penalty,
    dgs_bandwidth_multiplier,
)

__all__ = ["calculate_antenna_metrics"]


def calculate_antenna_metrics(config: AntennaConfig) -> Dict[str, float]:
    """
    Calculate full antenna metrics from geometry.

    Args:
        config: Full antenna configuration.

    Returns:
        Dictionary containing resonant_frequency_hz, gain_dbi, 
        impedance_ohms, and bandwidth_fractional.
    """
    # Convert inputs to meters for internal physics models
    patch_l = config.patch.length_mm * 1e-3
    patch_w = config.patch.width_mm * 1e-3
    sub_h = config.substrate.height_mm * 1e-3
    eps_r = config.substrate.epsilon_r
    tan_d = config.substrate.tan_delta

    from backend.physics_engine.cavity_model import (
        effective_permittivity,
        fringing_extension
    )
    
    eps_eff = effective_permittivity(eps_r, sub_h, patch_w)
    delta_l = fringing_extension(eps_eff, sub_h, patch_w)
    l_eff = patch_l + 2 * delta_l
    
    # 1. Base Cavity Model
    f_r_base = resonant_frequency_hz(patch_l, patch_w, sub_h, eps_r)
    
    # 2. DGS Perturbation on Frequency
    f_r_final = dgs_frequency_shift(f_r_base, config.slots, sub_h, eps_r)

    # 3. Gain Model
    base_gain = gain_dbi(patch_l, patch_w, sub_h, eps_r, tan_d)
    gain_penalty = dgs_gain_penalty(config.slots, patch_w, patch_l)
    final_gain = base_gain + gain_penalty

    # 4. Impedance Model
    r_edge = input_impedance_edge(patch_w, f_r_final)
    if config.feed.inset_mm > 0:
        inset_m = config.feed.inset_mm * 1e-3
        z_in = input_impedance_inset(r_edge, patch_l, inset_m)
    else:
        z_in = r_edge

    # 5. Bandwidth Model
    base_bw = impedance_bandwidth(f_r_final, sub_h, patch_w, eps_r, tan_d)
    bw_multiplier = dgs_bandwidth_multiplier(config.slots, patch_w, patch_l)
    final_bw = base_bw * bw_multiplier
    
    # 6. Efficiency Model
    from backend.physics_engine.gain_model import radiation_efficiency
    eta = radiation_efficiency(f_r_final, sub_h, eps_r, tan_d, patch_w)

    return {
        "resonant_frequency_hz": f_r_final,
        "gain_dbi": final_gain,
        "impedance_ohms": z_in,
        "bandwidth_fractional": final_bw,
        "radiation_efficiency": eta,
        "eps_eff": eps_eff,
        "delta_l_meters": delta_l,
        "l_eff_meters": l_eff,
    }
