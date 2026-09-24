"""Tests for the Latin Hypercube Sampler."""
import numpy as np

from backend.data_generator.sampler import sample_parameters
from backend.data_generator.constraints import validate_sample

def test_returns_correct_number() -> None:
    samples = sample_parameters(10)
    assert len(samples) == 10

def test_samples_are_valid() -> None:
    samples = sample_parameters(20)
    for sample in samples:
        assert validate_sample(sample)

def test_determinism() -> None:
    samples1 = sample_parameters(5, seed=42)
    samples2 = sample_parameters(5, seed=42)
    
    # Just check a few properties to ensure they match
    for s1, s2 in zip(samples1, samples2):
        assert s1.patch.width_mm == s2.patch.width_mm
        assert s1.substrate.epsilon_r == s2.substrate.epsilon_r
        assert len(s1.slots) == len(s2.slots)

def test_diverse_slot_counts() -> None:
    samples = sample_parameters(100)
    slot_counts = [len(s.slots) for s in samples]
    
    # Should have a mix of 0, 1, and 2 slots
    assert 0 in slot_counts
    assert 1 in slot_counts
    assert 2 in slot_counts
