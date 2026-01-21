import asyncio
import os
from app.plugins.base import BaseConverter, ConverterMeta
from app.core.logger import logger

class VideoConverter(BaseConverter):
    """
    Converter for video files using FFmpeg.
    """

    @property
    def meta(self) -> ConverterMeta:
        return ConverterMeta(
            name="video-converter",
            description="Converts video files using FFmpeg.",
            source_format=".mp4",  # Dynamic registration will handle others
            supported_targets=["mp3", "gif", "wav", "mkv", "avi"]
        )

    def __init__(self, source_format: str = ".mp4"):
        self._source_format = source_format

    @classmethod
    def supported_source_formats(cls) -> list[str]:
        return [".mp4", ".avi", ".mov", ".mkv"]

    async def convert(self, input_path: str, output_path: str, target_format: str, **kwargs) -> str:
        """
        Convert video using ffmpeg subprocess.
        """
        # Ensure target format is clean (no dot for ffmpeg check usually, but output_path has it)
        # target_format coming in has dot, e.g. ".mp3"
        
        target_ext = target_format.lower().lstrip(".")
        
        # Build command based on target
        # Default generic conversion
        args = ["-i", input_path]

        if target_ext == "mp3":
            # Extract audio: -vn (no video), -acodec libmp3lame
            args.extend(["-vn", "-acodec", "libmp3lame"])
        
        elif target_ext == "gif":
            # Create GIF: scale and fps
            # example: -vf "fps=10,scale=320:-1:flags=lanczos"
            args.extend(["-vf", "fps=10,scale=320:-1:flags=lanczos"])
        
        # For wav, mkv, avi we typically just let ffmpeg handle auto-detection or copy codecs if appropriate.
        # But simple re-encoding is safer for compatibility.
        # We also need 'y' to overwrite if it exists (though service usually handles path uniqueness, ffmpeg prompts without -y)
        args.append("-y") 
        args.append(output_path)

        logger.info(f"Running ffmpeg: ffmpeg {' '.join(args)}")

        process = await asyncio.create_subprocess_exec(
            "ffmpeg",
            *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            error_msg = stderr.decode().strip()
            logger.error(f"FFmpeg failed: {error_msg}")
            raise RuntimeError(f"Video conversion failed: {error_msg}")

        return output_path
