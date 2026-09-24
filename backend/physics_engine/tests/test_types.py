"""Tests for physics engine types and constants."""
import numpy as np
import pytest

from backend.physics_engine.types import (
    AntennaConfig,
    DGSSlot,
    FeedConfig,
    PatchConfig,
    SubstrateConfig,
    SUBSTRATES,
)
from backend.physics_engine.constants import c, epsilon_0, mu_0, sigma_copper, eta_0


# --- Constants tests ---

class TestConstants:
    """Verify physical constants are in expected ranges."""

    def test_speed_of_light(self) -> None:
        assert 2.99e8 < c < 3.01e8, "Speed of light out of range"

    def test_epsilon_0(self) -> None:
        assert 8.85e-12 < epsilon_0 < 8.86e-12

    def test_mu_0(self) -> None:
        expected = 4 * np.pi * 1e-7
        assert abs(mu_0 - expected) < 1e-15

    def test_sigma_copper(self) -> None:
        assert 5.7e7 < sigma_copper < 5.9e7

    def test_eta_0(self) -> None:
        assert 376 < eta_0 < 378, "Free-space impedance out of range"


# --- Type tests ---

class TestSubstrateConfig:
    """Verify SubstrateConfig dataclass."""

    def test_creation(self) -> None:
        sub = SubstrateConfig(
            width_mm=40.0, length_mm=40.0, height_mm=1.6,
            epsilon_r=4.4, tan_delta=0.02,
        )
        assert sub.width_mm == 40.0
        assert sub.epsilon_r == 4.4

    def test_all_fields_required(self) -> None:
        with pytest.raises(TypeError):
            SubstrateConfig(width_mm=40.0)  # type: ignore[call-arg]


class TestPatchConfig:
    """Verify PatchConfig dataclass."""

    def test_creation(self) -> None:
        patch = PatchConfig(width_mm=30.0, length_mm=23.0)
        assert patch.width_mm == 30.0
        assert patch.length_mm == 23.0


class TestFeedConfig:
    """Verify FeedConfig dataclass with default inset."""

    def test_default_inset(self) -> None:
        feed = FeedConfig(width_mm=3.0)
        assert feed.inset_mm == 0.0

    def test_explicit_inset(self) -> None:
        feed = FeedConfig(width_mm=3.0, inset_mm=7.0)
        assert feed.inset_mm == 7.0


class TestDGSSlot:
    """Verify DGSSlot dataclass."""

    def test_creation(self) -> None:
        slot = DGSSlot(width_mm=2.0, length_mm=8.0, x_mm=20.0, y_mm=20.0)
        assert slot.width_mm == 2.0
        assert slot.x_mm == 20.0


class TestAntennaConfig:
    """Verify AntennaConfig with optional slots."""

    def test_no_slots(self) -> None:
        config = AntennaConfig(
            substrate=SubstrateConfig(40, 40, 1.6, 4.4, 0.02),
            patch=PatchConfig(30, 23),
            feed=FeedConfig(3.0),
        )
        assert len(config.slots) == 0

    def test_with_slots(self) -> None:
        config = AntennaConfig(
            substrate=SubstrateConfig(40, 40, 1.6, 4.4, 0.02),
            patch=PatchConfig(30, 23),
            feed=FeedConfig(3.0),
            slots=[
                DGSSlot(2.0, 8.0, 15.0, 15.0),
                DGSSlot(2.0, 8.0, 25.0, 25.0),
            ],
        )
        assert len(config.slots) == 2

    def test_slots_independent(self) -> None:
        """Ensure default factory creates independent lists."""
        config1 = AntennaConfig(
            substrate=SubstrateConfig(40, 40, 1.6, 4.4, 0.02),
            patch=PatchConfig(30, 23),
            feed=FeedConfig(3.0),
        )
        config2 = AntennaConfig(
            substrate=SubstrateConfig(40, 40, 1.6, 4.4, 0.02),
            patch=PatchConfig(30, 23),
            feed=FeedConfig(3.0),
        )
        config1.slots.append(DGSSlot(1, 1, 1, 1))
        assert len(config2.slots) == 0, "Mutable default sharing detected"


class TestSubstratePresets:
    """Verify substrate material presets."""

    def test_fr4_exists(self) -> None:
        assert "FR4" in SUBSTRATES
        assert SUBSTRATES["FR4"]["epsilon_r"] == 4.4
        assert SUBSTRATES["FR4"]["tan_delta"] == 0.02

    def test_rogers_5880_exists(self) -> None:
        assert "Rogers RT5880" in SUBSTRATES
        assert SUBSTRATES["Rogers RT5880"]["epsilon_r"] == 2.2

    def test_all_presets_have_required_keys(self) -> None:
        for name, props in SUBSTRATES.items():
            assert "epsilon_r" in props, f"{name} missing epsilon_r"
            assert "tan_delta" in props, f"{name} missing tan_delta"
            assert props["epsilon_r"] > 1.0, f"{name} epsilon_r must be > 1"
            assert props["tan_delta"] > 0, f"{name} tan_delta must be > 0"
