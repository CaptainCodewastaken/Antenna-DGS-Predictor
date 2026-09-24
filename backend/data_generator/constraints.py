"""
Physical constraints for validating sampled antenna configurations.

Ensures that generated data points represent physically buildable and
simulate-able antennas.
"""
from typing import List

from backend.physics_engine.types import AntennaConfig, DGSSlot


def validate_sample(config: AntennaConfig) -> bool:
    """
    Validate that an antenna configuration is physically realistic.

    Checks:
    1. Substrate is larger than patch.
    2. Feed width is physically reasonable.
    3. Inset depth is within patch bounds.
    4. DGS slots fit within the ground plane.
    5. DGS slots do not overlap each other.

    Args:
        config: The generated antenna configuration.

    Returns:
        True if the configuration is physically valid, False otherwise.
    """
    # 1. Dimensions > 0
    if config.patch.length_mm <= 0 or config.patch.width_mm <= 0:
        return False
    if config.substrate.length_mm <= 0 or config.substrate.width_mm <= 0:
        return False
        
    # 2. Patch must fit on substrate (with some margin, say 2mm)
    margin = 2.0
    if config.patch.length_mm + margin > config.substrate.length_mm:
        return False
    if config.patch.width_mm + margin > config.substrate.width_mm:
        return False

    # 3. Feed constraints
    if config.feed.width_mm <= 0 or config.feed.width_mm > config.patch.width_mm:
        return False
    # Inset must not go deeper than half the patch length
    if config.feed.inset_mm < 0 or config.feed.inset_mm > config.patch.length_mm / 2.0:
        return False

    # 4. Slot constraints
    for slot in config.slots:
        if slot.length_mm <= 0 or slot.width_mm <= 0:
            return False
            
        # Slot must fit completely within substrate
        # Assuming (0,0) is center of substrate for slot coordinates
        # Then slot edges are x_mm ± length_mm/2, y_mm ± width_mm/2
        # Actually, let's say slots are length along X, width along Y.
        half_sub_l = config.substrate.length_mm / 2.0
        half_sub_w = config.substrate.width_mm / 2.0
        
        # We need to make sure we know orientation. Let's assume:
        # length_mm is along X, width_mm is along Y.
        slot_left = slot.x_mm - slot.length_mm / 2.0
        slot_right = slot.x_mm + slot.length_mm / 2.0
        slot_bottom = slot.y_mm - slot.width_mm / 2.0
        slot_top = slot.y_mm + slot.width_mm / 2.0
        
        if (slot_left < -half_sub_l or slot_right > half_sub_l or
            slot_bottom < -half_sub_w or slot_top > half_sub_w):
            return False

    # 5. Overlap constraints for multiple slots
    if len(config.slots) == 2:
        s1 = config.slots[0]
        s2 = config.slots[1]
        
        s1_left = s1.x_mm - s1.length_mm / 2.0
        s1_right = s1.x_mm + s1.length_mm / 2.0
        s1_bottom = s1.y_mm - s1.width_mm / 2.0
        s1_top = s1.y_mm + s1.width_mm / 2.0
        
        s2_left = s2.x_mm - s2.length_mm / 2.0
        s2_right = s2.x_mm + s2.length_mm / 2.0
        s2_bottom = s2.y_mm - s2.width_mm / 2.0
        s2_top = s2.y_mm + s2.width_mm / 2.0
        
        # Check if bounding boxes overlap
        overlap_x = s1_left < s2_right and s1_right > s2_left
        overlap_y = s1_bottom < s2_top and s1_top > s2_bottom
        
        if overlap_x and overlap_y:
            return False

    return True
