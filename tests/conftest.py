import sys
import os
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

# Add project root to sys.path so we can import 'app'
# This ensures tests can run even if the package isn't installed in editable mode
sys.path.append(str(Path(__file__).parent.parent))

from main import app

@pytest.fixture(scope="module")
def client():
    # Use TestClient as a context manager to trigger startup/shutdown events
    with TestClient(app) as c:
        yield c
