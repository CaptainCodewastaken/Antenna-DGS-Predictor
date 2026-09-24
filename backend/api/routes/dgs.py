"""DGS equivalent circuit endpoints."""
from fastapi import APIRouter
from pydantic import BaseModel

from backend.api.schemas import DGSSlotSchema
from backend.physics_engine.dgs_model import dgs_lc_equivalent

router = APIRouter()

class DGSCircuitResponse(BaseModel):
    L_nH: float
    C_pF: float
    f_resonant_ghz: float

@router.post("/circuit", response_model=DGSCircuitResponse)
def get_dgs_circuit(slot: DGSSlotSchema, substrate_height_mm: float = 1.6, epsilon_r: float = 4.4):
    """
    Returns the equivalent LC circuit values for a single DGS slot.
    """
    from backend.physics_engine.types import DGSSlot
    phys_slot = DGSSlot(
        width_mm=slot.width_mm,
        length_mm=slot.length_mm,
        x_mm=slot.x_mm,
        y_mm=slot.y_mm
    )
    
    h_m = substrate_height_mm * 1e-3
    L_henry, C_farad = dgs_lc_equivalent(phys_slot, h_m, epsilon_r)
    
    # f = 1 / (2 * pi * sqrt(LC))
    import math
    if L_henry > 0 and C_farad > 0:
        f_hz = 1.0 / (2.0 * math.pi * math.sqrt(L_henry * C_farad))
    else:
        f_hz = 0.0
        
    return DGSCircuitResponse(
        L_nH=L_henry * 1e9,
        C_pF=C_farad * 1e12,
        f_resonant_ghz=f_hz / 1e9
    )
