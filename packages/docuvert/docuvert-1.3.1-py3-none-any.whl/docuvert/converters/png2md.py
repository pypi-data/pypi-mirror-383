"""
PNG to Markdown converter using OCR for high-accuracy text extraction.
"""

import sys
import os
from io import BytesIO

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from core.exceptions import ConversionError, DependencyError

try:
    from PIL import Image
except ImportError as e:
    raise DependencyError(
        "Pillow is required for image processing",
        missing_dependency="pillow"
    ) from e

try:
    import pytesseract
except ImportError as e:
    raise DependencyError(
        "pytesseract is required for OCR text extraction",
        missing_dependency="pytesseract"
    ) from e


class Png2MdConverter:
    """Convert PNG to Markdown using OCR for maximum accuracy."""

    def parse_png2ast(self, input_path: str):
        """Parse PNG to AST representation (placeholder)."""
        return None

    def ast2md(self, ast_root, output_path: str):
        """Convert AST to Markdown (placeholder)."""
        pass

    def convert(self, input_path: str, output_path: str) -> None:
        """Convert PNG image to Markdown using OCR.

        Args:
            input_path: Path to input PNG file
            output_path: Path to output Markdown file
        """

        if not os.path.exists(input_path):
            raise ConversionError(f"Input file not found: {input_path}")

        if not output_path.lower().endswith(".md"):
            output_path += ".md"

        try:
            # Open and process image
            img = Image.open(input_path)

            # Pre-process image for better OCR accuracy
            # Convert to grayscale for better OCR
            if img.mode not in ('L', 'RGB'):
                img = img.convert('RGB')

            # Perform OCR with highest accuracy settings
            custom_config = r'--oem 3 --psm 6'  # OEM 3 = Default, PSM 6 = Uniform block of text

            # Extract text using OCR
            text = pytesseract.image_to_string(img, config=custom_config)

            # Clean up extracted text
            text = text.strip()

            if not text:
                print("Warning: No text detected in image. Creating markdown with image reference.")
                text = f"![Image]({os.path.basename(input_path)})\n\n*No text detected in this image*"

            # Create Markdown content with metadata
            markdown_content = f"""# Image to Markdown Conversion

**Source:** {os.path.basename(input_path)}
**Conversion Method:** OCR (Tesseract)

---

{text}

---

*Converted using Docuvert - Image to Markdown with OCR*
"""

            # Write to output file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)

            print(f"Successfully converted '{input_path}' to '{output_path}'")

        except pytesseract.TesseractNotFoundError:
            raise ConversionError(
                "Tesseract OCR is not installed or not in PATH",
                source_format="png",
                target_format="md",
                suggestions=[
                    "Install Tesseract OCR: brew install tesseract (macOS) or apt-get install tesseract-ocr (Linux)",
                    "Ensure Tesseract is in your system PATH"
                ]
            )
        except Exception as e:
            if isinstance(e, ConversionError):
                raise
            raise ConversionError(
                f"PNG to Markdown conversion failed: {e}",
                source_format="png",
                target_format="md",
                suggestions=[
                    "Ensure image is not corrupted",
                    "Check if Tesseract OCR is installed",
                    "Try converting the image to a different format first"
                ]
            )
