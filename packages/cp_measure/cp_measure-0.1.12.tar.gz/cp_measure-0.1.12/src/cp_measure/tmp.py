import numpy as np

from cp_measure.core.measureobjectintensitydistribution import get_radial_distribution

size = 240
rng = np.random.default_rng(42)
# pixels = rng.integers(low=1, high=255, size=(size, size)) # Random
pixels = np.ones((size, size), dtype=np.integer)  # All ones
pixels[70:80, 70:80] = 10
# Create two similar-sized objects
masks = np.zeros_like(pixels)
masks[50:100, 50:100] = 1  # First square 50x50
# masks[80:120, 90:120] = 1  # Major asymmetries on bottom right edge
masks[150:200, 150:200] = 2  # Second square 50x50
# masks[175:180, 180:210] = 2  # Minor asymmetries on bottom right edge

# Get measurements
result = get_radial_distribution(masks, pixels)
