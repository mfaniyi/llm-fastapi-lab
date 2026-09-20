from fastapi import FastAPI
from pydantic import BaseModel

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
    result = extract_candidate(request.text)

    # Convert the Pydantic candidate object into JSON-compatible data.
    result["candidate"] = result["candidate"].model_dump()

    # Return the candidate data together with monitoring information.
    return result