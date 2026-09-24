"""End-to-end integration tests for the physics engine."""
import pytest

from backend.physics_engine import calculate_antenna_metrics
from backend.physics_engine.types import (
    AntennaConfig,
    SubstrateConfig,
    PatchConfig,
    FeedConfig,
    DGSSlot,
)


def test_standard_patch_metrics() -> None:
    """Test a standard 2.4 GHz FR4 patch without DGS."""
    config = AntennaConfig(
        substrate=SubstrateConfig(epsilon_r=4.4, height_mm=1.6, tan_delta=0.02, width_mm=60.0, length_mm=60.0),
        patch=PatchConfig(width_mm=38.0, length_mm=29.0),
        feed=FeedConfig(width_mm=3.0, inset_mm=8.0),
        slots=[],
    )
    
    metrics = calculate_antenna_metrics(config)
    
    f_r = metrics["resonant_frequency_hz"]
    assert 2.2e9 <= f_r <= 2.6e9  # Roughly 2.4 GHz
    
    gain = metrics["gain_dbi"]
    assert 1.0 <= gain <= 8.0  # Typical gain for lossy FR4
    
    impedance = metrics["impedance_ohms"]
    assert 10.0 <= impedance <= 100.0  # Matched roughly to 50 ohms via inset
    
    bw = metrics["bandwidth_fractional"]
    assert 0.01 <= bw <= 0.05  # 1-5% bandwidth


def test_dgs_effects_applied() -> None:
    """Test that adding DGS slots properly shifts metrics."""
    base_config = AntennaConfig(
        substrate=SubstrateConfig(epsilon_r=4.4, height_mm=1.6, tan_delta=0.02, width_mm=60.0, length_mm=60.0),
        patch=PatchConfig(width_mm=38.0, length_mm=29.0),
        feed=FeedConfig(width_mm=3.0, inset_mm=8.0),
        slots=[],
    )
    
    dgs_config = AntennaConfig(
        substrate=SubstrateConfig(epsilon_r=4.4, height_mm=1.6, tan_delta=0.02, width_mm=60.0, length_mm=60.0),
        patch=PatchConfig(width_mm=38.0, length_mm=29.0),
        feed=FeedConfig(width_mm=3.0, inset_mm=8.0),
        slots=[
            DGSSlot(width_mm=5.0, length_mm=15.0, x_mm=0.0, y_mm=10.0)
        ],
    )
    
    base_metrics = calculate_antenna_metrics(base_config)
    dgs_metrics = calculate_antenna_metrics(dgs_config)
    
    # 1. Frequency should shift down
    assert dgs_metrics["resonant_frequency_hz"] < base_metrics["resonant_frequency_hz"]
    
    # 2. Gain should be lower (penalty applied)
    assert dgs_metrics["gain_dbi"] < base_metrics["gain_dbi"]
    
    # 3. Bandwidth should decrease slightly
    assert dgs_metrics["bandwidth_fractional"] < base_metrics["bandwidth_fractional"]


def test_edge_feed_impedance() -> None:
    """Test impedance when inset is 0."""
    config = AntennaConfig(
        substrate=SubstrateConfig(epsilon_r=4.4, height_mm=1.6, tan_delta=0.02, width_mm=60.0, length_mm=60.0),
        patch=PatchConfig(width_mm=38.0, length_mm=29.0),
        feed=FeedConfig(width_mm=3.0, inset_mm=0.0),
        slots=[],
    )
    
    metrics = calculate_antenna_metrics(config)
    
    # Edge impedance for standard patch should be high (150-350 ohms)
    assert 150.0 <= metrics["impedance_ohms"] <= 400.0
