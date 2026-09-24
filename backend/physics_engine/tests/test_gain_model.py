"""Tests for gain model: directivity, radiation efficiency, and gain."""
import pytest

from backend.physics_engine.gain_model import (
    directivity,
    gain_dbi,
    radiation_conductance,
    radiation_efficiency,
)
from backend.physics_engine.cavity_model import resonant_frequency_hz


class TestRadiationConductance:
    """Verify radiation conductance is positive and reasonable."""

    def test_positive(self) -> None:
        g1 = radiation_conductance(38e-3, 2.4e9)
        assert g1 > 0

    def test_wider_patch_higher_conductance(self) -> None:
        g_narrow = radiation_conductance(15e-3, 2.4e9)
        g_wide = radiation_conductance(38e-3, 2.4e9)
        assert g_wide > g_narrow


class TestDirectivity:
    """Verify directivity is in expected range for rectangular patches."""

    def test_typical_range(self) -> None:
        """Directivity should be 3–10 for typical patches (5–10 dBi)."""
        d0 = directivity(38e-3, 2.4e9)
        assert 2.0 <= d0 <= 15.0

    def test_wider_patch_higher_directivity(self) -> None:
        """Wider patch → higher directivity."""
        d_narrow = directivity(15e-3, 2.4e9)
        d_wide = directivity(38e-3, 2.4e9)
        assert d_wide > d_narrow


class TestRadiationEfficiency:
    """Verify radiation efficiency behavior."""

    def test_between_0_and_1(self) -> None:
        eta = radiation_efficiency(2.4e9, 1.6e-3, 4.4, 0.02, 38e-3)
        assert 0.0 < eta <= 1.0

    def test_fr4_lower_than_rogers(self) -> None:
        """FR4 (tanδ=0.02) should have lower efficiency than Rogers (tanδ=0.0009)."""
        eta_fr4 = radiation_efficiency(2.4e9, 1.6e-3, 4.4, 0.02, 38e-3)
        eta_rogers = radiation_efficiency(2.4e9, 0.787e-3, 2.2, 0.0009, 15e-3)
        assert eta_rogers > eta_fr4

    def test_lower_loss_tangent_higher_efficiency(self) -> None:
        """Lower tanδ → higher efficiency, all else equal."""
        eta_lossy = radiation_efficiency(5e9, 1.6e-3, 4.4, 0.05, 30e-3)
        eta_low_loss = radiation_efficiency(5e9, 1.6e-3, 4.4, 0.001, 30e-3)
        assert eta_low_loss > eta_lossy


class TestGainDbi:
    """Verify gain output is in expected range."""

    def test_fr4_patch_gain_range(self) -> None:
        """FR4 patch gain should be 2–8 dBi."""
        g = gain_dbi(29e-3, 38e-3, 1.6e-3, 4.4, 0.02)
        assert 0.0 <= g <= 10.0, f"Gain = {g:.2f} dBi, expected 0–10"

    def test_rogers_patch_gain_range(self) -> None:
        """Rogers patch gain should be 2–8 dBi."""
        g = gain_dbi(12e-3, 15e-3, 0.787e-3, 2.2, 0.0009)
        assert 0.0 <= g <= 10.0, f"Gain = {g:.2f} dBi, expected 0–10"

    def test_physical_bounds(self) -> None:
        """Gain should never exceed 12 dBi for a single rectangular patch."""
        g = gain_dbi(29e-3, 38e-3, 1.6e-3, 4.4, 0.02)
        assert g <= 12.0

    def test_gain_positive_for_standard_configs(self) -> None:
        """Gain should be positive (> 0 dBi) for well-designed patches."""
        configs = [
            (29e-3, 38e-3, 1.6e-3, 4.4, 0.02),     # FR4 WiFi
            (12e-3, 15e-3, 0.787e-3, 2.2, 0.0009),  # Rogers 5880
            (14e-3, 18e-3, 0.813e-3, 3.55, 0.0027),  # RO4003C
        ]
        for l, w, h, eps, td in configs:
            g = gain_dbi(l, w, h, eps, td)
            assert g > 0, f"Gain = {g:.2f} dBi for config L={l*1e3}mm"
