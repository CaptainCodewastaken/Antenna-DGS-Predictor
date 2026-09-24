"""S-parameter (return loss) endpoint."""
from fastapi import APIRouter
import numpy as np

from backend.api.schemas import PredictRequest

router = APIRouter()

@router.post("/s-parameter")
def get_s_parameter(request: PredictRequest, points: int = 101, span_ghz: float = 1.0):
    """
    Returns S11 vs frequency around the resonant frequency.
    Uses a simple resonant circuit approximation.
    """
    from backend.physics_engine import calculate_antenna_metrics
    from backend.physics_engine.types import AntennaConfig, SubstrateConfig, PatchConfig, FeedConfig, DGSSlot
    
    slots = []
    for s in request.slots:
        slots.append(DGSSlot(
            width_mm=s.width_mm,
            length_mm=s.length_mm,
            x_mm=s.x_mm,
            y_mm=s.y_mm
        ))
        
    config = AntennaConfig(
        substrate=SubstrateConfig(
            epsilon_r=request.substrate.epsilon_r,
            tan_delta=request.substrate.tan_delta,
            height_mm=request.substrate.height_mm,
            width_mm=request.substrate.width_mm,
            length_mm=request.substrate.length_mm,
        ),
        patch=PatchConfig(
            width_mm=request.patch.width_mm,
            length_mm=request.patch.length_mm,
        ),
        feed=FeedConfig(
            width_mm=request.feed.width_mm,
            inset_mm=request.feed.inset_mm,
        ),
        slots=slots
    )
    
    metrics = calculate_antenna_metrics(config)
    f_r = metrics["resonant_frequency_hz"]
    z_in = metrics["impedance_ohms"]
    bw_frac = metrics["bandwidth_fractional"]
    
    f_r_ghz = f_r / 1e9
    
    # Create frequency sweep
    f_start = max(0.1, f_r_ghz - span_ghz / 2)
    f_end = f_r_ghz + span_ghz / 2
    freqs = np.linspace(f_start, f_end, points)
    freqs_hz = freqs * 1e9
    
    # Simple RLC series resonant circuit approximation for input impedance
    # We know at resonance, Z_in is pure real.
    # Q = 1 / bw_frac
    Q = 1.0 / max(bw_frac, 1e-4)
    
    # Delta f
    delta_f = (freqs_hz / f_r) - (f_r / freqs_hz)
    
    # Complex impedance
    Z = z_in * (1 + 1j * Q * delta_f)
    
    # S11 with Z0 = 50 ohms
    Z0 = 50.0
    gamma = (Z - Z0) / (Z + Z0)
    s11_db = 20 * np.log10(np.abs(gamma) + 1e-10)
    
    return {
        "freq_ghz": freqs.tolist(),
        "s11_db": s11_db.tolist(),
        "z_in_real": np.real(Z).tolist(),
        "z_in_imag": np.imag(Z).tolist()
    }
