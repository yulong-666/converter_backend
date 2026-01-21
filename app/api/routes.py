import os
import shutil

from fastapi import APIRouter, File, HTTPException, UploadFile, BackgroundTasks, Form
from fastapi.responses import FileResponse

from app.core.config import get_settings
from app.core.logger import logger
from app.services.converter_service import ConverterService

router = APIRouter()
settings = get_settings()

# Initialize Service
converter_service = ConverterService()

# Temporary directories
UPLOAD_DIR = "temp/uploads"
OUTPUT_DIR = "temp/outputs"

# Ensure directories exist
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)


def remove_file(path: str):
    """
    Helper to remove a file and log any errors.
    """
    try:
        os.remove(path)
        logger.debug(f"Removed temporary file: {path}")
    except Exception as e:
        logger.warning(f"Failed to remove temporary file {path}: {e}")


@router.get("/health")
async def health_check():
    return {
        "status": "alive",
        "project_name": settings.PROJECT_NAME,
        "version": settings.VERSION,
    }


@router.get("/capabilities")
async def get_capabilities():
    """
    Get the list of supported conversions.
    """
    return converter_service.get_supported_conversions()


@router.post("/convert", response_class=FileResponse)
async def convert_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    target_format: str = Form(...)
):
    """
    Upload a file and convert it based on its extension.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is missing")

    input_path = None
    output_path = None

    try:
        # Generate input path
        input_path = os.path.join(UPLOAD_DIR, file.filename)
        
        # Determine strict absolute path to avoid traversal issues (basic check)
        input_path = os.path.abspath(input_path)

        # Save uploaded file
        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Execute conversion
        output_path = await converter_service.execute_conversion(input_path, OUTPUT_DIR, target_format=target_format)
        
        # Verify output exists
        if not os.path.exists(output_path):
             raise HTTPException(status_code=500, detail="Conversion generated no output")

        filename = os.path.basename(output_path)
        
        # Register cleanup tasks (Success Case)
        background_tasks.add_task(remove_file, input_path)
        background_tasks.add_task(remove_file, output_path)

        # Return file
        return FileResponse(
            path=output_path,
            filename=filename,
            media_type="application/octet-stream"
        )

    except Exception as e:
        # cleanup on failure
        if input_path and os.path.exists(input_path):
            remove_file(input_path)
        # If output path was somehow created but we are failing, clean it too
        if output_path and os.path.exists(output_path):
            remove_file(output_path)

        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Conversion failed: {str(e)}")
    finally:
        file.file.close()
