"""Radiation pattern endpoint."""
from fastapi import APIRouter
import numpy as np

from backend.api.schemas import PredictRequest

router = APIRouter()

@router.post("/pattern")
def get_pattern(request: PredictRequest, resolution_deg: int = 5):
    """
    Returns 3D radiation pattern (theta, phi, gain) and 2D cuts.
    Uses a simplified cos^2(theta) approximation for the microstrip patch.
    """
    # Create grid
    theta = np.radians(np.arange(0, 91, resolution_deg)) # 0 to 90
    phi = np.radians(np.arange(0, 361, resolution_deg))  # 0 to 360
    
    # Calculate base gain from physics engine
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
    peak_gain = metrics["gain_dbi"]
    
    # Simple cos^q(theta) model for patch antenna
    # q is chosen to match the directivity/gain roughly. Let's use q=2 for now.
    
    T, P = np.meshgrid(theta, phi, indexing='ij')
    # Gain in linear scale
    peak_linear = 10 ** (peak_gain / 10)
    
    # Model: U(theta, phi) ~ cos^2(theta)
    # Gain(theta, phi) = Peak * cos^2(theta)
    gain_linear = peak_linear * (np.cos(T) ** 2)
    # Avoid log10(0)
    gain_linear = np.maximum(gain_linear, 1e-10)
    gain_db = 10 * np.log10(gain_linear)
    
    # 2D Cuts
    # E-plane typically phi=0
    # H-plane typically phi=90
    phi_deg_arr = np.degrees(phi)
    theta_deg_arr = np.degrees(theta)
    
    idx_e = np.argmin(np.abs(phi_deg_arr - 0))
    idx_h = np.argmin(np.abs(phi_deg_arr - 90))
    
    e_plane = gain_db[:, idx_e].tolist()
    h_plane = gain_db[:, idx_h].tolist()
    
    return {
        "theta": theta_deg_arr.tolist(),
        "phi": phi_deg_arr.tolist(),
        "gain_db": gain_db.tolist(), # 2D array
        "e_plane": e_plane,
        "h_plane": h_plane,
        "beamwidth_e": 90.0, # Approximate
        "beamwidth_h": 90.0
    }
