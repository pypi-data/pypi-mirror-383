"""
PDF to HEIC converter with high-quality rendering.
"""

import sys
import os
from io import BytesIO

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from core.exceptions import ConversionError, DependencyError

try:
    import fitz  # PyMuPDF
except ImportError as e:
    raise DependencyError(
        "PyMuPDF is required for PDF to image conversion",
        missing_dependency="pymupdf"
    ) from e

try:
    from PIL import Image
except ImportError as e:
    raise DependencyError(
        "Pillow is required for image processing",
        missing_dependency="pillow"
    ) from e


class Pdf2HeicConverter:
    """Convert PDF to HEIC format (first page by default)."""

    def parse_pdf2ast(self, input_path: str):
        """Parse PDF to AST representation (placeholder)."""
        return None

    def ast2heic(self, ast_root, output_path: str):
        """Convert AST to HEIC (placeholder)."""
        pass

    def convert(self, input_path: str, output_path: str, page_number: int = 0) -> None:
        """Convert PDF to HEIC image.

        Args:
            input_path: Path to input PDF file
            output_path: Path to output HEIC file
            page_number: Page number to convert (0-indexed, default is first page)
        """

        if not os.path.exists(input_path):
            raise ConversionError(f"Input file not found: {input_path}")

        if not output_path.lower().endswith((".heic", ".heif")):
            output_path += ".heic"

        errors = []

        try:
            # Open PDF document
            pdf_document = fitz.open(input_path)

            # Check if page number is valid
            if page_number >= len(pdf_document):
                raise ConversionError(
                    f"Page {page_number} does not exist in PDF (total pages: {len(pdf_document)})",
                    source_format="pdf",
                    target_format="heic"
                )

            # Get the page
            page = pdf_document[page_number]

            # Render page to image with high DPI for quality
            mat = fitz.Matrix(3.0, 3.0)  # 3x zoom for 216 DPI (72 * 3)
            pix = page.get_pixmap(matrix=mat)

            # Convert to PIL Image for better processing
            img_data = pix.tobytes("png")
            img = Image.open(BytesIO(img_data))

            # Convert to RGB if needed (HEIC doesn't support transparency well)
            if img.mode in ('RGBA', 'LA'):
                # Create white background for transparency
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'RGBA':
                    background.paste(img, mask=img.split()[-1])
                else:  # LA mode
                    background.paste(img.convert('RGB'))
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')

            # Clean up PDF document first
            pdf_document.close()

            # Try to save as HEIC using pillow-heif
            try:
                import pillow_heif
                pillow_heif.register_heif_opener()
                img.save(output_path, format='HEIF', quality=95, optimize=True)
                print(f"Successfully converted PDF page {page_number} to '{output_path}' via pillow-heif")
                return

            except ImportError as e:
                errors.append(f"pillow-heif not available: {e}")
            except Exception as e:
                errors.append(f"pillow-heif conversion failed: {e}")

            # Fallback: save as temporary PNG and convert via system tools
            import tempfile
            import subprocess
            import shutil

            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_png:
                img.save(tmp_png.name, "PNG", optimize=True)
                tmp_png_path = tmp_png.name

            try:
                # Try ImageMagick
                if shutil.which("magick"):
                    result = subprocess.run([
                        "magick", tmp_png_path, "-quality", "95", output_path
                    ], capture_output=True, text=True)

                    if result.returncode == 0 and os.path.exists(output_path):
                        os.unlink(tmp_png_path)
                        print(f"Successfully converted PDF page {page_number} to '{output_path}' via ImageMagick")
                        return

                    errors.append(f"ImageMagick failed: {result.stderr.strip()}")
                else:
                    errors.append("ImageMagick 'magick' not found")

                # Try macOS sips
                if sys.platform == "darwin" and shutil.which("sips"):
                    result = subprocess.run([
                        "sips", "-s", "format", "heif", tmp_png_path, "--out", output_path
                    ], capture_output=True, text=True)

                    if result.returncode == 0 and os.path.exists(output_path):
                        os.unlink(tmp_png_path)
                        print(f"Successfully converted PDF page {page_number} to '{output_path}' via sips")
                        return

                    errors.append(f"sips failed: {result.stderr.strip()}")
                else:
                    errors.append("sips not available (not macOS or not found)")

            finally:
                # Clean up temporary file
                if os.path.exists(tmp_png_path):
                    os.unlink(tmp_png_path)

        except Exception as e:
            if isinstance(e, ConversionError):
                raise
            errors.append(f"PDF processing failed: {e}")

        # If we reach here, all conversion methods failed
        raise ConversionError(
            "PDF to HEIC conversion failed with all methods.\n" +
            "Errors: " + " | ".join(errors),
            source_format="pdf",
            target_format="heic",
            suggestions=[
                "Install pillow-heif (recommended): pip install pillow-heif",
                "Install ImageMagick with HEIF support",
                "On macOS, use built-in sips command",
                "Ensure PDF is not corrupted or password-protected"
            ]
        )