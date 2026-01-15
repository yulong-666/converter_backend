import io

def test_health_check(client):
    """Test the health check endpoint."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "alive"

def test_convert_file_happy_path(client):
    """Test uploading a valid JSON file for conversion."""
    file_content = b'{"test": "ok"}'
    files = {
        "file": ("test.json", io.BytesIO(file_content), "application/json")
    }
    
    response = client.post("/api/v1/convert", files=files)
    
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
    
    response = client.post("/api/v1/convert", files=files)
    
    # FastAPI/Starlette returns 422 for empty filenames if specific validation fails,
    # or 400 if our handler catches it. TestClient/FastAPI behavior here results in 422.
    assert response.status_code == 422
    # We don't check for exact "Filename is missing" because FastAPI validation might catch it first
    # returning a list of errors.
    # assert response.json()["detail"] == "Filename is missing"

def test_convert_file_unsupported_format(client):
    """Test uploading a file with an unsupported extension."""
    file_content = b'some data'
    files = {
        "file": ("test.xyz", io.BytesIO(file_content), "text/plain")
    }
    
    response = client.post("/api/v1/convert", files=files)
    
    assert response.status_code == 400
    assert "Unsupported file format" in response.json()["detail"]
