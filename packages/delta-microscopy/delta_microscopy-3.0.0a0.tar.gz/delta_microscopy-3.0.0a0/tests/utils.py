"""Utilities for tests."""

import cv2
import numpy as np
import numpy.random as npr
from scipy.ndimage import binary_fill_holes

from delta.imgops import SegmentationMask


def rand_mask(
    image_size: tuple[int, int],
    max_dots: int = 100,
    max_radius: int = 30,
    seed: int | None = None,
) -> SegmentationMask:
    """Generate a random binary mask with random size dots."""
    rng = npr.default_rng(seed)
    mask = np.zeros(image_size, dtype=np.uint8)
    num_dots = rng.integers(max_dots, endpoint=True)

    for _ in range(num_dots):
        cv2.circle(
            mask,
            center=(rng.integers(image_size[0]), rng.integers(image_size[0])),
            radius=rng.integers(1, max_radius),
            color=1,
            thickness=-1,
        )

    # Holes cause issues here
    mask = binary_fill_holes(mask).astype(np.uint8)

    return mask
