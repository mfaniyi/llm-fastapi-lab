import os

# Provide safe placeholder values so the LLM module can be imported during tests.
os.environ.setdefault(
    "AZURE_OPENAI_ENDPOINT",
    "https://test.example.com/openai/v1/responses",
)
os.environ.setdefault(
    "AZURE_OPENAI_API_KEY",
    "test-api-key",
)
os.environ.setdefault(
    "AZURE_OPENAI_DEPLOYMENT",
    "test-deployment",
)