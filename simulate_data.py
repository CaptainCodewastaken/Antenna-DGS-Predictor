import pandas as pd
import numpy as np

# Set random seed for reproducibility
np.random.seed(42)

# Define dataset size
num_samples = 5000

# 1. Generate realistic random physical dimensions
# Substrate parameters (FR4 is typically ~4.4 dielectric constant, but we'll focus on physical dims)
sub_w = np.random.uniform(20.0, 50.0, num_samples) # mm
sub_l = np.random.uniform(20.0, 50.0, num_samples)
sub_h = np.random.uniform(0.5, 2.0, num_samples)

# Patch dimensions (must be smaller than substrate)
patch_w = np.random.uniform(10.0, sub_w - 5.0, num_samples)
patch_l = np.random.uniform(10.0, sub_l - 5.0, num_samples)

# Feed width
feed_w = np.random.uniform(1.0, 4.0, num_samples)

# Slot dimensions
slot1_w = np.random.uniform(0.5, 3.0, num_samples)
slot1_l = np.random.uniform(1.0, 8.0, num_samples)
slot2_w = np.random.uniform(0.5, 3.0, num_samples)
slot2_l = np.random.uniform(1.0, 8.0, num_samples)

# 2. Simulate targets using fundamental physics approximations

# Frequency is primarily inversely proportional to Patch Length (f ~ c / 2L * sqrt(er))
# Adding perturbations based on slots (slots usually lower resonant freq by extending current path)
c = 300 # speed of light in mm/ns to get GHz directly
er = 4.4 # FR4 relative permittivity
freq_base = c / (2 * patch_l * np.sqrt(er))
freq_perturbation = - (slot1_l * 0.05) - (slot2_l * 0.05) + (sub_h * 0.1)
freq_noise = np.random.normal(0, 0.05, num_samples) # Add 50 MHz Gaussian noise
freq_ghz = freq_base + freq_perturbation + freq_noise

# Gain is primarily proportional to antenna physical aperture size (Patch_W * Patch_L)
gain_base = (patch_w * patch_l) / 100.0 # Arbitrary scaling to get realistic dBi values (2-8 dBi)
gain_perturbation = (sub_h * 1.5) - (slot1_w * 0.1) - (slot2_w * 0.1)
gain_noise = np.random.normal(0, 0.2, num_samples)
gain_dbi = gain_base + gain_perturbation + gain_noise

# 3. Create DataFrame
df = pd.DataFrame({
    'Sub_W': np.round(sub_w, 2),
    'Sub_L': np.round(sub_l, 2),
    'Sub_H': np.round(sub_h, 2),
    'Patch_W': np.round(patch_w, 2),
    'Patch_L': np.round(patch_l, 2),
    'Feed_W': np.round(feed_w, 2),
    'Slot1_W': np.round(slot1_w, 2),
    'Slot1_L': np.round(slot1_l, 2),
    'Slot2_W': np.round(slot2_w, 2),
    'Slot2_L': np.round(slot2_l, 2),
    'Freq_GHz': np.round(freq_ghz, 4),
    'Gain': np.round(gain_dbi, 4)
})

# Save to CSV
df.to_csv('antenna_data.csv', index=False)
print("Successfully generated 5,000 mathematically sound synthetic samples!")
