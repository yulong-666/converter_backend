import os
from typing import Dict

from fastapi import HTTPException
from loguru import logger

from app.plugins.base import BaseConverter
from app.plugins.json_to_md import JsonToMdConverter


class ConverterService:
    """
    Service to manage file converters and execute conversions.
    """
    _plugins: Dict[str, BaseConverter]

    def __init__(self):
        """
        Initialize the service and register available plugins.
        """
        self._plugins = {}
        self._register_plugins()

    def _register_plugins(self):
        """
        Register all available converter plugins.
        """
        # Register JsonToMdConverter
        json_converter = JsonToMdConverter()
        source_format = json_converter.meta.source_format
        self._plugins[source_format] = json_converter
        logger.info(f"Registered plugin: {json_converter.meta.name} for {source_format}")

    def get_converter(self, filename: str) -> BaseConverter:
        """
        Get the appropriate converter for a given filename based on its extension.

        Args:
            filename (str): The name or path of the file.

        Returns:
            BaseConverter: The matching converter instance.

        Raises:
            HTTPException: If no converter is found for the file extension.
        """
        _, ext = os.path.splitext(filename)
        ext = ext.lower()

        converter = self._plugins.get(ext)
        if not converter:
            logger.warning(f"No converter found for extension: {ext}")
            raise HTTPException(status_code=400, detail=f"Unsupported file format: {ext}")
        
        return converter

    async def execute_conversion(self, input_path: str, output_dir: str) -> str:
        """
        Execute the conversion for a given input file.

        Args:
            input_path (str): Absolute path to the input file.
            output_dir (str): Directory where the output file should be saved.

        Returns:
            str: Absolute path of the converted output file.
        """
        if not os.path.exists(input_path):
             raise FileNotFoundError(f"Input file not found: {input_path}")

        filename = os.path.basename(input_path)
        converter = self.get_converter(filename)
        
        # Determine output filename with new extension
        base_name, _ = os.path.splitext(filename)
        output_filename = f"{base_name}{converter.meta.target_format}"
        output_path = os.path.join(output_dir, output_filename)

        logger.info(f"Starting conversion: {input_path} -> {output_path} using {converter.meta.name}")
        
        # Execute conversion
        result_path = await converter.convert(input_path, output_path)
        
        return result_path
