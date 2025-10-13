
import sys
import os
# Add the parent directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from core.ast import ASTNode
from core.exceptions import ConversionError, DependencyError
from utils.ocr_utils import OCRExtractor
import pypandoc

class Pdf2MdConverter:
    """
    Converts a PDF file to a Markdown file.
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

    def ast2md(self, ast_root: ASTNode, output_path: str):
        """
        Converts an AST to a Markdown file.

        Args:
            ast_root (ASTNode): The root of the AST.
            output_path (str): The path to the output Markdown file.
        """
        # TODO: Implement the logic to convert the AST to a Markdown document.
        print(f"Converting AST to Markdown at {output_path}")

    def convert(self, input_path: str, output_path: str):
        """
        Converts a PDF file to a Markdown file using text extraction and OCR.

        Args:
            input_path (str): The path to the input PDF file.
            output_path (str): The path to the output Markdown file.
        """
        if not os.path.exists(input_path):
            raise ConversionError(f"Input file not found: {input_path}")

        try:
            print(f"🔄 Converting PDF to Markdown: {input_path}")

            # Extract text using OCR-enabled extraction
            text = OCRExtractor.extract_text_from_pdf(input_path, use_ocr=True)

            if not text.strip():
                text = "No text could be extracted from this PDF."

            # Convert to markdown format with basic structure
            markdown_content = self._format_as_markdown(text)

            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)

            print(f"✅ Successfully converted '{input_path}' to '{output_path}'")

        except Exception as e:
            raise ConversionError(
                f"PDF to Markdown conversion failed: {e}",
                source_format="pdf",
                target_format="markdown",
                suggestions=[
                    "For scanned PDFs, install OCR support: pip install pytesseract",
                    "Install Tesseract: brew install tesseract (macOS) or apt-get install tesseract-ocr (Linux)",
                    "Ensure PDF is not corrupted or password-protected"
                ]
            )

    def _format_as_markdown(self, text: str) -> str:
        """Format extracted text as markdown with basic structure."""
        lines = text.split('\n')
        markdown_lines = []

        # Add a title
        markdown_lines.append("# Extracted PDF Content\n")

        for line in lines:
            line = line.strip()
            if not line:
                markdown_lines.append("")
                continue

            # Check if line looks like a page header
            if line.startswith("--- Page"):
                markdown_lines.append(f"\n## {line}\n")
            else:
                markdown_lines.append(line)

        return '\n'.join(markdown_lines)
