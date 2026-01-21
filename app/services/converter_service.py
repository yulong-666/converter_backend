import os
from typing import Dict

from fastapi import HTTPException
from loguru import logger

import importlib
import pkgutil
import inspect
import app.plugins
from app.plugins.base import BaseConverter

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
        Dynamically register all available converter plugins from app.plugins package.
        """
        package_path = os.path.dirname(app.plugins.__file__)
        package_name = app.plugins.__name__

        # Iterate over all modules in the app.plugins package
        for _, name, _ in pkgutil.iter_modules([package_path]):
            # Skip base module
            if name == "base":
                continue
            
            try:
                # Import module
                module = importlib.import_module(f"{package_name}.{name}")
                
                # Inspect module for BaseConverter subclasses
                for _, obj in inspect.getmembers(module):
                    if (inspect.isclass(obj) and 
                        issubclass(obj, BaseConverter) and 
                        obj is not BaseConverter):
                        
                        # Use the new supported_source_formats method
                        source_formats = obj.supported_source_formats()
                        
                        for fmt in source_formats:
                            # Instantiate with specific source format if the init takes it, 
                            # or default init if compatible.
                            # Most our plugins taking 'source_format' in init work fine with this.
                            try:
                                # We check signature ?? Or just assume convention.
                                # Convention: __init__(self, source_format=default) or ()
                                # If we pass source_format, multi-format plugins work.
                                # Single format plugins (JsonToMd) don't have source_format in init (implicit).
                                # We might need to inspect signature.
                                
                                sig = inspect.signature(obj.__init__)
                                if 'source_format' in sig.parameters:
                                    instance = obj(source_format=fmt)
                                else:
                                    instance = obj()
                                    # Verification: if instance.meta.source_format != fmt...
                                    # Single source plugins like JsonToMd hardcode source_format in meta.
                                    # If they claim to support '.json' but strict check fails, that's their bug.
                                
                                self._plugins[fmt] = instance
                                logger.info(f"Registered plugin: {instance.meta.name} for {fmt}")
                            except Exception as e:
                                logger.error(f"Failed to instantiate plugin {obj.__name__} for {fmt}: {e}")

            except Exception as e:
                logger.error(f"Error loading plugin module {name}: {e}")

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

    def get_supported_conversions(self) -> Dict[str, list[str]]:
        """
        Get a dictionary of all supported source formats and their target formats.

        Returns:
            Dict[str, list[str]]: Mapping of source extension to list of target extensions.
        """
        capabilities = {}
        for ext, converter in self._plugins.items():
            capabilities[ext] = converter.meta.supported_targets
        return capabilities

    async def execute_conversion(self, input_path: str, output_dir: str, target_format: str) -> str:
        """
        Execute the conversion for a given input file.

        Args:
            input_path (str): Absolute path to the input file.
            output_dir (str): Directory where the output file should be saved.
            target_format (str): The desired target format extension.

        Returns:
            str: Absolute path of the converted output file.
        """
        if not os.path.exists(input_path):
             raise FileNotFoundError(f"Input file not found: {input_path}")

        filename = os.path.basename(input_path)
        converter = self.get_converter(filename)
        
        # Validate target format
        if target_format not in converter.meta.supported_targets:
            raise HTTPException(
                status_code=400, 
                detail=f"Conversion from {converter.meta.source_format} to {target_format} is not supported."
            )

        # Determine output filename with new extension
        base_name, _ = os.path.splitext(filename)
        # Ensure target_format starts with dot if not provided (though it should be)
        if not target_format.startswith("."):
            target_format = f".{target_format}"
            
        output_filename = f"{base_name}{target_format}"
        output_path = os.path.join(output_dir, output_filename)

        logger.info(f"Starting conversion: {input_path} -> {output_path} using {converter.meta.name}")
        
        # Execute conversion
        result_path = await converter.convert(input_path, output_path, target_format=target_format)
        
        return result_path
