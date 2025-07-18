"""Extremely naive, *colour-based* plant/weed classifier.

It looks at the proportion of green vs non-green pixels:

* green_ratio >= 0.55  →  (label=plant,  confidence=green_ratio)
* green_ratio <= 0.35  →  (label=weed,   confidence=1-green_ratio)
* otherwise           →  (label=unsure, confidence=0.0)

Real life: replace by a CNN or transformer.  We keep the function signature so
the rest of the pipeline could stay unchanged.
"""

from __future__ import annotations

from typing import Literal

import cv2
import numpy as np

Label = Literal["plant", "weed", "unsure"]


def _green_ratio(bgr: np.ndarray) -> float:
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    lower = np.array([25, 40, 40])
    upper = np.array([95, 255, 255])
    mask = cv2.inRange(hsv, lower, upper)
    green_pixels = int(mask.sum() / 255)
    total = bgr.shape[0] * bgr.shape[1]
    return green_pixels / total if total else 0.0


def classify(bgr: np.ndarray) -> tuple[Label, float]:
    """Return (label, confidence) for *bgr* image crop."""
    g = _green_ratio(bgr)
    if g >= 0.55:
        return "plant", g  # confident if mostly green
    if g <= 0.35:
        return "weed", 1 - g  # confident if very little green
    return "unsure", 0.0

