"""
Pydantic schemas for the API.
"""
from typing import List, Optional
from pydantic import BaseModel, Field, model_validator


class SubstrateSchema(BaseModel):
    epsilon_r: float = Field(..., gt=1.0, description="Relative permittivity")
    tan_delta: float = Field(..., ge=0.0, description="Loss tangent")
    height_mm: float = Field(..., gt=0.0, description="Substrate height in mm")
    width_mm: float = Field(..., gt=0.0, description="Substrate width in mm")
    length_mm: float = Field(..., gt=0.0, description="Substrate length in mm")


class PatchSchema(BaseModel):
    width_mm: float = Field(..., gt=0.0, description="Patch width in mm")
    length_mm: float = Field(..., gt=0.0, description="Patch length in mm")


class FeedSchema(BaseModel):
    width_mm: float = Field(..., gt=0.0, description="Feed line width in mm")
    inset_mm: float = Field(..., ge=0.0, description="Feed inset depth in mm")


class DGSSlotSchema(BaseModel):
    width_mm: float = Field(..., gt=0.0, description="Slot width in mm (along Y axis)")
    length_mm: float = Field(..., gt=0.0, description="Slot length in mm (along X axis)")
    x_mm: float = Field(..., description="Center X coordinate in mm")
    y_mm: float = Field(..., description="Center Y coordinate in mm")


class PredictRequest(BaseModel):
    substrate: SubstrateSchema
    patch: PatchSchema
    feed: FeedSchema
    slots: List[DGSSlotSchema] = Field(default_factory=list, max_length=2)

    @model_validator(mode="after")
    def validate_physics(self) -> 'PredictRequest':
        # Patch must fit on substrate
        if self.patch.width_mm > self.substrate.width_mm:
            raise ValueError("Patch width cannot exceed substrate width.")
        if self.patch.length_mm > self.substrate.length_mm:
            raise ValueError("Patch length cannot exceed substrate length.")
            
        # Inset must not be larger than half patch length
        if self.feed.inset_mm > self.patch.length_mm / 2.0:
            raise ValueError("Feed inset depth cannot exceed half the patch length.")
            
        # Feed width must not be larger than patch width
        if self.feed.width_mm > self.patch.width_mm:
            raise ValueError("Feed width cannot exceed patch width.")
            
        return self


class PhysicsMetricsSchema(BaseModel):
    resonant_frequency_hz: float
    gain_dbi: float
    impedance_ohms: float
    bandwidth_fractional: float
    radiation_efficiency: float
    eps_eff: float
    delta_l_meters: float
    l_eff_meters: float


class PredictResponse(BaseModel):
    physics: PhysicsMetricsSchema
    ml_predictions: dict[str, dict[str, float]]
