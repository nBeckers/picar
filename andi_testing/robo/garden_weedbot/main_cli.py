"""Simple command-line interface for the Garden WeedBot pipeline."""

import argparse
from pathlib import Path

from .pipeline import process_images


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Detect, crop and classify plants/weeds in garden pictures.",
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("images"),
        help="Folder containing raw images (default: ./images)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("output"),
        help="Destination folder for cropped, labelled images (default: ./output)",
    )
    parser.add_argument(
        "--conf",
        type=float,
        default=0.6,
        help=(
            "Confidence threshold in [0,1]. Predictions below the threshold "
            "go to the 'unsure' directory. (default: 0.6)"
        ),
    )
    parser.add_argument(
        "--area-min",
        type=int,
        default=5000,
        help="Minimum detected contour area in pixels to be considered a plant (default: 5000)",
    )
    return parser


def main(argv: list[str] | None = None) -> None:  # noqa: D401
    """Entry-point used by ``python -m garden_weedbot``."""
    parser = build_parser()
    args = parser.parse_args(argv)

    process_images(
        input_dir=args.input,
        output_dir=args.output,
        confidence_threshold=args.conf,
        min_area=args.area_min,
    )


if __name__ == "__main__":  # pragma: no cover
    main()

