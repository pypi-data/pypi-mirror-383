"""
OCR utilities for text extraction from PDFs and images.
"""

import os
from io import BytesIO
from typing import Optional

try:
    import fitz  # PyMuPDF
except ImportError as e:
    raise ImportError("PyMuPDF is required for PDF processing") from e

try:
    from PIL import Image
except ImportError as e:
    raise ImportError("Pillow is required for image processing") from e

try:
    import pytesseract
except ImportError:
    pytesseract = None

import pdfplumber


class OCRExtractor:
    """Enhanced text extraction with OCR fallback for scanned documents."""

    @staticmethod
    def extract_text_from_pdf(input_path: str, use_ocr: bool = True) -> str:
        """
        Extract text from PDF using multiple methods.

        Args:
            input_path: Path to PDF file
            use_ocr: Whether to use OCR for scanned PDFs (default: True)

        Returns:
            Extracted text string
        """
        extracted_text = ""

        # Method 1: Try pdfplumber first (fast, good for text-based PDFs)
        try:
            with pdfplumber.open(input_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    page_text = page.extract_text()
                    if page_text and page_text.strip():
                        extracted_text += f"--- Page {page_num + 1} ---\n"
                        extracted_text += page_text + "\n\n"

            # If we got meaningful text, return it
            if extracted_text.strip() and len(extracted_text.strip()) > 50:
                print("✅ Successfully extracted text using pdfplumber (text-based PDF)")
                return extracted_text

        except Exception as e:
            print(f"⚠️ pdfplumber extraction failed: {e}")

        # Method 2: OCR using PyMuPDF + Tesseract (for scanned/image-based PDFs)
        if not use_ocr:
            return extracted_text if extracted_text else "No text could be extracted from this PDF."

        if pytesseract is None:
            print("⚠️ OCR not available - pytesseract not installed")
            print("📋 Install with: pip install pytesseract")
            print("🔧 Also install Tesseract: brew install tesseract (macOS) or apt-get install tesseract-ocr (Linux)")
            return extracted_text if extracted_text else "No text could be extracted from this PDF."

        try:
            print("🔍 Attempting OCR extraction (for scanned/image-based PDFs)...")
            return OCRExtractor._ocr_pdf_pages(input_path)

        except Exception as e:
            print(f"❌ OCR extraction failed: {e}")

        return extracted_text if extracted_text else "No text could be extracted from this PDF."

    @staticmethod
    def _ocr_pdf_pages(input_path: str) -> str:
        """Perform OCR on all pages of a PDF."""
        pdf_doc = fitz.open(input_path)
        ocr_text = ""

        for page_num in range(len(pdf_doc)):
            page = pdf_doc[page_num]

            # Render page to image at high resolution for better OCR
            mat = fitz.Matrix(2.0, 2.0)  # 2x zoom for better OCR accuracy
            pix = page.get_pixmap(matrix=mat)

            # Convert to PIL Image
            img_data = pix.tobytes("png")
            img = Image.open(BytesIO(img_data))

            # Perform OCR
            try:
                page_text = pytesseract.image_to_string(img, lang='eng')
                if page_text.strip():
                    ocr_text += f"--- Page {page_num + 1} ---\n"
                    ocr_text += page_text + "\n\n"
                    print(f"✅ OCR extracted text from page {page_num + 1}")
                else:
                    print(f"⚠️ No text found on page {page_num + 1}")

            except Exception as e:
                print(f"❌ OCR failed for page {page_num + 1}: {e}")

        pdf_doc.close()

        if ocr_text.strip():
            print("✅ Successfully extracted text using OCR")
            return ocr_text
        else:
            print("⚠️ No text could be extracted via OCR")
            return ""

    @staticmethod
    def extract_text_from_image(image_path: str) -> str:
        """
        Extract text from image using OCR.

        Args:
            image_path: Path to image file

        Returns:
            Extracted text string
        """
        if pytesseract is None:
            raise ImportError("pytesseract is required for OCR. Install with: pip install pytesseract")

        try:
            with Image.open(image_path) as img:
                text = pytesseract.image_to_string(img, lang='eng')
                return text.strip()
        except Exception as e:
            print(f"❌ OCR failed for image {image_path}: {e}")
            return ""

    @staticmethod
    def is_tesseract_available() -> bool:
        """Check if Tesseract OCR is available."""
        return pytesseract is not None

    @staticmethod
    def get_tesseract_languages() -> list:
        """Get list of available Tesseract languages."""
        if pytesseract is None:
            return []

        try:
            return pytesseract.get_languages()
        except:
            return ['eng']  # Default to English