"""
Dataset Generation CLI.

Generates a dataset of synthetic antenna configurations and computes their
physical performance metrics using the physics engine.
"""
import argparse
import logging
from pathlib import Path

import pandas as pd

from backend.data_generator.sampler import sample_parameters
from backend.physics_engine import calculate_antenna_metrics
from backend.physics_engine.types import AntennaConfig

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger(__name__)


def flatten_config(config: AntennaConfig, metrics: dict[str, float]) -> dict:
    """Flatten configuration and metrics into a single row."""
    row = {
        "sub_eps_r": config.substrate.epsilon_r,
        "sub_tan_d": config.substrate.tan_delta,
        "sub_h": config.substrate.height_mm,
        "sub_size": config.substrate.width_mm,
        "patch_l": config.patch.length_mm,
        "patch_w": config.patch.width_mm,
        "feed_w": config.feed.width_mm,
        "feed_inset": config.feed.inset_mm,
        "num_slots": len(config.slots),
    }

    for i in range(2):
        s = config.slots[i] if i < len(config.slots) else None
        prefix = f"slot{i+1}_"
        row.update({
            f"{prefix}l": s.length_mm if s else 0.0,
            f"{prefix}w": s.width_mm if s else 0.0,
            f"{prefix}x": s.x_mm if s else 0.0,
            f"{prefix}y": s.y_mm if s else 0.0,
        })

    # Metrics
    row.update(metrics)
    
    return row


def generate_dataset(n_samples: int, seed: int, output_path: str) -> None:
    """Generate and save the dataset."""
    logger.info(f"Sampling {n_samples} configurations (seed={seed})...")
    configs = sample_parameters(n_samples, seed)
    
    logger.info("Computing physics metrics...")
    data = []
    for i, config in enumerate(configs):
        if i > 0 and i % 1000 == 0:
            logger.info(f"Processed {i}/{n_samples}...")
            
        metrics = calculate_antenna_metrics(config)
        row = flatten_config(config, metrics)
        data.append(row)
        
    df = pd.DataFrame(data)
    
    # Save CSV
    out_csv = Path(output_path)
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_csv, index=False)
    
    # Save Parquet
    out_parquet = out_csv.with_suffix(".parquet")
    df.to_parquet(out_parquet, index=False)
    
    logger.info(f"Dataset generated successfully.")
    logger.info(f"Saved to {out_csv} and {out_parquet}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate synthetic antenna dataset")
    parser.add_argument("--samples", type=int, default=1000, help="Number of samples")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--output", type=str, required=True, help="Output CSV path")
    
    args = parser.parse_args()
    generate_dataset(args.samples, args.seed, args.output)


if __name__ == "__main__":
    main()
