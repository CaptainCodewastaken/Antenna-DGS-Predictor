"""Tests for physical constraints."""
from backend.physics_engine.types import (
    AntennaConfig, SubstrateConfig, PatchConfig, FeedConfig, DGSSlot
)
from backend.data_generator.constraints import validate_sample

def _get_base_config() -> AntennaConfig:
    return AntennaConfig(
        substrate=SubstrateConfig(epsilon_r=4.4, height_mm=1.6, tan_delta=0.02, width_mm=60.0, length_mm=60.0),
        patch=PatchConfig(width_mm=38.0, length_mm=29.0),
        feed=FeedConfig(width_mm=3.0, inset_mm=8.0),
        slots=[],
    )

def test_valid_base() -> None:
    config = _get_base_config()
    assert validate_sample(config)

def test_patch_too_large() -> None:
    config = _get_base_config()
    config.patch.width_mm = 70.0  # Larger than substrate
    assert not validate_sample(config)

def test_feed_too_wide() -> None:
    config = _get_base_config()
    config.feed.width_mm = 40.0  # Larger than patch width
    assert not validate_sample(config)

def test_inset_too_deep() -> None:
    config = _get_base_config()
    config.feed.inset_mm = 20.0  # > length/2 (29/2 = 14.5)
    assert not validate_sample(config)

def test_slot_out_of_bounds() -> None:
    config = _get_base_config()
    # Substrate is 60x60, so bounds are -30 to +30.
    config.slots = [DGSSlot(width_mm=5.0, length_mm=15.0, x_mm=25.0, y_mm=0.0)]
    # x + length/2 = 25 + 7.5 = 32.5 > 30
    assert not validate_sample(config)

def test_slots_overlap() -> None:
    config = _get_base_config()
    s1 = DGSSlot(width_mm=5.0, length_mm=10.0, x_mm=0.0, y_mm=0.0)
    s2 = DGSSlot(width_mm=5.0, length_mm=10.0, x_mm=5.0, y_mm=0.0)
    # They overlap from x=2.5 to x=5.0
    config.slots = [s1, s2]
    assert not validate_sample(config)
