
import asyncio
import os
import sys

# Add project root to path
sys.path.append(os.getcwd())

from app.services.converter_service import ConverterService

async def verify_plugins():
    print("Verifying Plugin Registration...")
    
    service = ConverterService()
    caps = service.get_supported_conversions()
    print(f"[INFO] Capabilities: {caps}")

    # Check PDF
    assert ".pdf" in caps, "PDF support missing"
    assert ".docx" in caps[".pdf"], "PDF->DOCX missing"
    assert ".png" in caps[".pdf"], "PDF->PNG missing"
    print("[PASS] PDF Plugin registered.")

    # Check Images
    images = [".jpg", ".jpeg", ".png", ".webp"]
    for img in images:
        assert img in caps, f"{img} support missing"
        assert ".pdf" in caps[img], f"{img}->PDF missing"
    print("[PASS] Image Plugins registered.")

    print("\nVerification Complete.")

if __name__ == "__main__":
    try:
        asyncio.run(verify_plugins())
    except Exception as e:
        print(f"Verification Failed: {e}")
        sys.exit(1)
