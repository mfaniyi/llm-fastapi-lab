from fastapi.testclient import TestClient
from llm_fastapi_lab.main import app
from unittest.mock import patch
from llm_fastapi_lab.models import CandidateExtraction

# Create a test client for the FastAPI application.
client = TestClient(app)


def test_health_check():
    # Verify that the health endpoint returns a successful response.
    response = client.get("/")

    # Confirm the endpoint returns HTTP 200.
    assert response.status_code == 200

    # Confirm the expected health-check response.
    assert response.json() == {"status": "ok"}


def test_extract_candidate_success():
    # Define the structured result that the mocked LLM will return.
    mock_candidate = CandidateExtraction(
        name="Jane Smith",
        role="Data Analyst",
        experience_years=4,
    )

    # Replace the real LLM function with a controlled mock response.
    with patch(
        "llm_fastapi_lab.main.extract_candidate",
        return_value={
            "candidate": mock_candidate,
            "latency_seconds": 1.2,
            "input_tokens": 100,
            "output_tokens": 50,
            "estimated_cost_usd": 0.000125,
            "attempts": 1,
            "success": True,
        },
    ):
        # Send a candidate extraction request to the API.
        response = client.post(
            "/extract-candidate",
            json={
                "text": "Jane Smith is a Data Analyst with 4 years of experience."
            },
        )

    # Confirm that the API request succeeded.
    assert response.status_code == 200

    # Read the JSON response returned by the API.
    data = response.json()

    # Verify that the candidate was extracted correctly.
    assert data["candidate"]["name"] == "Jane Smith"
    assert data["candidate"]["role"] == "Data Analyst"
    assert data["candidate"]["experience_years"] == 4

    # Verify that monitoring information is included.
    assert data["attempts"] == 1
    assert data["success"] is True


def test_extract_candidate_invalid_request():
    # Send a request without the required "text" field.
    response = client.post(
        "/extract-candidate",
        json={},
    )

    # FastAPI should reject the invalid request.
    assert response.status_code == 422

    # Confirm the validation error identifies the missing field.
    data = response.json()
    assert data["detail"][0]["loc"][-1] == "text"


def test_extract_candidate_llm_failure():
    # Replace the LLM function with a controlled failure.
    with patch(
        "llm_fastapi_lab.main.extract_candidate",
        side_effect=RuntimeError(
            "LLM request failed after two attempts. Please try again later."
        ),
    ):
        # Send a valid candidate request to the API.
        response = client.post(
            "/extract-candidate",
            json={
                "text": "John Doe is a Software Engineer with 5 years of experience."
            },
        )

    # Confirm that the API reports the service failure.
    assert response.status_code == 503

    # Confirm that the expected error message is returned.
    assert response.json()["detail"] == (
        "LLM request failed after two attempts. Please try again later."
    )


def test_extract_candidate_malformed_response():
    # Replace the LLM function with a controlled malformed-response failure.
    with patch(
        "llm_fastapi_lab.main.extract_candidate",
        side_effect=RuntimeError(
            "LLM returned an invalid structured response after two attempts."
        ),
    ):
        # Send a valid candidate request to the API.
        response = client.post(
            "/extract-candidate",
            json={
                "text": "Jane Doe is a Product Manager with 6 years of experience."
            },
        )

    # Confirm that the API reports the failure as a service error.
    assert response.status_code == 503

    # Confirm that the expected malformed-response message is returned.
    assert response.json()["detail"] == (
        "LLM returned an invalid structured response after two attempts."
    ) 


def test_monitoring_cost():
    # Request the running cost estimate from the monitoring endpoint.
    response = client.get("/monitoring/cost")

    # Confirm that the endpoint responds successfully.
    assert response.status_code == 200

    # Confirm that the cost field is included in the response.
    data = response.json()
    assert "estimated_cost_per_100_requests_usd" in data

    # Confirm that the returned cost is numeric.
    assert isinstance(data["estimated_cost_per_100_requests_usd"], (int, float))