"""High-level orchestration of the WeedBot image pipeline."""

from __future__ import annotations

import shutil
from pathlib import Path

import cv2

from . import utils
from .simple_classifier import classify


def _supported(path: Path) -> bool:
    return path.suffix.lower() in {".jpg", ".jpeg", ".png", ".bmp"}


def process_images(
    input_dir: Path,
    output_dir: Path,
    confidence_threshold: float = 0.6,
    min_area: int = 5_000,
) -> None:
    """Run detection + classification on *input_dir* and write results.

    Parameters
    ----------
    input_dir
        Folder with garden photos (RGB).  Each file must have an extension in
        {jpg, jpeg, png, bmp}.
    output_dir
        Destination folder.  Images will be written to

            output_dir/plant/<original>_<idx>.jpg
            output_dir/weed/<original>_<idx>.jpg
            output_dir/unsure/<original>_<idx>.jpg

    confidence_threshold
        Minimum confidence returned by the classifier for an image to be saved
        as *plant* or *weed*.  Below the threshold the crop is kept in
        *unsure*.
    min_area
        Minimum contour area in pixels to be considered.
    """

    if not input_dir.exists():
        raise FileNotFoundError(f"Input directory not found: {input_dir}")

    # Prepare destination folders.
    for sub in ("plant", "weed", "unsure"):
        utils.ensure_dir(output_dir / sub)

    image_paths = sorted(p for p in input_dir.iterdir() if _supported(p))
    if not image_paths:
        print("No images found – nothing to do.")
        return

    for path in image_paths:
        print(f"Processing {path.name} …", flush=True)
        img = utils.load_image(path)

        # Detection – segmentation by colour -> contours.
        mask = utils.hsv_green_mask(img)
        contours = utils.find_contours(mask, min_area=min_area)
        if not contours:
            # No vegetation detected → copy whole image to unsure.
            dst = output_dir / "unsure" / path.name
            shutil.copy(path, dst)
            continue

        for idx, c in enumerate(contours):
            crop = utils.crop_from_contour(img, c)
            label, conf = classify(crop)

            # Decide destination.
            if conf < confidence_threshold or label == "unsure":
                sub = "unsure"
            else:
                sub = label

            out_name = f"{path.stem}_{idx:02d}{path.suffix}"
            out_path = output_dir / sub / out_name
            cv2.imwrite(str(out_path), crop)

    print(f"Finished. Crops saved under: {output_dir}")

