"""
HEIC to PDF converter with fallback methods.
"""

import sys
import os
import tempfile
import subprocess
import shutil

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


class Heic2PdfConverter:
    """Convert HEIC to PDF format using layered fallbacks."""

    def parse_heic2ast(self, input_path: str):
        """Parse HEIC to AST representation (placeholder)."""
        return None

    def ast2pdf(self, ast_root, output_path: str):
        """Convert AST to PDF (placeholder)."""
        pass

    def convert(self, input_path: str, output_path: str) -> None:
        """Convert HEIC to PDF.

        Args:
            input_path: Path to input HEIC file
            output_path: Path to output PDF file
        """

        if not os.path.exists(input_path):
            raise ConversionError(f"Input file not found: {input_path}")

        if not output_path.lower().endswith(".pdf"):
            output_path += ".pdf"

        errors = []

        # Method 1: Direct HEIC to PDF via pillow-heif
        try:
            import pillow_heif
            pillow_heif.register_heif_opener()

            with Image.open(input_path) as img:
                # Convert to RGB if needed
                if img.mode != 'RGB':
                    img = img.convert('RGB')

                # Get image dimensions and calculate page size
                img_width, img_height = img.size
                scale_factor = 72 / 300  # Convert 300 DPI to 72 DPI (PDF standard)
                page_width = img_width * scale_factor
                page_height = img_height * scale_factor

                # Ensure minimum readable size
                min_width, min_height = 200, 200
                if page_width < min_width or page_height < min_height:
                    scale = max(min_width / page_width, min_height / page_height)
                    page_width *= scale
                    page_height *= scale

                # Create temporary PNG for ReportLab
                with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_png:
                    img.save(tmp_png.name, "PNG")
                    tmp_png_path = tmp_png.name

                try:
                    # Create PDF with custom page size
                    c = canvas.Canvas(output_path, pagesize=(page_width, page_height))
                    c.drawImage(tmp_png_path, 0, 0, width=page_width, height=page_height)
                    c.save()

                    print(f"Successfully converted '{input_path}' to '{output_path}' via pillow-heif")
                    return

                finally:
                    # Clean up temporary file
                    if os.path.exists(tmp_png_path):
                        os.unlink(tmp_png_path)

        except ImportError as e:
            errors.append(f"pillow-heif not available: {e}")
        except Exception as e:
            errors.append(f"pillow-heif conversion failed: {e}")

        # Method 2: pyheif fallback
        try:
            import pyheif

            heif_file = pyheif.read(input_path)
            img = Image.frombytes(
                heif_file.mode,
                heif_file.size,
                heif_file.data,
                "raw",
                heif_file.mode,
                heif_file.stride,
            )

            # Convert to RGB if needed
            if img.mode != 'RGB':
                img = img.convert('RGB')

            # Get image dimensions and calculate page size
            img_width, img_height = img.size
            scale_factor = 72 / 300  # Convert 300 DPI to 72 DPI (PDF standard)
            page_width = img_width * scale_factor
            page_height = img_height * scale_factor

            # Ensure minimum readable size
            min_width, min_height = 200, 200
            if page_width < min_width or page_height < min_height:
                scale = max(min_width / page_width, min_height / page_height)
                page_width *= scale
                page_height *= scale

            # Create temporary PNG for ReportLab
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_png:
                img.save(tmp_png.name, "PNG")
                tmp_png_path = tmp_png.name

            try:
                # Create PDF with custom page size
                c = canvas.Canvas(output_path, pagesize=(page_width, page_height))
                c.drawImage(tmp_png_path, 0, 0, width=page_width, height=page_height)
                c.save()

                print(f"Successfully converted '{input_path}' to '{output_path}' via pyheif")
                return

            finally:
                # Clean up temporary file
                if os.path.exists(tmp_png_path):
                    os.unlink(tmp_png_path)

        except ImportError as e:
            errors.append(f"pyheif not available: {e}")
        except Exception as e:
            errors.append(f"pyheif conversion failed: {e}")

        # Method 3: System tools (sips on macOS, ImageMagick)
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_png:
            tmp_png_path = tmp_png.name

        try:
            # Try macOS sips first
            if sys.platform == "darwin" and shutil.which("sips"):
                result = subprocess.run([
                    "sips", "-s", "format", "png", input_path, "--out", tmp_png_path
                ], capture_output=True, text=True)

                if result.returncode == 0 and os.path.exists(tmp_png_path):
                    # Convert PNG to PDF
                    with Image.open(tmp_png_path) as img:
                        img_width, img_height = img.size
                        scale_factor = 72 / 300
                        page_width = img_width * scale_factor
                        page_height = img_height * scale_factor

                        min_width, min_height = 200, 200
                        if page_width < min_width or page_height < min_height:
                            scale = max(min_width / page_width, min_height / page_height)
                            page_width *= scale
                            page_height *= scale

                        c = canvas.Canvas(output_path, pagesize=(page_width, page_height))
                        c.drawImage(tmp_png_path, 0, 0, width=page_width, height=page_height)
                        c.save()

                    print(f"Successfully converted '{input_path}' to '{output_path}' via sips")
                    return

                errors.append(f"sips failed: {result.stderr.strip()}")

            # Try ImageMagick
            if shutil.which("magick"):
                result = subprocess.run([
                    "magick", input_path, tmp_png_path
                ], capture_output=True, text=True)

                if result.returncode == 0 and os.path.exists(tmp_png_path):
                    # Convert PNG to PDF
                    with Image.open(tmp_png_path) as img:
                        img_width, img_height = img.size
                        scale_factor = 72 / 300
                        page_width = img_width * scale_factor
                        page_height = img_height * scale_factor

                        min_width, min_height = 200, 200
                        if page_width < min_width or page_height < min_height:
                            scale = max(min_width / page_width, min_height / page_height)
                            page_width *= scale
                            page_height *= scale

                        c = canvas.Canvas(output_path, pagesize=(page_width, page_height))
                        c.drawImage(tmp_png_path, 0, 0, width=page_width, height=page_height)
                        c.save()

                    print(f"Successfully converted '{input_path}' to '{output_path}' via ImageMagick")
                    return

                errors.append(f"ImageMagick failed: {result.stderr.strip()}")

        finally:
            # Clean up temporary file
            if os.path.exists(tmp_png_path):
                os.unlink(tmp_png_path)

        # If we reach here, all conversion methods failed
        raise ConversionError(
            "HEIC to PDF conversion failed with all methods.\n" +
            "Errors: " + " | ".join(errors),
            source_format="heic",
            target_format="pdf",
            suggestions=[
                "Install pillow-heif (recommended): pip install pillow-heif",
                "Install pyheif: pip install pyheif",
                "Install ImageMagick with HEIF support",
                "On macOS, use built-in sips command",
                "Ensure HEIC file is not corrupted"
            ]
        )