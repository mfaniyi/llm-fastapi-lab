from dataclasses import dataclass


@dataclass
class LLMCallLog:
    model: str
    latency_seconds: float
    input_tokens: int
    output_tokens: int
    estimated_cost_usd: float
    attempts: int
    success: bool


def estimate_cost(
    input_tokens: int,
    output_tokens: int,
    input_price_per_million: float,
    output_price_per_million: float,
) -> float:
    # Calculate the input-token cost.
    input_cost = (input_tokens / 1_000_000) * input_price_per_million

    # Calculate the output-token cost.
    output_cost = (output_tokens / 1_000_000) * output_price_per_million

    # Return the estimated total cost in USD.
    return input_cost + output_cost


# Store LLM call logs while the application is running.
call_logs: list[LLMCallLog] = []


def record_call(log: LLMCallLog) -> None:
    # Add the latest LLM call to the running log.
    call_logs.append(log)


def get_running_cost() -> float:
    # Sum the estimated cost of all recorded LLM calls.
    return sum(log.estimated_cost_usd for log in call_logs)