# LLM FastAPI Lab

A practical FastAPI application that integrates an Azure OpenAI / Microsoft Foundry LLM for structured candidate information extraction.

The project demonstrates how to build an LLM-backed API that:

* Accepts unstructured candidate information.
* Uses an LLM to extract structured candidate data.
* Validates the structured response.
* Retries failed LLM requests once.
* Handles timeouts and malformed responses safely.
* Tracks latency, token usage, and estimated cost.
* Provides a simple web interface for interacting with the API.

## Project Goal

The goal of this lab is to understand how to integrate an LLM into a FastAPI application while making the integration more reliable, observable, and suitable for production-oriented workflows.

## Architecture

The application follows this flow:

```text
Client / Frontend
       |
       v
    FastAPI
       |
       v
Candidate Extraction Logic
       |
       v
Azure OpenAI / Microsoft Foundry
       |
       v
Structured LLM Response
       |
       v
Pydantic Validation
       |
       v
JSON Response
```

Monitoring information is collected during each LLM request:

```text
LLM Request
    |
    +-- Latency
    +-- Input Tokens
    +-- Output Tokens
    +-- Estimated Cost
    +-- Attempts
    +-- Success / Failure
```

## Features

### Structured LLM Extraction

The application extracts:

* Candidate name
* Job role
* Years of professional experience

The extracted information is returned using a Pydantic model:

```python
class CandidateExtraction(BaseModel):
    name: str
    role: str
    experience_years: int
```

### Retry and Failure Handling

The application allows one retry when an LLM request fails.

It handles:

* Request timeouts
* OpenAI API errors
* Malformed structured responses

After two unsuccessful attempts, the application fails safely instead of returning invalid candidate data.

FastAPI converts controlled LLM failures into an HTTP `503 Service Unavailable` response.

### Structured Response Validation

The application validates the extracted candidate before accepting the response.

A candidate is considered invalid when:

* The name is empty.
* The role is empty.
* Experience is negative.

### LLM Monitoring

Each successful LLM request records:

* Model/deployment
* Latency
* Input tokens
* Output tokens
* Estimated cost
* Number of attempts
* Success status

The application also exposes an endpoint for estimated cost per 100 requests.

### Simple Frontend

A lightweight HTML, CSS, and JavaScript interface is included.

The frontend allows users to:

1. Enter candidate information.
2. Submit it to FastAPI.
3. Display the structured candidate information.
4. Display latency and estimated cost.
5. Show loading and error states.

## Project Structure

```text
llm-fastapi-lab/
├── .gitignore
├── .python-version
├── README.md
├── pyproject.toml
├── uv.lock
│
└── src/
    └── llm_fastapi_lab/
        ├── __init__.py
        ├── llm.py
        ├── main.py
        ├── models.py
        ├── monitoring.py
        │
        └── static/
            └── index.html
```

## Technologies

* Python
* FastAPI
* Pydantic
* OpenAI Python SDK
* Azure OpenAI / Microsoft Foundry
* HTML
* CSS
* JavaScript
* uv
* Git / GitHub

## Requirements

* Python 3.14+
* uv
* An Azure OpenAI / Microsoft Foundry deployment
* Azure OpenAI API credentials

## Installation

Clone the repository:

```bash
git clone https://github.com/mfaniyi/llm-fastapi-lab.git
cd llm-fastapi-lab
```

Install the project dependencies with uv:

```bash
uv sync
```

## Environment Variables

Create a `.env` file in the project root:

```env
AZURE_OPENAI_ENDPOINT=your_endpoint
AZURE_OPENAI_API_KEY=your_api_key
AZURE_OPENAI_DEPLOYMENT=your_deployment_name
```

Do not commit `.env` or API keys to GitHub.

## Running the Application

Start the FastAPI development server:

```bash
uv run fastapi dev src/llm_fastapi_lab/main.py
```

The API will be available at:

```text
http://127.0.0.1:8000
```

## Frontend

Open:

```text
http://127.0.0.1:8000/ui
```

The frontend provides a simple interface for candidate extraction.

Example input:

```text
Jane Smith is a Data Analyst with 4 years of professional experience.
```

Example result:

```json
{
    "candidate": {
        "name": "Jane Smith",
        "role": "Data Analyst",
        "experience_years": 4
    },
    "latency_seconds": 7.03,
    "input_tokens": 101,
    "output_tokens": 138,
    "estimated_cost_usd": 0.000263,
    "attempts": 1,
    "success": true
}
```

## API Endpoints

### Health Check

```http
GET /
```

Example:

```bash
curl http://127.0.0.1:8000/
```

Response:

```json
{
    "status": "ok"
}
```

### Extract Candidate

```http
POST /extract-candidate
```

Example:

```bash
curl -X POST "http://127.0.0.1:8000/extract-candidate" \
  -H "Content-Type: application/json" \
  -d "{\"text\":\"Jane Smith is a Data Analyst with 4 years of professional experience.\"}"
```

### Monitoring Cost

```http
GET /monitoring/cost
```

Example:

```bash
curl http://127.0.0.1:8000/monitoring/cost
```

Example response:

```json
{
    "estimated_cost_per_100_requests_usd": 0.024
}
```

## Error Handling

### LLM Timeout

When an LLM request times out:

```text
Attempt 1 → Timeout
Attempt 2 → Timeout
         ↓
HTTP 503
```

Example response:

```json
{
    "detail": "LLM request failed after two attempts. Please try again later."
}
```

### Malformed Structured Response

When the LLM produces an invalid candidate:

```text
Attempt 1 → Invalid response
Attempt 2 → Invalid response
         ↓
HTTP 503
```

Example response:

```json
{
    "detail": "LLM returned an invalid structured response after two attempts."
}
```

## Monitoring and Cost Estimation

The application estimates LLM cost using input and output token usage.

The calculation is:

```text
Input Cost =
(input tokens / 1,000,000) × input price

Output Cost =
(output tokens / 1,000,000) × output price

Total Cost =
Input Cost + Output Cost
```

The current lab pricing configuration uses:

```text
Input:  $0.25 / 1M tokens
Output: $2.00 / 1M tokens
```

These values are configured for the lab's cost estimation and should be updated if the model pricing changes.

## Development Workflow

The project uses `uv` for Python environment and dependency management.

Typical workflow:

```bash
uv sync
uv run fastapi dev src/llm_fastapi_lab/main.py
```

Git changes are committed incrementally at meaningful milestones.

## Learning Objectives

This project was built to practice:

* FastAPI API development
* LLM integration
* Structured outputs
* Function/tool-style structured extraction
* Pydantic validation
* Prompt design
* Retry strategies
* Timeout handling
* Failure handling
* Token monitoring
* Latency monitoring
* LLM cost estimation
* Frontend-to-API integration
* Git and GitHub workflows

## Current Status

The lab currently provides a working end-to-end LLM application:

```text
Browser
   ↓
Frontend
   ↓
FastAPI
   ↓
LLM Integration
   ↓
Azure OpenAI / Microsoft Foundry
   ↓
Structured Output
   ↓
Validation
   ↓
Monitoring
   ↓
JSON Response
```

The application has been tested for both successful requests and controlled failure scenarios.

## Future Improvements

Potential future enhancements include:

* Persistent monitoring storage
* Authentication
* Automated tests for failure scenarios
* More sophisticated candidate validation
* Centralized logging
* Production deployment
* Docker containerization
* Database-backed candidate storage
* Authentication and authorization
* Improved frontend design
* Automated CI/CD with GitHub Actions

## License

This project is currently intended as a learning and development project.
