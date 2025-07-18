"""Helper functions used across the pipeline."""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np


def load_image(path: Path) -> np.ndarray:
    """Load an image as BGR (OpenCV default)."""
    img = cv2.imread(str(path))
    if img is None:
        raise FileNotFoundError(f"Could not read image: {path}")
    return img


def ensure_dir(path: Path) -> None:
    """Create *path* if it doesn't exist."""
    path.mkdir(parents=True, exist_ok=True)


def hsv_green_mask(bgr: np.ndarray) -> np.ndarray:
    """Return a binary mask of *green-ish* pixels in *bgr* image.

    The thresholds were chosen empirically and will obviously need tuning in
    real applications.
    """
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    lower = np.array([25, 40, 40])  # hue 25/179 ≈ 50°, fairly green/yellow
    upper = np.array([95, 255, 255])
    mask = cv2.inRange(hsv, lower, upper)
    return mask


def find_contours(mask: np.ndarray, min_area: int = 5000) -> list[np.ndarray]:
    """Return contours in *mask* larger than *min_area* pixels."""
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    big = [c for c in contours if cv2.contourArea(c) >= min_area]
    return big


def crop_from_contour(img: np.ndarray, contour: np.ndarray) -> np.ndarray:
    x, y, w, h = cv2.boundingRect(contour)
    return img[y : y + h, x : x + w]

