"""
Data types for antenna configurations.

All dimension fields are in millimeters at the API boundary.
Internal physics computations convert to SI (meters) before use.
"""
from dataclasses import dataclass, field


@dataclass
class SubstrateConfig:
    """Substrate / ground plane configuration.

    Attributes:
        width_mm: Ground plane width in mm.
        length_mm: Ground plane length in mm.
        height_mm: Substrate thickness in mm.
        epsilon_r: Relative permittivity (dielectric constant).
        tan_delta: Loss tangent.
    """
    width_mm: float
    length_mm: float
    height_mm: float
    epsilon_r: float
    tan_delta: float


@dataclass
class PatchConfig:
    """Rectangular patch dimensions.

    Attributes:
        width_mm: Patch width in mm.
        length_mm: Patch length in mm.
    """
    width_mm: float
    length_mm: float


@dataclass
class FeedConfig:
    """Microstrip feed line configuration.

    Attributes:
        width_mm: Feed line width in mm.
        inset_mm: Inset depth for impedance matching in mm.
    """
    width_mm: float
    inset_mm: float = 0.0


@dataclass
class DGSSlot:
    """Rectangular DGS slot on the ground plane.

    Attributes:
        width_mm: Slot width in mm.
        length_mm: Slot length in mm.
        x_mm: Slot center X position on ground plane in mm.
        y_mm: Slot center Y position on ground plane in mm.
    """
    width_mm: float
    length_mm: float
    x_mm: float
    y_mm: float


@dataclass
class AntennaConfig:
    """Complete antenna configuration.

    Attributes:
        substrate: Substrate / ground plane parameters.
        patch: Rectangular patch parameters.
        feed: Microstrip feed line parameters.
        slots: List of DGS slots (0, 1, or 2).
    """
    substrate: SubstrateConfig
    patch: PatchConfig
    feed: FeedConfig
    slots: list[DGSSlot] = field(default_factory=list)


# Preset substrate materials with published properties.
SUBSTRATES: dict[str, dict[str, float]] = {
    "FR4": {"epsilon_r": 4.4, "tan_delta": 0.02},
    "Rogers RT5880": {"epsilon_r": 2.2, "tan_delta": 0.0009},
    "Rogers RO4003C": {"epsilon_r": 3.55, "tan_delta": 0.0027},
    "Rogers RO3010": {"epsilon_r": 10.2, "tan_delta": 0.0022},
}
