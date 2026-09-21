import os
import time

from dotenv import load_dotenv
from openai import APIError, APITimeoutError, OpenAI

from llm_fastapi_lab.models import CandidateExtraction
from llm_fastapi_lab.monitoring import LLMCallLog, estimate_cost, record_call


# Load environment variables from the local .env file.
load_dotenv()

# Create the OpenAI client with a 30-second request timeout.
client = OpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    base_url=os.getenv("AZURE_OPENAI_ENDPOINT").replace("/responses", ""),
    timeout=30.0,
)


def test_llm_connection():
    # Read the Azure deployment name from the environment.
    deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")

    # Send a request using the Responses API.
    response = client.responses.create(
        model=deployment,
        instructions="You are a helpful assistant.",
        input="Reply with exactly: LLM connection successful.",
    )

    # Return the model's text response.
    return response.output_text


def _request_candidate_extraction(candidate_text: str):
    # Send the candidate text to the LLM and request structured output.
    return client.responses.parse(
        model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
        instructions=(
            "Extract the candidate's name, job role, and years of experience. "
            "Return only the requested structured information."
        ),
        input=candidate_text,
        text_format=CandidateExtraction,
    )


def _is_valid_candidate(candidate: CandidateExtraction) -> bool:
    # Reject responses with missing required text fields.
    if not candidate.name.strip() or not candidate.role.strip():
        return False

    # Reject impossible experience values.
    if candidate.experience_years < 0:
        return False

    # Accept the candidate when all basic checks pass.
    return True


def _record_failed_call(
    attempts: int,
    latency_seconds: float,
    input_tokens: int = 0,
    output_tokens: int = 0,
) -> None:
    # Calculate the estimated cost for the failed request.
    estimated_cost = estimate_cost(
        input_tokens,
        output_tokens,
        input_price_per_million=0.25,
        output_price_per_million=2.00,
    )

    # Record the failed LLM call and its monitoring information.
    record_call(
        LLMCallLog(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
            latency_seconds=latency_seconds,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            estimated_cost_usd=estimated_cost,
            attempts=attempts,
            success=False,
        )
    )


def extract_candidate(candidate_text: str) -> dict:
    # Start the high-resolution timer before the LLM request.
    start_time = time.perf_counter()

    # Allow one initial attempt plus one retry.
    max_attempts = 2
    attempts = 0

    # Keep the latest response so its token usage can be recorded.
    response = None

    # Try the LLM request up to two times.
    while attempts < max_attempts:
        attempts += 1

        try:
            # Request structured candidate information from the LLM.
            response = _request_candidate_extraction(candidate_text)

            # Stop retrying when the request succeeds.
            break

        except (APITimeoutError, APIError):
            # Retry once when the LLM request times out or returns an API error.
            if attempts == max_attempts:
                # Calculate the total time spent on the failed attempts.
                latency_seconds = time.perf_counter() - start_time

                # Record the failed request because no usable response was received.
                _record_failed_call(
                    attempts=attempts,
                    latency_seconds=latency_seconds,
                )

                # Raise a controlled error after the final attempt.
                raise RuntimeError(
                    "LLM request failed after two attempts. Please try again later."
                )

    # Check whether the LLM returned a valid structured result.
    if response.output_parsed is None or not _is_valid_candidate(
        response.output_parsed
    ):
        # Retry once when the first response is malformed.
        if attempts < max_attempts:
            attempts += 1

            try:
                # Make the single allowed retry request.
                response = _request_candidate_extraction(candidate_text)

            except (APITimeoutError, APIError):
                # Calculate the total time spent across both attempts.
                latency_seconds = time.perf_counter() - start_time

                # Record the failed request.
                _record_failed_call(
                    attempts=attempts,
                    latency_seconds=latency_seconds,
                )

                # Fail safely if the retry encounters an LLM error.
                raise RuntimeError(
                    "LLM request failed during the retry. Please try again later."
                )

        # Check whether the retry also returned an invalid response.
        if response.output_parsed is None or not _is_valid_candidate(
            response.output_parsed
        ):
            # Calculate the total time spent across both attempts.
            latency_seconds = time.perf_counter() - start_time

            # Capture token usage when the API returned a response.
            input_tokens = response.usage.input_tokens
            output_tokens = response.usage.output_tokens

            # Record the malformed-response failure.
            _record_failed_call(
                attempts=attempts,
                latency_seconds=latency_seconds,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
            )

            # Fail safely when the final response is still invalid.
            raise RuntimeError(
                "LLM returned an invalid structured response after two attempts."
            )

    # Calculate how long the complete LLM operation took.
    latency_seconds = time.perf_counter() - start_time

    # Capture the input tokens used by the request.
    input_tokens = response.usage.input_tokens

    # Capture the output tokens generated by the model.
    output_tokens = response.usage.output_tokens

    # Calculate the estimated cost using gpt-5-mini pricing.
    estimated_cost = estimate_cost(
        input_tokens,
        output_tokens,
        input_price_per_million=0.25,
        output_price_per_million=2.00,
    )

    # Display monitoring information during development.
    print(f"LLM latency: {latency_seconds:.3f} seconds")
    print(f"Input tokens: {input_tokens}")
    print(f"Output tokens: {output_tokens}")
    print(f"Estimated cost: ${estimated_cost:.8f}")

    # Record the completed successful LLM operation.
    record_call(
        LLMCallLog(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
            latency_seconds=latency_seconds,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            estimated_cost_usd=estimated_cost,
            attempts=attempts,
            success=True,
        )
    )

    # Return the structured result and monitoring information.
    return {
        "candidate": response.output_parsed,
        "latency_seconds": latency_seconds,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "estimated_cost_usd": estimated_cost,
        "attempts": attempts,
        "success": True,
    }
