"""Tests for impedance and bandwidth models."""
import numpy as np
import pytest

from backend.physics_engine.impedance_model import (
    input_impedance_edge,
    input_impedance_inset,
    compute_optimal_inset,
    impedance_bandwidth,
)
from backend.physics_engine.cavity_model import resonant_frequency_hz


class TestInputImpedanceEdge:
    """Verify edge impedance calculations."""

    def test_typical_range(self) -> None:
        """Edge impedance should typically be between 150 and 400 ohms."""
        r_edge = input_impedance_edge(38e-3, 2.4e9)
        assert 150.0 <= r_edge <= 400.0, f"R_edge = {r_edge:.1f}Ω"

    def test_wider_patch_lower_impedance(self) -> None:
        """Wider patches have lower edge impedance."""
        r_narrow = input_impedance_edge(20e-3, 2.4e9)
        r_wide = input_impedance_edge(40e-3, 2.4e9)
        assert r_wide < r_narrow


class TestInputImpedanceInset:
    """Verify inset impedance distribution (cosine squared)."""

    def test_edge_is_max(self) -> None:
        """y=0 should return r_edge."""
        r_in = input_impedance_inset(250.0, 30e-3, 0.0)
        assert r_in == pytest.approx(250.0)

    def test_center_is_zero(self) -> None:
        """y=L/2 should return 0."""
        r_in = input_impedance_inset(250.0, 30e-3, 15e-3)
        assert r_in == pytest.approx(0.0, abs=1e-5)

    def test_monotonic_decrease(self) -> None:
        """Resistance drops from edge to center."""
        r_edge = 250.0
        r_1 = input_impedance_inset(r_edge, 30e-3, 5e-3)
        r_2 = input_impedance_inset(r_edge, 30e-3, 10e-3)
        assert r_edge > r_1 > r_2 > 0.0

    def test_invalid_length(self) -> None:
        with pytest.raises(ValueError):
            input_impedance_inset(250.0, 0, 5e-3)


class TestComputeOptimalInset:
    """Verify optimal inset calculations for matching."""

    def test_matching_50_ohms(self) -> None:
        """Should find the point where R_in = 50."""
        r_edge = 250.0
        patch_l = 30e-3
        y0 = compute_optimal_inset(r_edge, patch_l, 50.0)
        
        # Verify by plugging back in
        r_matched = input_impedance_inset(r_edge, patch_l, y0)
        assert r_matched == pytest.approx(50.0)

    def test_target_greater_than_edge(self) -> None:
        """If target > edge, matching is impossible, should return 0."""
        y0 = compute_optimal_inset(200.0, 30e-3, 300.0)
        assert y0 == 0.0


class TestImpedanceBandwidth:
    """Verify bandwidth calculations."""

    def test_typical_range(self) -> None:
        """Bandwidth of typical patch is 1% to 5%."""
        f_r = resonant_frequency_hz(29e-3, 38e-3, 1.6e-3, 4.4)
        bw = impedance_bandwidth(f_r, 1.6e-3, 38e-3, 4.4, 0.02)
        assert 0.01 <= bw <= 0.08, f"BW = {bw*100:.2f}%"

    def test_thicker_substrate_wider_bandwidth(self) -> None:
        """Increasing h increases bandwidth."""
        f_r1 = resonant_frequency_hz(29e-3, 38e-3, 0.8e-3, 4.4)
        bw_thin = impedance_bandwidth(f_r1, 0.8e-3, 38e-3, 4.4, 0.02)
        
        f_r2 = resonant_frequency_hz(29e-3, 38e-3, 1.6e-3, 4.4)
        bw_thick = impedance_bandwidth(f_r2, 1.6e-3, 38e-3, 4.4, 0.02)
        
        assert bw_thick > bw_thin

    def test_lower_permittivity_wider_bandwidth(self) -> None:
        """Lower ε_r increases bandwidth."""
        f_r1 = resonant_frequency_hz(29e-3, 38e-3, 1.6e-3, 4.4)
        bw_high_eps = impedance_bandwidth(f_r1, 1.6e-3, 38e-3, 4.4, 0.02)
        
        f_r2 = resonant_frequency_hz(29e-3, 38e-3, 1.6e-3, 2.2)
        bw_low_eps = impedance_bandwidth(f_r2, 1.6e-3, 38e-3, 2.2, 0.0009)
        
        assert bw_low_eps > bw_high_eps
