"""CLI for simple *detection-only* stage.

Extracts every detected plant patch and writes it to ``cropped_out_images/``.
The detection algorithm is the same as in :pymod:`garden_weedbot.pipeline`
but skips the classification step entirely.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import cv2

from . import utils


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Crop out individual plants from photos.")
    p.add_argument("--input", type=Path, default=Path("images"), help="Input folder with raw photos")
    p.add_argument(
        "--output",
        type=Path,
        default=Path("cropped_out_images"),
        help="Destination folder for all crops (default: ./cropped_out_images)",
    )
    p.add_argument("--area-min", type=int, default=5000, help="Minimum contour area to keep")
    return p


def process(input_dir: Path, output_dir: Path, min_area: int = 5000) -> None:  # noqa: D401
    if not input_dir.exists():
        raise FileNotFoundError(input_dir)

    utils.ensure_dir(output_dir)

    imgs = sorted(p for p in input_dir.iterdir() if p.suffix.lower() in {".jpg", ".png", ".jpeg", ".bmp"})
    if not imgs:
        print("No images found – nothing to do.")
        return

    for path in imgs:
        print(f"Cropping {path.name} …", flush=True)
        img = utils.load_image(path)
        mask = utils.hsv_green_mask(img)
        contours = utils.find_contours(mask, min_area)
        for idx, c in enumerate(contours):
            crop = utils.crop_from_contour(img, c)
            out_name = f"{path.stem}_{idx:02d}{path.suffix}"
            out_path = output_dir / out_name
            cv2.imwrite(str(out_path), crop)

    print(f"Done. Crops in {output_dir}")


def main(argv: list[str] | None = None) -> None:  # pragma: no cover
    args = build_parser().parse_args(argv)
    process(args.input, args.output, args.area_min)


if __name__ == "__main__":  # pragma: no cover
    main()

