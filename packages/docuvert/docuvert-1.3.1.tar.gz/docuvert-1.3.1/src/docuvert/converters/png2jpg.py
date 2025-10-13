"""
PNG to JPEG converter with alpha channel handling.
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


class Png2JpgConverter:
    """Convert PNG to JPEG format."""

    def parse_png2ast(self, input_path: str):
        """Parse PNG to AST representation (placeholder)."""
        return None

    def ast2jpg(self, ast_root, output_path: str):
        """Convert AST to JPEG (placeholder)."""
        pass

    def convert(self, input_path: str, output_path: str) -> None:
        """Convert PNG to JPEG."""

        if not os.path.exists(input_path):
            raise ConversionError(f"Input file not found: {input_path}")

        if not output_path.lower().endswith((".jpg", ".jpeg")):
            output_path += ".jpg"

        try:
            with Image.open(input_path) as img:
                # Handle alpha channel - JPEG doesn't support transparency
                if img.mode in ('RGBA', 'LA'):
                    # Create white background
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'RGBA':
                        background.paste(img, mask=img.split()[-1])  # Use alpha as mask
                    else:  # LA mode
                        background.paste(img.convert('RGB'))
                    img = background
                elif img.mode != 'RGB':
                    img = img.convert('RGB')

                img.save(output_path, "JPEG", quality=95, optimize=True)

            print(f"Successfully converted '{input_path}' to '{output_path}'")

        except Exception as e:
            raise ConversionError(
                f"PNG to JPEG conversion failed: {e}",
                source_format="png",
                target_format="jpeg",
                suggestions=["Note: PNG transparency will be flattened to white background"]
            )