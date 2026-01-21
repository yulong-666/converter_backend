import io

def test_health_check(client):
    """Test the health check endpoint."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "alive"

def test_capabilities(client):
    """Test the capabilities endpoint."""
    response = client.get("/api/v1/capabilities")
    assert response.status_code == 200
    data = response.json()
    # Direct dictionary of source -> [targets]
    assert ".json" in data
    assert ".md" in data[".json"]

def test_convert_file_happy_path(client):
    """Test uploading a valid JSON file for conversion."""
    file_content = b'{"test": "ok"}'
    files = {
        "file": ("test.json", io.BytesIO(file_content), "application/json")
    }
    data = {
        "target_format": ".md"
    }
    
    response = client.post("/api/v1/convert", files=files, data=data)
    
    if response.status_code != 200:
        print(f"DEBUG: Response status: {response.status_code}")
        print(f"DEBUG: Response body: {response.json()}")
    
    assert response.status_code == 200
    assert "application/octet-stream" in response.headers["content-type"]
    
    # Check if the content resembles Markdown from our plugin
    # Expected output: "# Converted JSON Data\n\n```json..."
    content = response.content.decode("utf-8")
    assert "# Converted JSON Data" in content
    assert '"test": "ok"' in content

def test_convert_file_no_filename(client):
    """Test uploading a file without a filename."""
    file_content = b'{}'
    files = {
        "file": ("", io.BytesIO(file_content), "application/json")
    }
    data = {
        "target_format": ".md"
    }
    
    response = client.post("/api/v1/convert", files=files, data=data)
    
    # FastAPI/Starlette returns 422 for empty filenames if specific validation fails,
    # or 400 if our handler catches it. TestClient/FastAPI behavior here results in 422.
    assert response.status_code == 422

def test_convert_file_unsupported_format(client):
    """Test uploading a file with an unsupported extension."""
    file_content = b'some data'
    files = {
        "file": ("test.xyz", io.BytesIO(file_content), "text/plain")
    }
    data = {
        "target_format": ".md"
    }
    
    response = client.post("/api/v1/convert", files=files, data=data)
    
    assert response.status_code == 400
    assert "Unsupported file format" in response.json()["detail"]

def test_convert_file_cleanup_on_error(client, mocker):
    """Test that input file is removed if conversion fails."""
    # We need to mock the converter service to fail
    # Since we are using an integration test with a real app, we need to patch 
    # the method on the actual service instance or ensuring the dependency override works.
    # However, for simplicity in this setup, we can try to rely on side-effects or 
    # just patch 'app.api.routes.converter_service.execute_conversion' if possible.
    # But since 'converter_service' is imported in routes, we patch it there.
    
    # Note: 'mocker' fixture requires pytest-mock. If not available, we might skip or fail.
    # Assuming pytest-mock is installed or we use unittest.mock.
    
    import app.api.routes
    from unittest.mock import AsyncMock
    
    # Create a mock that raises an exception
    mock_convert = AsyncMock(side_effect=Exception("Simulated Conversion Failure"))
    
    # Patch the method on the imported service instance
    # We need to be careful about where we patch. 
    # 'app.api.routes.converter_service' is the instance.
    mocker.patch.object(app.api.routes.converter_service, 'execute_conversion', side_effect=Exception("Simulated Failure"))
    
    file_content = b'{"fail": "me"}'
    files = {
        "file": ("fail.json", io.BytesIO(file_content), "application/json")
    }
    data = {
        "target_format": ".md"
    }
    
    # We also want to verify file existence, but since the test runs in same process/thread usually with TestClient,
    # checking os.path.exists during the request is hard.
    # Instead, we rely on the log or side-effect that the file is gone AFTER the request.
    # But wait, if we mock execute_conversion, the file SHOULD exist before the mock is called.
    # The route saves the file, then calls execute_conversion.
    # If execute_conversion fails, the route's exception handler should remove the file.
    
    # We can spy on os.remove to see if it was called with the expected path.
    mock_remove = mocker.patch("app.api.routes.remove_file", wraps=app.api.routes.remove_file)
    
    response = client.post("/api/v1/convert", files=files, data=data)
    
    assert response.status_code == 500
    assert "Conversion failed" in response.json()["detail"]
    
    # Verify remove_file was called.
    # We expect it to be called for input_path.
    assert mock_remove.call_count >= 1
    # We can inspect call args if we want to be strict, but determining the exact temp path is tricky without regex match on the uuid/filename.

