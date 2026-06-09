# Tests

This directory contains comprehensive tests for the Mergington High School API backend.

## Test Structure

- `conftest.py` — Pytest configuration and shared fixtures
  - `client`: Provides a TestClient instance for HTTP testing
  - `fresh_activities`: Provides a fresh copy of the activities database for test isolation

- `test_app.py` — Integration tests for all API endpoints
  - `TestRoot` — Tests for GET `/` endpoint (redirect behavior)
  - `TestGetActivities` — Tests for GET `/activities` endpoint (list all activities)
  - `TestSignupForActivity` — Tests for POST `/activities/{activity_name}/signup` endpoint
  - `TestRemoveParticipant` — Tests for DELETE `/activities/{activity_name}/participants/{email}` endpoint

## Running Tests

### Run all tests
```bash
pytest tests/
```

### Run tests with verbose output
```bash
pytest tests/ -v
```

### Run a specific test class
```bash
pytest tests/test_app.py::TestGetActivities -v
```

### Run a specific test
```bash
pytest tests/test_app.py::TestSignupForActivity::test_signup_valid_activity_and_email -v
```

### Run tests and show test discovery
```bash
pytest tests/ --collect-only
```

## Test Coverage

The test suite covers:

- **Root Endpoint**: Redirect from `/` to static files
- **List Activities**: Retrieving all activities with proper structure and fields
- **Signup**: 
  - Valid signup scenarios
  - Duplicate prevention (same student, same activity)
  - Activity not found errors
  - Multiple activity signups allowed
  - Verification that participants are added
- **Remove Participant**:
  - Valid removal scenarios
  - Activity not found errors
  - Participant not found errors
  - Idempotent removal attempts

## Test Design Principles

1. **Isolation**: Each test uses a TestClient with a fresh application instance
2. **Clear naming**: Test names clearly describe what is being tested
3. **Single responsibility**: Each test verifies one specific behavior
4. **Fixtures**: Shared `client` fixture ensures consistent test setup

## Dependencies

The tests require:
- `pytest` — Test runner
- `httpx` — HTTP client (for TestClient)
- `fastapi` — Web framework

All dependencies are listed in `requirements.txt`.
