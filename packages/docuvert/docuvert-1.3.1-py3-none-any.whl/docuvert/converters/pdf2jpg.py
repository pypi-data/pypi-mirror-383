"""
PDF to JPEG converter with high-quality rendering.
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


class Pdf2JpgConverter:
    """Convert PDF to JPEG format (first page by default)."""

    def parse_pdf2ast(self, input_path: str):
        """Parse PDF to AST representation (placeholder)."""
        return None

    def ast2jpg(self, ast_root, output_path: str):
        """Convert AST to JPEG (placeholder)."""
        pass

    def convert(self, input_path: str, output_path: str, page_number: int = None,
                pages: str = None, all_pages: bool = False) -> None:
        """Convert PDF to JPEG image(s).

        Args:
            input_path: Path to input PDF file
            output_path: Path to output JPEG file (or template for multi-page)
            page_number: Single page number to convert (0-indexed, default is first page if no other options)
            pages: Page range string (e.g., "1-3", "1,3,5", "1-3,5,7-9")
            all_pages: Convert all pages (creates numbered output files)
        """

        if not os.path.exists(input_path):
            raise ConversionError(f"Input file not found: {input_path}")

        if not output_path.lower().endswith((".jpg", ".jpeg")):
            output_path += ".jpg"

        try:
            # Open PDF document
            pdf_document = fitz.open(input_path)
            total_pages = len(pdf_document)

            # Determine which pages to convert
            if all_pages:
                pages_to_convert = list(range(total_pages))
            elif pages:
                pages_to_convert = self._parse_page_range(pages, total_pages)
            elif page_number is not None:
                pages_to_convert = [page_number]
            else:
                # Default: convert first page only
                pages_to_convert = [0]

            # Validate page numbers
            for page_num in pages_to_convert:
                if page_num >= total_pages or page_num < 0:
                    raise ConversionError(
                        f"Page {page_num} does not exist in PDF (total pages: {total_pages})",
                        source_format="pdf",
                        target_format="jpeg"
                    )

            # Convert pages
            if len(pages_to_convert) == 1:
                # Single page conversion
                self._convert_single_page(pdf_document, pages_to_convert[0], output_path)
            else:
                # Multi-page conversion with numbered files
                self._convert_multiple_pages(pdf_document, pages_to_convert, output_path)

            # Clean up
            pdf_document.close()

        except Exception as e:
            if isinstance(e, ConversionError):
                raise
            raise ConversionError(
                f"PDF to JPEG conversion failed: {e}",
                source_format="pdf",
                target_format="jpeg",
                suggestions=[
                    "Ensure PDF is not corrupted or password-protected",
                    "Check if page numbers exist in the PDF"
                ]
            )

    def _parse_page_range(self, page_range: str, total_pages: int) -> list:
        """Parse page range string into list of page numbers.

        Args:
            page_range: String like "1-3", "1,3,5", "1-3,5,7-9" (1-indexed)
            total_pages: Total number of pages in document

        Returns:
            List of 0-indexed page numbers
        """
        pages = []
        parts = page_range.split(',')

        for part in parts:
            part = part.strip()
            if '-' in part:
                # Range like "1-3"
                start, end = part.split('-')
                start = int(start.strip())
                end = int(end.strip())
                # Convert to 0-indexed
                pages.extend(range(start - 1, end))
            else:
                # Single page like "5"
                page = int(part.strip())
                # Convert to 0-indexed
                pages.append(page - 1)

        return sorted(set(pages))  # Remove duplicates and sort

    def _convert_single_page(self, pdf_document, page_number: int, output_path: str):
        """Convert a single PDF page to JPEG."""
        page = pdf_document[page_number]

        # Render page to image with high DPI for quality
        mat = fitz.Matrix(3.0, 3.0)  # 3x zoom for 216 DPI (72 * 3)
        pix = page.get_pixmap(matrix=mat)

        # Convert to PIL Image for better processing
        img_data = pix.tobytes("png")
        img = Image.open(BytesIO(img_data))

        # Convert to RGB if needed (JPEG doesn't support transparency)
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

        # Save as JPEG with high quality
        img.save(output_path, "JPEG", quality=95, optimize=True)

        print(f"Successfully converted PDF page {page_number + 1} to '{output_path}'")

    def _convert_multiple_pages(self, pdf_document, page_numbers: list, output_path: str):
        """Convert multiple PDF pages to numbered JPEG files."""
        base_name = output_path.rsplit('.', 1)[0]

        for page_num in page_numbers:
            # Create numbered output file
            numbered_output = f"{base_name}_page_{page_num + 1:04d}.jpg"
            self._convert_single_page(pdf_document, page_num, numbered_output)

        print(f"Successfully converted {len(page_numbers)} pages to JPEG images")