import json
from typing import Any

import aiofiles
from loguru import logger

from app.plugins.base import BaseConverter, ConverterMeta


class JsonToMdConverter(BaseConverter):
    """
    Converter that transforms JSON files into Markdown code blocks.
    """

    @classmethod
    def supported_source_formats(cls) -> list[str]:
        return [".json"]

    @property
    def meta(self) -> ConverterMeta:
        return ConverterMeta(
            name="json2md",
            description="Convert JSON data to Markdown code block",
            source_format=".json",
            supported_targets=[".md"],
        )

    async def convert(self, input_path: str, output_path: str, target_format: str, **kwargs: Any) -> str:
        """
        Convert a JSON file to a Markdown file containing the JSON data in a code block.

        Args:
            input_path (str): Path to the source JSON file.
            output_path (str): Path where the Markdown file will be saved.
            target_format (str): The desired target format (must be ".md").
            **kwargs: Additional arguments (unused).

        Returns:
            str: Path to the generated Markdown file.

        Raises:
            ValueError: If the input file is not valid JSON or target format is unsupported.
        """
        if target_format not in self.meta.supported_targets:
            raise ValueError(f"Target format {target_format} is not supported by {self.meta.name}")
        try:
            # Asynchronously read the input JSON file
            async with aiofiles.open(input_path, mode="r", encoding="utf-8") as f:
                content = await f.read()

            # Parse JSON to ensure validity and re-format
            data = json.loads(content)
            json_str = json.dumps(data, indent=4, ensure_ascii=False)

            # Create Markdown content
            md_content = f"# Converted JSON Data\n\n```json\n{json_str}\n```\n"

            # Asynchronously write to the output Markdown file
            async with aiofiles.open(output_path, mode="w", encoding="utf-8") as f:
                await f.write(md_content)
            
            logger.info(f"Successfully converted {input_path} to {output_path}")
            return output_path

        except json.JSONDecodeError as e:
            error_msg = f"Failed to parse JSON file {input_path}: {e}"
            logger.error(error_msg)
            raise ValueError(error_msg) from e
        except Exception as e:
            error_msg = f"Unexpected error during conversion of {input_path}: {e}"
            logger.error(error_msg)
            raise e
