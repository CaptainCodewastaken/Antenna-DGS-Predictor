"""Tests for the DGS perturbation model."""
import pytest

from backend.physics_engine.dgs_model import (
    dgs_lc_equivalent,
    dgs_frequency_shift,
    dgs_gain_penalty,
    dgs_bandwidth_multiplier,
)
from backend.physics_engine.types import DGSSlot


class TestDGSLcEquivalent:
    def test_positive_values(self) -> None:
        slot = DGSSlot(length_mm=10.0, width_mm=2.0, x_mm=0.0, y_mm=0.0)
        l_dgs, c_dgs = dgs_lc_equivalent(slot, 1.6e-3, 4.4)
        assert l_dgs > 0
        assert c_dgs > 0


class TestDGSFrequencyShift:
    def test_no_slots(self) -> None:
        f = dgs_frequency_shift(2.4e9, [], 1.6e-3, 4.4)
        assert f == 2.4e9

    def test_shift_down(self) -> None:
        slot = DGSSlot(length_mm=15.0, width_mm=2.0, x_mm=0.0, y_mm=0.0)
        f = dgs_frequency_shift(2.4e9, [slot], 1.6e-3, 4.4)
        assert f < 2.4e9
        # Max reduction shouldn't be crazy
        assert f > 2.4e9 * 0.7

    def test_more_slots_more_shift(self) -> None:
        slot1 = DGSSlot(length_mm=10.0, width_mm=2.0, x_mm=0.0, y_mm=0.0)
        slot2 = DGSSlot(length_mm=10.0, width_mm=2.0, x_mm=10.0, y_mm=0.0)
        f_one = dgs_frequency_shift(2.4e9, [slot1], 1.6e-3, 4.4)
        f_two = dgs_frequency_shift(2.4e9, [slot1, slot2], 1.6e-3, 4.4)
        
        assert f_two < f_one


class TestDGSGainPenalty:
    def test_no_slots(self) -> None:
        p = dgs_gain_penalty([], 30e-3, 30e-3)
        assert p == 0.0

    def test_penalty_is_negative(self) -> None:
        slot = DGSSlot(length_mm=10.0, width_mm=5.0, x_mm=0.0, y_mm=0.0)
        p = dgs_gain_penalty([slot], 30e-3, 30e-3)
        assert p < 0.0

    def test_larger_slot_more_penalty(self) -> None:
        slot_small = DGSSlot(length_mm=5.0, width_mm=2.0, x_mm=0.0, y_mm=0.0)
        slot_large = DGSSlot(length_mm=20.0, width_mm=5.0, x_mm=0.0, y_mm=0.0)
        
        p_small = dgs_gain_penalty([slot_small], 30e-3, 30e-3)
        p_large = dgs_gain_penalty([slot_large], 30e-3, 30e-3)
        
        assert p_large < p_small  # more negative


class TestDGSBandwidthMultiplier:
    def test_no_slots(self) -> None:
        m = dgs_bandwidth_multiplier([], 30e-3, 30e-3)
        assert m == 1.0

    def test_reduction(self) -> None:
        slot = DGSSlot(length_mm=10.0, width_mm=5.0, x_mm=0.0, y_mm=0.0)
        m = dgs_bandwidth_multiplier([slot], 30e-3, 30e-3)
        assert 0.5 <= m < 1.0

    def test_larger_slot_more_reduction(self) -> None:
        slot_small = DGSSlot(length_mm=5.0, width_mm=2.0, x_mm=0.0, y_mm=0.0)
        slot_large = DGSSlot(length_mm=20.0, width_mm=5.0, x_mm=0.0, y_mm=0.0)
        
        m_small = dgs_bandwidth_multiplier([slot_small], 30e-3, 30e-3)
        m_large = dgs_bandwidth_multiplier([slot_large], 30e-3, 30e-3)
        
        assert m_large < m_small
