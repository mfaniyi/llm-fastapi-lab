from fastapi.testclient import TestClient

from llm_fastapi_lab.main import app

# Create a test client for the FastAPI application.
client = TestClient(app)


def test_health_check():
    # Verify that the health endpoint returns a successful response.
    response = client.get("/")

    # Confirm the endpoint returns HTTP 200.
    assert response.status_code == 200

    # Confirm the expected health-check response.
    assert response.json() == {"status": "ok"}