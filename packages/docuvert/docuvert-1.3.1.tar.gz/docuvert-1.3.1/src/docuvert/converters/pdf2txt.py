
import sys
import os
# Add the parent directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from core.ast import ASTNode
from core.exceptions import ConversionError, DependencyError
from utils.ocr_utils import OCRExtractor

class Pdf2TxtConverter:
    """
    Converts a PDF file to a plain text file.
    """
    def parse_pdf2ast(self, input_path: str) -> ASTNode:
        """
        Parses a PDF file and converts it to an AST.

        Args:
            input_path (str): The path to the input PDF file.

        Returns:
            ASTNode: The root of the generated AST.
        """
        # TODO: Implement the logic to parse the PDF and build an AST.
        print(f"Parsing PDF at {input_path} and converting to AST.")
        return ASTNode(type="root")

    def ast2txt(self, ast_root: ASTNode, output_path: str):
        """
        Converts an AST to a plain text file.

        Args:
            ast_root (ASTNode): The root of the AST.
            output_path (str): The path to the output plain text file.
        """
        # TODO: Implement the logic to convert the AST to a plain text document.
        print(f"Converting AST to plain text at {output_path}")

    def _extract_text_from_pdf(self, input_path: str) -> str:
        """Extract text from PDF using OCR utility."""
        return OCRExtractor.extract_text_from_pdf(input_path, use_ocr=True)

    def convert(self, input_path: str, output_path: str):
        """
        Converts a PDF file to a plain text file using text extraction and OCR.

        Args:
            input_path (str): The path to the input PDF file.
            output_path (str): The path to the output plain text file.
        """
        if not os.path.exists(input_path):
            raise ConversionError(f"Input file not found: {input_path}")

        try:
            print(f"🔄 Converting PDF to text: {input_path}")
            text = self._extract_text_from_pdf(input_path)

            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(text)

            print(f"✅ Successfully converted '{input_path}' to '{output_path}'")

        except Exception as e:
            raise ConversionError(
                f"PDF to text conversion failed: {e}",
                source_format="pdf",
                target_format="txt",
                suggestions=[
                    "For scanned PDFs, install OCR support: pip install pytesseract",
                    "Install Tesseract: brew install tesseract (macOS) or apt-get install tesseract-ocr (Linux)",
                    "Ensure PDF is not corrupted or password-protected"
                ]
            )
