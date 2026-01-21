from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel


class ConverterMeta(BaseModel):
    """
    Metadata for a converter plugin.

    Attributes:
        name (str): Unique name of the plugin (e.g., "word2pdf").
        description (str): Brief description of what the plugin does.
        source_format (str): The extension of the source file (e.g., ".docx").
        supported_targets (list[str]): List of supported target format extensions (e.g., [".pdf", ".txt"]).
    """
    name: str
    description: str
    source_format: str
    supported_targets: list[str]


class BaseConverter(ABC):
    """
    Abstract base class for all file converters.
    All converter plugins must inherit from this class and implement the abstract methods.
    """

    @property
    @abstractmethod
    def meta(self) -> ConverterMeta:
        """
        Metadata for the converter.
        Must be implemented by subclasses to provide plugin details.
        """
        pass

    @abstractmethod
    async def convert(self, input_path: str, output_path: str, target_format: str, **kwargs: Any) -> str:
        """
        Execute the file conversion logic.

        Args:
            input_path (str): Absolute path to the input file.
            output_path (str): Absolute path where the output file should be saved.
            target_format (str): The desired target format extension (e.g., ".pdf").
            **kwargs: Additional keyword arguments for the conversion process.

        Returns:
            str: The absolute path of the converted output file.
        """
        pass

    async def validate(self, input_path: str) -> bool:
        """
        Validate the input file before conversion.
        Subclasses can override this to perform specific validation checks.

        Args:
            input_path (str): Absolute path to the input file.

        Returns:
            bool: True if valid, False otherwise. Defaults to True.
        """
        return True
