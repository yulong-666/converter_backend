from typing import Any
from PIL import Image
from loguru import logger

from app.plugins.base import BaseConverter, ConverterMeta


class ImageConverter(BaseConverter):
    """
    Converter for Image files.
    Supports basic image format conversions (JPG, PNG, WEBP) and Image-to-PDF.
    """

    def __init__(self, source_format: str):
        self._source_format = source_format

    @classmethod
    def supported_source_formats(cls) -> list[str]:
        return [".jpg", ".jpeg", ".png", ".webp"]

    @property
    def meta(self) -> ConverterMeta:
        return ConverterMeta(
            name=f"image-converter-{self._source_format.strip('.')}",
            description=f"Convert {self._source_format} images",
            source_format=self._source_format,
            supported_targets=[".png", ".jpg", ".jpeg", ".webp", ".pdf"],
        )

    async def convert(self, input_path: str, output_path: str, target_format: str, **kwargs: Any) -> str:
        if target_format not in self.meta.supported_targets:
            raise ValueError(f"Target format {target_format} is not supported by {self.meta.name}")

        try:
            with Image.open(input_path) as img:
                # Handle color mode conversions
                # JPG and PDF (usually) do not support RGBA (transparency)
                if img.mode == 'RGBA':
                    if target_format in ['.jpg', '.jpeg', '.pdf']:
                        img = img.convert('RGB')
                
                # Save
                img.save(output_path)
                return output_path

        except Exception as e:
            logger.error(f"Error converting image {input_path} to {target_format}: {e}")
            raise e
