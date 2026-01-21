import asyncio
import os
import shutil
from app.plugins.base import BaseConverter, ConverterMeta
from app.core.logger import logger

class OfficeConverter(BaseConverter):
    """
    Converter for Office documents using LibreOffice (soffice).
    """

    @property
    def meta(self) -> ConverterMeta:
        return ConverterMeta(
            name="office-converter",
            description="Converts Office documents using LibreOffice.",
            source_format=".docx", # Dynamic registration handles others
            supported_targets=["pdf"]
        )
    
    def __init__(self, source_format: str = ".docx"):
        self._source_format = source_format

    @classmethod
    def supported_source_formats(cls) -> list[str]:
        return [".docx", ".pptx"]

    async def convert(self, input_path: str, output_path: str, target_format: str, **kwargs) -> str:
        """
        Convert office doc using soffice subprocess.
        """
        if target_format.lower() != ".pdf":
             raise ValueError(f"OfficeConverter only supports PDF output, got {target_format}")

        # soffice --headless --convert-to pdf --outdir {output_dir} {input_path}
        # Note: soffice outputs the file with the same name but .pdf extension in the outdir.
        # We need to make sure we align with the service's expected output_path.
        
        output_dir = os.path.dirname(output_path)
        expected_filename = os.path.splitext(os.path.basename(input_path))[0] + ".pdf"
        actual_output_path = os.path.join(output_dir, expected_filename)

        args = [
            "--headless",
            "--convert-to", "pdf",
            "--outdir", output_dir,
            input_path
        ]
        
        # On Windows it might be 'soffice.exe' or need full path. 
        # On Linux/Docker it's 'soffice'.
        # We assume 'soffice' is in PATH.
        cmd = "soffice"
        if os.name == 'nt':
             # Fallback check for common windows paths or assume 'soffice' is in PATH
             pass

        logger.info(f"Running soffice: {cmd} {' '.join(args)}")

        process = await asyncio.create_subprocess_exec(
            cmd,
            *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            error_msg = stderr.decode().strip()
            # LibreOffice sometimes writes mild warnings to stderr, check returncode strictly
            logger.error(f"LibreOffice failed: {error_msg}")
            raise RuntimeError(f"Office conversion failed: {error_msg}")

        # Ideally, we should now rename/move the file if output_path is different from actual_output_path
        # But usually converter_service asks for [name].pdf so it matches.
        if actual_output_path != output_path and os.path.exists(actual_output_path):
            shutil.move(actual_output_path, output_path)
            
        return output_path
