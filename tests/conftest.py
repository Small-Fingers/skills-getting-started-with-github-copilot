"""Pytest configuration and shared fixtures."""

import pytest
from copy import deepcopy
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Provide a TestClient instance for testing the FastAPI application."""
    return TestClient(app)


@pytest.fixture
def fresh_activities():
    """Provide a fresh copy of the activities database for each test.
    
    This fixture ensures test isolation by providing a deep copy of the
    in-memory activities database, preventing state pollution between tests.
    """
    return deepcopy(app.activities)
