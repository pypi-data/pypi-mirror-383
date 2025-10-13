"""
JPEG to PNG converter.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from core.exceptions import ConversionError, DependencyError

try:
    from PIL import Image
except ImportError as e:
    raise DependencyError(
        "Pillow is required for image conversion",
        missing_dependency="pillow"
    ) from e


class Jpg2PngConverter:
    """Convert JPEG to PNG format."""

    def parse_jpg2ast(self, input_path: str):
        """Parse JPEG to AST representation (placeholder)."""
        return None

    def ast2png(self, ast_root, output_path: str):
        """Convert AST to PNG (placeholder)."""
        pass

    def convert(self, input_path: str, output_path: str) -> None:
        """Convert JPEG to PNG."""

        if not os.path.exists(input_path):
            raise ConversionError(f"Input file not found: {input_path}")

        if not output_path.lower().endswith(".png"):
            output_path += ".png"

        try:
            with Image.open(input_path) as img:
                # Convert to RGBA to preserve any transparency
                if img.mode not in ('RGBA', 'LA'):
                    img = img.convert('RGBA')

                img.save(output_path, "PNG", optimize=True)

            print(f"Successfully converted '{input_path}' to '{output_path}'")

        except Exception as e:
            raise ConversionError(
                f"JPEG to PNG conversion failed: {e}",
                source_format="jpeg",
                target_format="png"
            )