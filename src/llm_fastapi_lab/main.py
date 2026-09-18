from fastapi import FastAPI

# Create the FastAPI application.
app = FastAPI(title="LLM FastAPI Lab")


@app.get("/")
def health_check():
    # Return a simple response to confirm the API is running.
    return {"status": "ok"}