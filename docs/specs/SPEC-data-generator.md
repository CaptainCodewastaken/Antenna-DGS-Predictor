# Spec: data-generator

> **Module ID:** `data-generator`  
> **Capability Map:** [capability_map.md](file:///Users/himaghnaroy/.gemini/antigravity-ide/brain/b5b0a198-c758-41d8-a785-cb83ea463b44/capability_map.md)  
> **Depends on:** `physics-engine`  
> **Consumed by:** `ml-models`

---

## Objective

Generate a large, physically valid dataset of rectangular microstrip patch antenna configurations and their computed performance metrics using the physics engine. This dataset is the sole training source for all ML models. Every sample must satisfy physical constraints — no impossible geometries, no unphysical outputs.

### Key Requirements
1. **Volume:** 5,000–10,000 samples (configurable)
2. **Coverage:** Parameter space must be well-covered via Latin Hypercube Sampling (LHS) — not naive uniform random
3. **Validity:** Every sample passes physical constraint checks before inclusion
4. **Reproducibility:** Deterministic with a fixed random seed
5. **DGS variation:** Mix of no-slot, 1-slot, and 2-slot configurations

---

## Tech Stack

- **Language:** Python 3.10+
- **Dependencies:** NumPy, SciPy (for LHS), Pandas, `physics-engine` module
- **Output format:** CSV and Parquet (Parquet for ML training, CSV for human inspection)

---

## Commands

```bash
# Generate the full dataset (default: 10,000 samples)
python -m backend.data_generator.generate --output backend/data/antenna_dataset.csv --samples 10000 --seed 42

# Generate a small test dataset
python -m backend.data_generator.generate --output backend/data/test_dataset.csv --samples 100 --seed 42

# Validate an existing dataset (check physical constraints)
python -m backend.data_generator.validate --input backend/data/antenna_dataset.csv

# Run tests
pytest backend/data_generator/tests/ -v
```

---

## Project Structure

```
backend/data_generator/
├── __init__.py
├── generate.py          # Main generation script (CLI entry point)
├── sampler.py           # LHS parameter sampling with physical constraints
├── validate.py          # Dataset validation: check all physical constraints
├── constraints.py       # Physical constraint definitions and checks
├── tests/
│   ├── test_sampler.py
│   ├── test_constraints.py
│   └── test_generate.py
```

---

## Parameter Space

### Input Parameters (Features)

| Parameter | Symbol | Range | Unit | Constraint |
|-----------|--------|-------|------|------------|
| Substrate width | `Sub_W` | 20–60 | mm | > Patch_W + 5 |
| Substrate length | `Sub_L` | 20–60 | mm | > Patch_L + 5 |
| Substrate height | `Sub_H` | 0.5–3.2 | mm | Standard PCB thicknesses |
| Substrate permittivity | `Epsilon_r` | 2.2–10.2 | — | From SUBSTRATES preset list |
| Loss tangent | `Tan_delta` | 0.0009–0.02 | — | Paired with Epsilon_r |
| Patch width | `Patch_W` | 8–45 | mm | < Sub_W - 5 |
| Patch length | `Patch_L` | 8–45 | mm | < Sub_L - 5 |
| Feed width | `Feed_W` | 0.5–5.0 | mm | Microstrip feed line |
| Feed inset | `Feed_Inset` | 0–Patch_L/3 | mm | For 50Ω matching |
| Number of slots | `Num_Slots` | 0, 1, 2 | — | Distribution: 30% no-slot, 40% 1-slot, 30% 2-slot |
| Slot 1 width | `Slot1_W` | 0.5–5.0 | mm | < Sub_W/3 (if present) |
| Slot 1 length | `Slot1_L` | 1.0–15.0 | mm | < Sub_L/3 (if present) |
| Slot 1 X position | `Slot1_X` | — | mm | Slot fully within ground plane |
| Slot 1 Y position | `Slot1_Y` | — | mm | Slot fully within ground plane |
| Slot 2 (same as Slot 1) | — | — | — | Non-overlapping with Slot 1 |

### Output Parameters (Targets)

| Parameter | Symbol | Expected Range | Unit |
|-----------|--------|---------------|------|
| Resonant frequency | `Freq_GHz` | 1.0–15.0 | GHz |
| Gain | `Gain_dBi` | 1.0–10.0 | dBi |

### Supplementary Outputs (stored but not ML targets)

| Parameter | Description |
|-----------|-------------|
| `Bandwidth_GHz` | -10 dB bandwidth from S₁₁ |
| `S11_min_dB` | Minimum S₁₁ at resonance |
| `DGS_delta_f` | Total frequency shift from DGS |

---

## Sampling Strategy

### Latin Hypercube Sampling (LHS)

Instead of naive uniform random sampling (which can leave gaps and create clusters), use **LHS** to ensure even coverage of the parameter space:

```python
from scipy.stats.qmc import LatinHypercube

sampler = LatinHypercube(d=num_dimensions, seed=42)
samples = sampler.random(n=num_samples)
# Scale to physical ranges
```

### Substrate Material Sampling

Don't uniformly sample `ε_r` — sample from the **preset list** to produce realistic configurations:

| Material | ε_r | tan_delta | Probability |
|----------|-----|-----------|-------------|
| FR4 | 4.4 | 0.02 | 40% |
| Rogers RT5880 | 2.2 | 0.0009 | 20% |
| Rogers RO4003C | 3.55 | 0.0027 | 20% |
| Rogers RO3010 | 10.2 | 0.0022 | 10% |
| Custom | Uniform(2.0, 12.0) | Uniform(0.001, 0.025) | 10% |

---

## Physical Constraints (`constraints.py`)

Every generated sample MUST pass all of these:

```python
def validate_sample(sample: dict) -> bool:
    """Return True if sample is physically valid."""
    # 1. Patch fits inside substrate (with margin)
    assert sample["Patch_W"] < sample["Sub_W"] - 4.0  # 2mm margin each side
    assert sample["Patch_L"] < sample["Sub_L"] - 4.0

    # 2. Substrate height is realistic
    assert 0.2 <= sample["Sub_H"] <= 5.0  # mm

    # 3. Computed frequency is in realistic range
    assert 0.5 <= sample["Freq_GHz"] <= 20.0

    # 4. Computed gain is in realistic range
    assert 0.0 <= sample["Gain_dBi"] <= 12.0

    # 5. Slots fit inside ground plane
    for slot in sample.get("slots", []):
        assert slot_within_ground_plane(slot, sample["Sub_W"], sample["Sub_L"])

    # 6. Slots don't overlap each other
    if sample["Num_Slots"] == 2:
        assert not slots_overlap(sample["slots"][0], sample["slots"][1])

    # 7. Feed width is physically reasonable
    assert sample["Feed_W"] < sample["Patch_W"] / 2

    return True
```

Samples that fail validation are **discarded and regenerated** (rejection sampling). Target: <5% rejection rate with well-tuned parameter ranges.

---

## Output Schema (CSV)

```csv
Sub_W,Sub_L,Sub_H,Epsilon_r,Tan_delta,Patch_W,Patch_L,Feed_W,Feed_Inset,Num_Slots,Slot1_W,Slot1_L,Slot1_X,Slot1_Y,Slot2_W,Slot2_L,Slot2_X,Slot2_Y,Freq_GHz,Gain_dBi,Bandwidth_GHz,S11_min_dB,DGS_delta_f
```

For samples with 0 or 1 slots, absent slot columns are filled with 0.0.

---

## Code Style

Same as `physics-engine`: type hints, logging, docstrings, SI units internally.

```python
import logging
import numpy as np
import pandas as pd
from backend.physics_engine import full_analysis
from backend.physics_engine.types import AntennaConfig

logger = logging.getLogger(__name__)

def generate_dataset(
    num_samples: int = 10_000,
    seed: int = 42,
    output_path: str = "backend/data/antenna_dataset.csv",
) -> pd.DataFrame:
    """Generate antenna dataset using physics engine with LHS sampling."""
    logger.info(f"Generating {num_samples} samples with seed={seed}")
    # ... implementation
```

---

## Testing Strategy

**Framework:** pytest  
**Coverage target:** ≥90%

| Category | What it tests |
|----------|--------------|
| **Constraint enforcement** | Every generated sample passes `validate_sample()` |
| **LHS coverage** | No dimension has >10% of samples in any 10% bin (no clustering) |
| **Determinism** | Same seed → identical dataset |
| **DGS distribution** | ~30/40/30 split for 0/1/2 slots |
| **Material distribution** | Substrate materials appear in expected proportions |
| **Output ranges** | All frequencies in [0.5, 20] GHz, all gains in [0, 12] dBi |
| **No NaN/Inf** | Zero NaN or Inf values in the entire dataset |
| **Schema** | CSV columns match expected schema exactly |

---

## Boundaries

### Always Do
- Run `validate_sample()` on every sample before writing to output
- Use LHS, never naive uniform random
- Log rejection rate and warn if >10%
- Include `--seed` flag for reproducibility

### Ask First
- Changing parameter ranges
- Adding new output columns
- Switching from rejection sampling to a different strategy

### Never Do
- Include physically invalid samples in the dataset
- Use `iterrows()` or Python loops over the DataFrame — vectorize
- Hardcode file paths (use CLI arguments)

---

## Success Criteria

1. Generates 10,000 valid samples in <5 minutes
2. Zero NaN/Inf values in the output
3. Rejection rate <5%
4. All physical constraints pass on 100% of samples
5. LHS coverage verified: KS-test p-value > 0.05 for each dimension (uniform marginals)
6. Dataset saved as both CSV and Parquet
7. Reproducible: same seed produces byte-identical output
