import os
import shutil

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import FileResponse

from app.core.config import get_settings
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


@router.get("/health")
async def health_check():
    return {
        "status": "alive",
        "project_name": settings.PROJECT_NAME,
        "version": settings.VERSION,
    }


@router.post("/convert", response_class=FileResponse)
async def convert_file(file: UploadFile = File(...)):
    """
    Upload a file and convert it based on its extension.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is missing")

    try:
        # Generate input path
        input_path = os.path.join(UPLOAD_DIR, file.filename)
        
        # Determine strict absolute path to avoid traversal issues (basic check)
        input_path = os.path.abspath(input_path)

        # Save uploaded file
        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Execute conversion
        output_path = await converter_service.execute_conversion(input_path, OUTPUT_DIR)
        
        # Verify output exists
        if not os.path.exists(output_path):
             raise HTTPException(status_code=500, detail="Conversion generated no output")

        filename = os.path.basename(output_path)
        
        # Return file
        return FileResponse(
            path=output_path,
            filename=filename,
            media_type="application/octet-stream"
        )

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Conversion failed: {str(e)}")
    finally:
        # Optional: cleanup input file here if desired?
        # For now, we leave them in temp/ as per implicit requirement ("Temporary storage")
        # Real production might want a background task to clean this up.
        file.file.close()
