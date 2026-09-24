# Spec: physics-engine

> **Module ID:** `physics-engine`  
> **Capability Map:** [capability_map.md](file:///Users/himaghnaroy/.gemini/antigravity-ide/brain/b5b0a198-c758-41d8-a785-cb83ea463b44/capability_map.md)  
> **Depends on:** nothing (foundation module)  
> **Consumed by:** `data-generator`, `api`

---

## Objective

Build a pure-Python analytical physics engine that computes the electromagnetic performance of a rectangular microstrip patch antenna with optional rectangular-slot DGS (Defected Ground Structure). Every output must be grounded in published antenna theory — no black-box approximations or arbitrary scaling.

The engine must compute:
1. **Resonant frequency** (GHz) — cavity model with fringing corrections
2. **Gain** (dBi) — aperture/directivity model with radiation efficiency
3. **Full radiation pattern** — E(θ, φ) across the hemisphere for 2D polar and 3D surface plots
4. **S₁₁ return loss** — input impedance vs frequency sweep
5. **DGS equivalent circuit** — L, C values and frequency perturbation for rectangular slots

### Users
- `data-generator` module — calls the engine in a tight loop (5,000–10,000 times) to build the training dataset
- `api` module — calls the engine in real-time for single-point predictions (must be fast, <50ms per call)

---

## Tech Stack

- **Language:** Python 3.10+
- **Dependencies:** NumPy, SciPy (only for special functions if needed)
- **No external EM solvers.** Every computation is closed-form or semi-analytical.

---

## Commands

```bash
# Run all physics engine tests
pytest backend/physics_engine/tests/ -v

# Run a quick sanity check (prints sample outputs)
python -m backend.physics_engine.validate

# Benchmark: time 10,000 evaluations
python -m backend.physics_engine.benchmark
```

---

## Project Structure

```
backend/physics_engine/
├── __init__.py              # Public API: frequency(), gain(), pattern(), s_parameter(), dgs_circuit()
├── cavity_model.py          # Resonant frequency: ε_eff, ΔL, f_r
├── radiation.py             # Far-field pattern: E-plane, H-plane, full (θ, φ) grid
├── gain_model.py            # Directivity, radiation efficiency, gain
├── impedance.py             # Input impedance, S₁₁ return loss vs frequency
├── dgs_model.py             # DGS equivalent circuit: L, C, Δf perturbation
├── constants.py             # Physical constants: c, ε₀, μ₀, etc.
├── types.py                 # Dataclasses: AntennaConfig, DGSSlot, PatternResult, etc.
├── validate.py              # Sanity check script: known antenna → expected outputs
├── benchmark.py             # Performance benchmark
└── tests/
    ├── test_cavity_model.py
    ├── test_radiation.py
    ├── test_gain_model.py
    ├── test_impedance.py
    ├── test_dgs_model.py
    └── test_integration.py  # End-to-end: config → all outputs
```

---

## Physics Equations (Canonical Reference)

### Module 1: `cavity_model.py` — Resonant Frequency

**Effective dielectric constant** (Hammerstad):
```
ε_eff = (ε_r + 1) / 2 + (ε_r - 1) / 2 × [1 + 12h/W]^(-0.5)
```
- `ε_r`: substrate relative permittivity (e.g., 4.4 for FR4, 2.2 for Rogers RT/duroid 5880)
- `h`: substrate height (meters)
- `W`: patch width (meters)

**Fringing extension** (Hammerstad):
```
ΔL = 0.412 × h × [(ε_eff + 0.3)(W/h + 0.264)] / [(ε_eff - 0.258)(W/h + 0.8)]
```

**Effective patch length:**
```
L_eff = L + 2ΔL
```

**Resonant frequency** (TM₀₁₀ dominant mode):
```
f_r = c / (2 × L_eff × √ε_eff)
```
Where `c = 2.998 × 10⁸ m/s`.

**Validation targets:**
- FR4 (ε_r=4.4), h=1.6mm, W=38mm, L=29mm → f_r ≈ 2.4 GHz (WiFi band)
- Rogers 5880 (ε_r=2.2), h=0.787mm, W=15mm, L=12mm → f_r ≈ 8.5 GHz

---

### Module 2: `radiation.py` — Far-Field Radiation Pattern

The rectangular patch is modeled as **two radiating slots** (width W, height h) separated by distance L_eff.

**Normalized E-plane pattern (φ = 0°):**
```
F_E(θ) = cos(k₀ × L_eff × sinθ / 2) × sinc(k₀ × h × sinθ / 2)
```

**Normalized H-plane pattern (φ = 90°):**
```
F_H(θ) = sinc(k₀ × W × sinθ / 2) × cos(k₀ × L_eff × sinθ / 2)
```

**Full 3D pattern** (for arbitrary θ, φ):
```
F(θ, φ) = cos(k₀ × L_eff × sinθ × cosφ / 2)
         × sinc(k₀ × W × sinθ × sinφ / 2)
         × sinc(k₀ × h × sinθ / 2)
```

Where:
- `k₀ = 2π / λ₀ = 2πf/c` (free-space wavenumber)
- `sinc(x) = sin(x)/x` for x ≠ 0, 1 for x = 0

**Output format:**
```python
{
    "theta_deg": np.ndarray,       # 0 to 180, shape (N,)
    "phi_deg": np.ndarray,         # 0 to 360, shape (M,)
    "gain_pattern_db": np.ndarray, # shape (N, M), normalized to peak
    "e_plane_db": np.ndarray,      # shape (N,), φ=0° cut
    "h_plane_db": np.ndarray,      # shape (N,), φ=90° cut
}
```

**Angular resolution:** 1° default (181 × 361 grid), configurable.

---

### Module 3: `gain_model.py` — Directivity & Gain

**Radiation conductance** of each slot (Balanis approximation):
```
G₁ = (W / (120 × λ₀)) × [1 - (k₀h)²/24]     for k₀h << 1
```

**Directivity** (two-slot array):
```
D₀ = (2 × π × W²) / (λ₀² × G_total)
```
Where `G_total = 2 × (G₁ + G₁₂)` and `G₁₂` is the mutual conductance between the two slots (computed via numerical integration or Balanis's tabulated approximation).

**Simplified directivity** (valid for W/λ₀ < 1):
```
D₀ ≈ (6.6 × W²) / λ₀²     (Balanis eq. 14-17 approximation)
```

**Radiation efficiency:**
```
η_rad = G_rad / (G_rad + G_dielectric + G_conductor + G_surface_wave)
```

Where:
- `G_dielectric = (ε_r × tanδ × f) / (4 × h)` — dielectric loss (tanδ ≈ 0.02 for FR4, 0.0009 for Rogers)
- `G_conductor = Rs / (π × h)` — conductor loss (Rs = surface resistance of copper)
- `G_surface_wave` — negligible for thin substrates (h/λ₀ < 0.05), set to 0

**Gain:**
```
G = η_rad × D₀     (linear)
G_dBi = 10 × log₁₀(G)
```

**Expected ranges:** 2–8 dBi for typical rectangular patches.

---

### Module 4: `impedance.py` — Input Impedance & S₁₁

**Edge input resistance** (simplified Balanis):
```
R_edge = 1 / (2 × G₁)
```
Typically 150–300 Ω for a rectangular patch.

**Inset-fed input resistance:**
```
R_in(y₀) = R_edge × cos²(π × y₀ / L)
```
Where `y₀` is the inset depth. Feed position is configurable; default `y₀` computed to match 50 Ω.

**Input impedance vs frequency** (transmission line model):
```
Z_in(f) = R_in × [1 + j × Q_total × (f/f_r - f_r/f)]⁻¹
```
Where `Q_total` is the total quality factor:
```
1/Q_total = 1/Q_rad + 1/Q_dielectric + 1/Q_conductor
Q_rad = c × √ε_eff / (4 × f_r × h)
Q_dielectric = 1 / tanδ
Q_conductor = h × √(π × f_r × μ₀ × σ_copper)
```

**S₁₁ return loss:**
```
Γ(f) = (Z_in(f) - Z₀) / (Z_in(f) + Z₀)     where Z₀ = 50 Ω
S₁₁(f) = 20 × log₁₀(|Γ(f)|)                  in dB
```

**Output format:**
```python
{
    "freq_ghz": np.ndarray,   # sweep range, shape (K,)
    "s11_db": np.ndarray,     # S₁₁ in dB, shape (K,)
    "z_in_real": np.ndarray,  # Re(Z_in), shape (K,)
    "z_in_imag": np.ndarray,  # Im(Z_in), shape (K,)
    "bandwidth_ghz": float,   # -10 dB bandwidth
    "q_total": float,
}
```

**Frequency sweep:** default `f_r ± 50%`, 500 points. Configurable.

---

### Module 5: `dgs_model.py` — Rectangular Slot DGS

A rectangular slot etched in the ground plane acts as a **parallel LC resonator** in the transmission line model.

**Slot equivalent capacitance:**
```
C_dgs = (ε₀ × ε_r × slot_W × slot_L) / h
```

**Slot resonant frequency:**
```
f_dgs = c / (2 × slot_L × √ε_eff_slot)
```
Where `ε_eff_slot` uses the slot dimensions in the same Hammerstad formula.

**Slot equivalent inductance** (derived from resonance):
```
L_dgs = 1 / (4π² × f_dgs² × C_dgs)
```

**Frequency perturbation** on the patch:
```
Δf/f_r = -α × (slot_area / patch_area) × (ε_eff / ε_eff_slot)
```
Where `α` is a coupling coefficient (empirically 0.1–0.3 depending on slot position relative to the patch center). Slots near the center of the patch cause larger perturbation than slots near the edge.

**Position-dependent coupling:**
```
α(x, y) = α_max × cos²(π × x / L_ground) × cos²(π × y / W_ground)
```
Where `(x, y)` is the slot center position on the ground plane, and `α_max ≈ 0.2`.

**Perturbed frequency:**
```
f_perturbed = f_r × (1 + Δf/f_r)
```
Note: Δf/f_r is typically negative (slots lower the frequency).

**Gain perturbation:**
DGS slots modify the ground plane current distribution. The gain change is modeled as:
```
ΔG_dBi = -β × (slot_area / ground_area) × 10
```
Where `β ≈ 0.5–1.0` (slots generally reduce gain slightly by disrupting the ground plane, but can improve bandwidth).

**For multiple slots:** perturbations are additive (valid for non-overlapping, well-separated slots).

**Output format:**
```python
{
    "L_nH": float,              # equivalent inductance in nH
    "C_pF": float,              # equivalent capacitance in pF
    "f_dgs_ghz": float,         # slot resonant frequency
    "delta_f_ratio": float,     # Δf/f_r (negative = lower freq)
    "f_perturbed_ghz": float,   # final perturbed antenna frequency
    "delta_gain_dbi": float,    # gain change in dBi
}
```

---

## Data Types (`types.py`)

```python
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class SubstrateConfig:
    width_mm: float        # Ground plane / substrate width
    length_mm: float       # Ground plane / substrate length
    height_mm: float       # Substrate thickness
    epsilon_r: float       # Relative permittivity (4.4 for FR4)
    tan_delta: float       # Loss tangent (0.02 for FR4)

@dataclass
class PatchConfig:
    width_mm: float        # Patch width
    length_mm: float       # Patch length

@dataclass
class FeedConfig:
    width_mm: float        # Feed line width
    inset_mm: float = 0.0  # Inset depth for impedance matching

@dataclass
class DGSSlot:
    width_mm: float        # Slot width
    length_mm: float       # Slot length
    x_mm: float            # Slot center X position on ground plane
    y_mm: float            # Slot center Y position on ground plane

@dataclass
class AntennaConfig:
    substrate: SubstrateConfig
    patch: PatchConfig
    feed: FeedConfig
    slots: list[DGSSlot] = field(default_factory=list)

# Preset substrate materials
SUBSTRATES = {
    "FR4": {"epsilon_r": 4.4, "tan_delta": 0.02},
    "Rogers RT5880": {"epsilon_r": 2.2, "tan_delta": 0.0009},
    "Rogers RO4003C": {"epsilon_r": 3.55, "tan_delta": 0.0027},
    "Rogers RO3010": {"epsilon_r": 10.2, "tan_delta": 0.0022},
}
```

---

## Public API (`__init__.py`)

```python
def resonant_frequency(config: AntennaConfig) -> float:
    """Returns resonant frequency in GHz, including DGS perturbation."""

def gain(config: AntennaConfig) -> float:
    """Returns gain in dBi, including DGS perturbation."""

def radiation_pattern(
    config: AntennaConfig,
    theta_resolution: int = 181,
    phi_resolution: int = 361,
) -> dict:
    """Returns full radiation pattern as dict with theta, phi, gain arrays."""

def s_parameter(
    config: AntennaConfig,
    freq_start_ghz: float | None = None,
    freq_stop_ghz: float | None = None,
    num_points: int = 500,
) -> dict:
    """Returns S₁₁ sweep as dict with freq, s11_db, z_in arrays."""

def dgs_equivalent_circuit(slot: DGSSlot, config: AntennaConfig) -> dict:
    """Returns L, C, resonant frequency, and perturbation for a single slot."""

def full_analysis(config: AntennaConfig) -> dict:
    """Convenience: returns all outputs in one call."""
```

---

## Code Style

```python
import numpy as np
from backend.physics_engine.types import AntennaConfig, DGSSlot

def effective_permittivity(epsilon_r: float, h: float, w: float) -> float:
    """
    Compute effective dielectric constant using Hammerstad's formula.

    Args:
        epsilon_r: Substrate relative permittivity.
        h: Substrate height in meters.
        w: Patch width in meters.

    Returns:
        Effective dielectric constant (dimensionless).

    Reference:
        Hammerstad, E.O. (1975). "Equations for Microstrip Circuit Design."
    """
    ratio = w / h
    eps_eff = (epsilon_r + 1) / 2 + (epsilon_r - 1) / 2 * (1 + 12 / ratio) ** (-0.5)
    return eps_eff
```

**Conventions:**
- All internal computations in **SI units** (meters, Hz, F, H). Conversion to mm/GHz/pF/nH only at API boundaries.
- Every function has a **docstring with physics reference** (author, equation number where applicable).
- **No magic numbers** — all constants in `constants.py` with names and units.
- Type hints on all functions.
- `logging` module for diagnostic output, never `print()`.

---

## Testing Strategy

**Framework:** pytest  
**Location:** `backend/physics_engine/tests/`  
**Coverage target:** ≥90% line coverage

### Test Categories

| Category | What it tests | Example |
|----------|--------------|---------|
| **Known-answer** | Compare against published textbook results | FR4 patch at 2.4 GHz: ±5% tolerance on frequency |
| **Physical bounds** | Outputs within physically realistic ranges | Gain ∈ [0, 12] dBi; Freq ∈ [0.5, 20] GHz |
| **Monotonicity** | Increasing patch length → decreasing frequency | Sweep L, assert f_r monotonically decreasing |
| **DGS perturbation** | Slots lower frequency, magnitude depends on area | Larger slot → larger |Δf|; no slot → Δf = 0 |
| **Symmetry** | Pattern symmetric about broadside | E_plane(θ) = E_plane(-θ) |
| **S₁₁ resonance** | Minimum S₁₁ occurs at computed f_r | argmin(S₁₁) within ±2% of f_r |
| **Edge cases** | Zero-area slot, maximum slot, very thin substrate | No NaN, no division by zero |
| **Performance** | 10,000 evaluations < 30 seconds | Benchmark test |

---

## Boundaries

### Always Do
- Validate all inputs: patch must fit inside substrate, slot must fit inside ground plane, dimensions > 0
- Use SI units internally, convert at boundaries only
- Include physics reference in every function docstring
- Run `pytest` before committing any change to this module

### Ask First
- Adding new physics models beyond what's specified (e.g., higher-order modes)
- Changing the public API function signatures
- Adding dependencies beyond NumPy/SciPy

### Never Do
- Use arbitrary scaling factors without physics justification
- Hardcode specific antenna dimensions (parameterize everything)
- Return results without physical units documented
- Approximate π, c, or other constants manually (use `numpy` or `scipy.constants`)

---

## Success Criteria

1. **Resonant frequency** within ±5% of textbook values for 3+ known antenna configurations (FR4 @2.4GHz, Rogers @5.8GHz, Rogers @8.5GHz)
2. **Gain** within ±1 dBi of expected range for standard rectangular patches (2–8 dBi)
3. **Radiation pattern** produces recognizable broadside pattern: main lobe at θ=0°, 3dB beamwidth in expected range (60°–120° for typical patches), back lobe suppression ≥10 dB
4. **S₁₁** shows clear resonance dip (< -10 dB) at the computed resonant frequency
5. **DGS perturbation** shifts frequency downward, magnitude proportional to slot area, zero perturbation when no slots present
6. **Performance**: `full_analysis()` completes in <50ms for a single configuration; 10,000 evaluations in <30s
7. **All tests pass** with ≥90% coverage

---

## Open Questions

1. **Mutual conductance G₁₂**: Use Balanis's tabulated values or the numerical integration formula? Tabulated is faster but less accurate for unusual W/L ratios.
2. **DGS coupling coefficient α_max**: The 0.2 value is a starting point from literature. Should we calibrate this against any specific published DGS study?
3. **Higher-order modes**: Should we warn the user when patch dimensions could excite TM₀₂ or TM₂₀ modes, even if we don't compute them?
