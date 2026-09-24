"""Tests for cavity model: effective permittivity, fringing, and resonant frequency."""
import numpy as np
import pytest

from backend.physics_engine.cavity_model import (
    effective_permittivity,
    fringing_extension,
    resonant_frequency_hz,
)


class TestEffectivePermittivity:
    """Verify Hammerstad effective permittivity formula."""

    def test_fr4_typical(self) -> None:
        """FR4 (ε_r=4.4), h=1.6mm, W=38mm → ε_eff should be between 1 and ε_r."""
        eps_eff = effective_permittivity(4.4, 1.6e-3, 38e-3)
        assert 1.0 < eps_eff < 4.4
        # Expected ~4.08 for wide patch on FR4
        assert 3.8 < eps_eff < 4.3

    def test_rogers_5880(self) -> None:
        """Rogers RT5880 (ε_r=2.2), h=0.787mm, W=15mm."""
        eps_eff = effective_permittivity(2.2, 0.787e-3, 15e-3)
        assert 1.0 < eps_eff < 2.2

    def test_higher_epsilon_r_gives_higher_epsilon_eff(self) -> None:
        """ε_eff increases with ε_r, all else equal."""
        h, w = 1.6e-3, 30e-3
        eps_low = effective_permittivity(2.2, h, w)
        eps_high = effective_permittivity(4.4, h, w)
        assert eps_high > eps_low

    def test_wider_patch_gives_higher_epsilon_eff(self) -> None:
        """Wider patch → more field in substrate → higher ε_eff."""
        h, eps_r = 1.6e-3, 4.4
        eps_narrow = effective_permittivity(eps_r, h, 10e-3)
        eps_wide = effective_permittivity(eps_r, h, 40e-3)
        assert eps_wide > eps_narrow

    def test_invalid_inputs(self) -> None:
        """Negative or zero dimensions raise ValueError."""
        with pytest.raises(ValueError):
            effective_permittivity(4.4, 0, 30e-3)
        with pytest.raises(ValueError):
            effective_permittivity(4.4, 1.6e-3, -1e-3)
        with pytest.raises(ValueError):
            effective_permittivity(0.5, 1.6e-3, 30e-3)


class TestFringingExtension:
    """Verify Hammerstad fringing extension formula."""

    def test_positive_extension(self) -> None:
        """ΔL must always be positive."""
        eps_eff = effective_permittivity(4.4, 1.6e-3, 38e-3)
        delta_l = fringing_extension(eps_eff, 1.6e-3, 38e-3)
        assert delta_l > 0

    def test_extension_proportional_to_height(self) -> None:
        """Thicker substrate → larger fringing extension."""
        eps_eff_thin = effective_permittivity(4.4, 0.8e-3, 30e-3)
        eps_eff_thick = effective_permittivity(4.4, 3.2e-3, 30e-3)
        dl_thin = fringing_extension(eps_eff_thin, 0.8e-3, 30e-3)
        dl_thick = fringing_extension(eps_eff_thick, 3.2e-3, 30e-3)
        assert dl_thick > dl_thin

    def test_reasonable_magnitude(self) -> None:
        """ΔL should be a fraction of the substrate height (typically 0.3h to 0.5h)."""
        h = 1.6e-3
        eps_eff = effective_permittivity(4.4, h, 38e-3)
        delta_l = fringing_extension(eps_eff, h, 38e-3)
        ratio = delta_l / h
        assert 0.1 < ratio < 1.0, f"ΔL/h = {ratio} out of expected range"


class TestResonantFrequency:
    """Verify resonant frequency against known textbook values."""

    def test_fr4_wifi_2_4ghz(self) -> None:
        """
        FR4 patch designed for 2.4 GHz WiFi.
        ε_r=4.4, h=1.6mm, W=38mm, L=29mm.
        Expected f_r ≈ 2.4 GHz (±5%).
        """
        f_r = resonant_frequency_hz(
            patch_l=29e-3, patch_w=38e-3,
            sub_h=1.6e-3, epsilon_r=4.4,
        )
        f_ghz = f_r / 1e9
        assert 2.28 <= f_ghz <= 2.52, f"f_r = {f_ghz:.3f} GHz, expected ~2.4"

    def test_rogers_5880_high_freq(self) -> None:
        """
        Rogers RT5880 patch for ~8.5 GHz.
        ε_r=2.2, h=0.787mm, W=15mm, L=12mm.
        Expected f_r ≈ 8.0–9.0 GHz (±5%).
        """
        f_r = resonant_frequency_hz(
            patch_l=12e-3, patch_w=15e-3,
            sub_h=0.787e-3, epsilon_r=2.2,
        )
        f_ghz = f_r / 1e9
        assert 7.5 <= f_ghz <= 9.5, f"f_r = {f_ghz:.3f} GHz, expected ~8.5"

    def test_rogers_4003c_5_8ghz(self) -> None:
        """
        Rogers RO4003C patch for ~5.8 GHz.
        ε_r=3.55, h=0.813mm, W=18mm, L=14mm.
        Expected f_r ≈ 5.5–6.5 GHz.
        """
        f_r = resonant_frequency_hz(
            patch_l=14e-3, patch_w=18e-3,
            sub_h=0.813e-3, epsilon_r=3.55,
        )
        f_ghz = f_r / 1e9
        assert 5.0 <= f_ghz <= 7.0, f"f_r = {f_ghz:.3f} GHz, expected ~5.8"

    def test_monotonicity_length(self) -> None:
        """Increasing patch length → decreasing resonant frequency."""
        lengths = np.linspace(15e-3, 40e-3, 20)
        freqs = [
            resonant_frequency_hz(l, 30e-3, 1.6e-3, 4.4) for l in lengths
        ]
        # Each frequency should be less than the previous
        for i in range(1, len(freqs)):
            assert freqs[i] < freqs[i - 1], (
                f"Non-monotonic at L={lengths[i]*1e3:.1f}mm: "
                f"f[{i}]={freqs[i]/1e9:.3f} >= f[{i-1}]={freqs[i-1]/1e9:.3f}"
            )

    def test_monotonicity_epsilon_r(self) -> None:
        """Higher ε_r → lower resonant frequency (slower wave)."""
        f_low_eps = resonant_frequency_hz(29e-3, 38e-3, 1.6e-3, 2.2)
        f_high_eps = resonant_frequency_hz(29e-3, 38e-3, 1.6e-3, 4.4)
        assert f_high_eps < f_low_eps

    def test_frequency_in_realistic_range(self) -> None:
        """Typical patch antennas resonate between 0.5 and 20 GHz."""
        f_r = resonant_frequency_hz(29e-3, 38e-3, 1.6e-3, 4.4)
        f_ghz = f_r / 1e9
        assert 0.5 <= f_ghz <= 20.0

    def test_invalid_dimensions(self) -> None:
        """Zero or negative dimensions raise ValueError."""
        with pytest.raises(ValueError):
            resonant_frequency_hz(0, 30e-3, 1.6e-3, 4.4)
        with pytest.raises(ValueError):
            resonant_frequency_hz(29e-3, -1, 1.6e-3, 4.4)
