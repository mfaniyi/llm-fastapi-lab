from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from llm_fastapi_lab.monitoring import get_cost_per_100_requests
from llm_fastapi_lab.llm import extract_candidate


# Create the FastAPI application.
app = FastAPI(title="LLM FastAPI Lab")


@app.get("/")
def health_check():
    # Return a simple response to confirm the API is running.
    return {"status": "ok"}

class CandidateRequest(BaseModel):
    # Candidate text supplied by the API client.
    text: str

@app.post("/extract-candidate")
def extract_candidate_endpoint(request: CandidateRequest):
    try:
        # Extract structured candidate information using the LLM.
        result = extract_candidate(request.text)

    except RuntimeError as exc:
        # Return a clear service-unavailable response for LLM failures.
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    # Convert the Pydantic candidate object into JSON-compatible data.
    result["candidate"] = result["candidate"].model_dump()

    # Return the candidate data together with monitoring information.
    return result


@app.get("/monitoring/cost")
def monitoring_cost():
    # Return the estimated running cost scaled to 100 requests.
    return {
        "estimated_cost_per_100_requests_usd": get_cost_per_100_requests()
    }