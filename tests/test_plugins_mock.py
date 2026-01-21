import pytest
from unittest.mock import AsyncMock, patch
from app.plugins.video_plugin import VideoConverter
from app.plugins.office_plugin import OfficeConverter

@pytest.mark.asyncio
async def test_video_converter_ffmpeg_call():
    """Verify VideoConverter calls ffmpeg with correct arguments."""
    converter = VideoConverter()
    input_path = "/tmp/input.mp4"
    output_path = "/tmp/output.mp3"
    
    # Mock subprocess
    with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_exec:
        # Configure mock process
        mock_process = AsyncMock()
        mock_process.communicate.return_value = (b"", b"")
        mock_process.returncode = 0
        mock_exec.return_value = mock_process

        await converter.convert(input_path, output_path, ".mp3")
        
        # Verify call
        # Expected: ffmpeg -i input.mp4 -vn -acodec libmp3lame -y output.mp3
        args = mock_exec.call_args[0]
        assert args[0] == "ffmpeg"
        assert args[1] == "-i"
        assert args[2] == input_path
        assert "-vn" in args
        assert "-acodec" in args
        assert "libmp3lame" in args
        assert output_path in args

@pytest.mark.asyncio
async def test_office_converter_soffice_call():
    """Verify OfficeConverter calls soffice with correct arguments."""
    converter = OfficeConverter()
    input_path = "/tmp/doc.docx"
    output_path = "/tmp/output/doc.pdf" # This logic depends on outdir
    
    # Mock subprocess
    with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_exec:
        # Configure mock process
        mock_process = AsyncMock()
        mock_process.communicate.return_value = (b"", b"")
        mock_process.returncode = 0
        mock_exec.return_value = mock_process

        # We need to make sure shutil.move isn't actually called or we mock it too,
        # because the plugin tries to move the file if paths differ.
        with patch("shutil.move") as mock_move:
            await converter.convert(input_path, output_path, ".pdf")
        
        # Verify call
        # Expected: soffice --headless --convert-to pdf --outdir /tmp/output /tmp/doc.docx
        args = mock_exec.call_args[0]
        cmd = args[0]
        assert "soffice" in cmd or cmd == "soffice"
        assert "--headless" in args
        assert "--convert-to" in args
        assert "pdf" in args
        assert "--outdir" in args
        assert input_path in args
