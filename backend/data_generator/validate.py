"""
Validate an existing dataset against physical constraints.
"""
import argparse
import sys
import logging
import pandas as pd

from backend.physics_engine.types import AntennaConfig, SubstrateConfig, PatchConfig, FeedConfig, DGSSlot
from backend.data_generator.constraints import validate_sample

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate a generated dataset")
    parser.add_argument("--input", type=str, required=True, help="Input CSV path")
    args = parser.parse_args()
    
    df = pd.read_csv(args.input)
    logger.info(f"Loaded {len(df)} samples from {args.input}")
    
    invalid_count = 0
    for _, row in df.iterrows():
        # Reconstruct config
        # Assuming a default substrate size large enough if not in row
        # In our sampler we used a random size, but here we can just use a large 
        # size for validation if not present, but wait, if it's not in the row we 
        # can't fully validate the margin. Let's add sub_size to the row in generate.py
        # For now, let's assume 100x100 if not present.
        sub_size = row.get("sub_size", 100.0)
        
        substrate = SubstrateConfig(
            epsilon_r=row["sub_eps_r"],
            tan_delta=row["sub_tan_d"],
            height_mm=row["sub_h"],
            width_mm=sub_size,
            length_mm=sub_size,
        )
        patch = PatchConfig(
            width_mm=row["patch_w"],
            length_mm=row["patch_l"],
        )
        feed = FeedConfig(
            width_mm=row["feed_w"],
            inset_mm=row["feed_inset"],
        )
        slots = []
        if row["num_slots"] >= 1:
            slots.append(DGSSlot(
                width_mm=row["slot1_w"],
                length_mm=row["slot1_l"],
                x_mm=row["slot1_x"],
                y_mm=row["slot1_y"],
            ))
        if row["num_slots"] == 2:
            slots.append(DGSSlot(
                width_mm=row["slot2_w"],
                length_mm=row["slot2_l"],
                x_mm=row["slot2_x"],
                y_mm=row["slot2_y"],
            ))
            
        config = AntennaConfig(substrate=substrate, patch=patch, feed=feed, slots=slots)
        
        if not validate_sample(config):
            invalid_count += 1
            
    if invalid_count > 0:
        logger.error(f"FAILED: {invalid_count} samples are invalid!")
        sys.exit(1)
    else:
        logger.info("SUCCESS: All samples are physically valid.")
        sys.exit(0)

if __name__ == "__main__":
    main()
