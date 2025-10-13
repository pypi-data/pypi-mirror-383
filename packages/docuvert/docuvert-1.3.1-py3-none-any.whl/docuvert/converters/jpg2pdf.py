"""
JPEG to PDF converter with quality preservation.
"""

import sys
import os

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
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.utils import ImageReader
except ImportError as e:
    raise DependencyError(
        "ReportLab is required for PDF generation",
        missing_dependency="reportlab"
    ) from e


class Jpg2PdfConverter:
    """Convert JPEG to PDF format."""

    def parse_jpg2ast(self, input_path: str):
        """Parse JPEG to AST representation (placeholder)."""
        return None

    def ast2pdf(self, ast_root, output_path: str):
        """Convert AST to PDF (placeholder)."""
        pass

    def convert(self, input_path: str, output_path: str) -> None:
        """Convert JPEG to PDF.

        Args:
            input_path: Path to input JPEG file
            output_path: Path to output PDF file
        """

        if not os.path.exists(input_path):
            raise ConversionError(f"Input file not found: {input_path}")

        if not output_path.lower().endswith(".pdf"):
            output_path += ".pdf"

        try:
            # Open and analyze the image
            with Image.open(input_path) as img:
                # Get image dimensions
                img_width, img_height = img.size

                # Calculate appropriate page size
                # Standard DPI for print is 300, but we'll use a reasonable scale
                scale_factor = 72 / 300  # Convert 300 DPI to 72 DPI (PDF standard)
                page_width = img_width * scale_factor
                page_height = img_height * scale_factor

                # Ensure minimum readable size
                min_width, min_height = 200, 200
                if page_width < min_width or page_height < min_height:
                    scale = max(min_width / page_width, min_height / page_height)
                    page_width *= scale
                    page_height *= scale

                # Create PDF with custom page size
                c = canvas.Canvas(output_path, pagesize=(page_width, page_height))

                # Draw the image to fill the entire page
                c.drawImage(input_path, 0, 0, width=page_width, height=page_height)

                # Save the PDF
                c.save()

            print(f"Successfully converted '{input_path}' to '{output_path}'")

        except Exception as e:
            raise ConversionError(
                f"JPEG to PDF conversion failed: {e}",
                source_format="jpeg",
                target_format="pdf",
                suggestions=[
                    "Ensure JPEG file is not corrupted",
                    "Check if JPEG file is readable by PIL/Pillow"
                ]
            )