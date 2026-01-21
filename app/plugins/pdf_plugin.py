import os
from typing import Any
import fitz  # PyMuPDF
from pdf2docx import Converter as Pdf2DocxConverter
from loguru import logger

from app.plugins.base import BaseConverter, ConverterMeta


class PdfConverter(BaseConverter):
    """
    Converter for PDF files.
    Supports conversion to DOCX, PNG, TXT, and MD.
    """

    @classmethod
    def supported_source_formats(cls) -> list[str]:
        return [".pdf"]

    @property
    def meta(self) -> ConverterMeta:
        return ConverterMeta(
            name="pdf-converter",
            description="Convert PDF documents to Word, Image, or Text",
            source_format=".pdf",
            supported_targets=[".docx", ".png", ".txt", ".md"],
        )

    async def convert(self, input_path: str, output_path: str, target_format: str, **kwargs: Any) -> str:
        """
        Convert PDF to specified format.
        """
        if target_format not in self.meta.supported_targets:
            raise ValueError(f"Target format {target_format} is not supported by {self.meta.name}")

        try:
            if target_format == ".docx":
                return self._convert_to_docx(input_path, output_path)
            elif target_format == ".png":
                return self._convert_to_png(input_path, output_path)
            elif target_format in [".txt", ".md"]:
                return self._convert_to_text(input_path, output_path, target_format)
            else:
                raise ValueError(f"Unimplemented format: {target_format}")

        except Exception as e:
            logger.error(f"Error converting PDF {input_path} to {target_format}: {e}")
            raise e

    def _convert_to_docx(self, input_path: str, output_path: str) -> str:
        cv = Pdf2DocxConverter(input_path)
        cv.convert(output_path, start=0, end=None)
        cv.close()
        return output_path

    def _convert_to_png(self, input_path: str, output_path: str) -> str:
        # For MVP, only convert the first page to an image
        doc = fitz.open(input_path)
        page = doc[0]  # first page
        pix = page.get_pixmap()
        pix.save(output_path)
        doc.close()
        return output_path

    def _convert_to_text(self, input_path: str, output_path: str, target_format: str) -> str:
        doc = fitz.open(input_path)
        text = ""
        for page in doc:
            text += page.get_text()
        
        doc.close()

        # Wrap in markdown code block if MD is requested, or just raw text
        content = text
        if target_format == ".md":
             content = f"# Extracted Text\n\n```text\n{text}\n```"

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        return output_path
