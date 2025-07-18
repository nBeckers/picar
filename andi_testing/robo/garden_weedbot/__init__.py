"""Garden WeedBot – simple image-processing pipeline.

Run as module:

    python -m garden_weedbot --input images --output output
"""

# Bump this manually when the public API changes.
__version__ = "0.1.0"

# Re-export CLI entry point so `python -m garden_weedbot` works.

from .main_cli import main as _main  # noqa: E402  pylint: disable=wrong-import-position

__all__ = ["_main"]
