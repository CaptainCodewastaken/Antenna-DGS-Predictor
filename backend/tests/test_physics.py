import pytest
from backend.physics_engine.cavity_model import effective_permittivity, resonant_frequency_hz
from backend.physics_engine.gain_model import directivity, radiation_efficiency, gain_dbi
from backend.physics_engine import calculate_antenna_metrics
from backend.physics_engine.types import AntennaConfig, SubstrateConfig, PatchConfig, FeedConfig

def test_effective_permittivity():
    eps = effective_permittivity(4.4, 1.6e-3, 30e-3)
    assert eps > 1.0 and eps < 4.4

def test_resonant_frequency():
    # 30x40 patch on 1.6mm FR4
    f_r = resonant_frequency_hz(30e-3, 40e-3, 1.6e-3, 4.4)
    # Expected around 2.4 GHz
    assert 2.0e9 < f_r < 3.0e9

def test_radiation_efficiency():
    # Test valid outputs for efficiency (0 to 1)
    f_r = 2.4e9
    eta = radiation_efficiency(f_r, 1.6e-3, 4.4, 0.02, 40e-3)
    assert 0.0 < eta <= 1.0

def test_calculate_antenna_metrics():
    config = AntennaConfig(
        substrate=SubstrateConfig(epsilon_r=4.4, tan_delta=0.02, height_mm=1.6, width_mm=60, length_mm=60),
        patch=PatchConfig(width_mm=40, length_mm=30),
        feed=FeedConfig(width_mm=3, inset_mm=10),
        slots=[]
    )
    metrics = calculate_antenna_metrics(config)
    
    assert "resonant_frequency_hz" in metrics
    assert "bandwidth_fractional" in metrics
    assert "radiation_efficiency" in metrics
    
    assert metrics["radiation_efficiency"] > 0
    assert metrics["bandwidth_fractional"] > 0
    assert metrics["gain_dbi"] > 0
