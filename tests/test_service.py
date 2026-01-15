import pytest
import os
from fastapi import HTTPException
from app.services.converter_service import ConverterService
from app.plugins.json_to_md import JsonToMdConverter # Type check only if needed, mostly we check class name

def test_plugin_discovery():
    """Test that the service discovers the JSON converter."""
    service = ConverterService()
    
    # Check if .json extension is registered
    converter = service.get_converter("test.json")
    assert converter is not None
    # We can check the type or meta
    assert converter.meta.name == "json2md"

def test_unsupported_format_error():
    """Test that requesting an unknown format raises HTTPException."""
    service = ConverterService()
    
    with pytest.raises(HTTPException) as excinfo:
        service.get_converter("test.xyz")
    
    assert excinfo.value.status_code == 400
    assert "Unsupported file format" in excinfo.value.detail

def test_case_insensitivity():
    """Test that extension matching is case-insensitive."""
    service = ConverterService()
    
    converter = service.get_converter("TEST.JSON")
    assert converter is not None
