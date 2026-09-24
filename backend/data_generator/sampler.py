"""
Latin Hypercube Sampler for Antenna Configurations.

Draws constrained random samples from the parameter space of the antenna.
Uses SciPy's LatinHypercube for space-filling sampling.
"""
import logging
from typing import List, Dict, Any

import numpy as np
from scipy.stats import qmc

from backend.physics_engine.types import (
    AntennaConfig, SubstrateConfig, PatchConfig, FeedConfig, DGSSlot, SUBSTRATES
)
from backend.data_generator.constraints import validate_sample

logger = logging.getLogger(__name__)

# Define parameter bounds for sampling
BOUNDS = {
    "patch_l": (10.0, 50.0),      # mm
    "patch_w": (10.0, 60.0),      # mm
    "sub_size": (40.0, 100.0),    # mm (Square substrate)
    "feed_w": (1.5, 5.0),         # mm
    "inset_d": (0.0, 20.0),       # mm
    "slot1_l": (2.0, 30.0),       # mm
    "slot1_w": (0.5, 5.0),        # mm
    "slot1_x": (-20.0, 20.0),     # mm
    "slot1_y": (-20.0, 20.0),     # mm
    "slot2_l": (2.0, 30.0),       # mm
    "slot2_w": (0.5, 5.0),        # mm
    "slot2_x": (-20.0, 20.0),     # mm
    "slot2_y": (-20.0, 20.0),     # mm
}

# Probabilities for discrete variables
SUBSTRATE_NAMES = list(SUBSTRATES.keys())
SUBSTRATE_PROBS = [0.4, 0.2, 0.2, 0.2]  # Weighted toward FR4

NUM_SLOTS_PROBS = [0.3, 0.4, 0.3]  # 0, 1, or 2 slots


def _scale_sample(val_01: float, bounds: tuple[float, float]) -> float:
    """Scale a [0,1] sample to the required bounds."""
    low, high = bounds
    return low + val_01 * (high - low)


def sample_parameters(n: int, seed: int = 42) -> List[AntennaConfig]:
    """
    Generate valid antenna configurations using LHS.

    Args:
        n: Number of valid samples to generate.
        seed: Random seed for reproducibility.

    Returns:
        List of physically valid AntennaConfig objects.
    """
    rng = np.random.default_rng(seed)
    
    # We may need to oversample because some will be rejected by constraints
    valid_samples: List[AntennaConfig] = []
    
    batch_size = max(n * 2, 100)
    
    # The continuous variables
    keys = list(BOUNDS.keys())
    num_vars = len(keys)
    
    sampler = qmc.LatinHypercube(d=num_vars, seed=seed)
    
    attempts = 0
    max_attempts = n * 100
    
    while len(valid_samples) < n and attempts < max_attempts:
        lhs_samples = sampler.random(n=batch_size)
        
        # Also sample discrete variables for this batch
        sub_choices = rng.choice(SUBSTRATE_NAMES, size=batch_size, p=SUBSTRATE_PROBS)
        slot_counts = rng.choice([0, 1, 2], size=batch_size, p=NUM_SLOTS_PROBS)
        
        for i in range(batch_size):
            attempts += 1
            if len(valid_samples) >= n:
                break
                
            # Build the continuous dict
            params = {}
            for j, key in enumerate(keys):
                params[key] = _scale_sample(lhs_samples[i, j], BOUNDS[key])
                
            # Discrete choices
            sub_name = sub_choices[i]
            sub_props = SUBSTRATES[sub_name]
            num_slots = slot_counts[i]
            
            # Construct the objects
            substrate = SubstrateConfig(
                epsilon_r=sub_props["epsilon_r"],
                tan_delta=sub_props["tan_delta"],
                height_mm=1.6 if sub_name == "FR4" else 0.8, # simplification
                width_mm=params["sub_size"],
                length_mm=params["sub_size"],
            )
            
            patch = PatchConfig(
                width_mm=params["patch_w"],
                length_mm=params["patch_l"],
            )
            
            feed = FeedConfig(
                width_mm=params["feed_w"],
                inset_mm=params["inset_d"],
            )
            
            slots = [
                DGSSlot(
                    width_mm=params[f"slot{i+1}_w"],
                    length_mm=params[f"slot{i+1}_l"],
                    x_mm=params[f"slot{i+1}_x"],
                    y_mm=params[f"slot{i+1}_y"],
                )
                for i in range(num_slots)
            ]
                
            config = AntennaConfig(
                substrate=substrate,
                patch=patch,
                feed=feed,
                slots=slots
            )
            
            if validate_sample(config):
                valid_samples.append(config)
                
    if len(valid_samples) < n:
        logger.warning(
            f"Only generated {len(valid_samples)} valid samples out of {n} "
            f"requested after {attempts} attempts."
        )
        
    return valid_samples
