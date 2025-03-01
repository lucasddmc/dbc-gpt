from fastapi import FastAPI
from .api import generate_specification, status
import uvicorn

app = FastAPI(
    title="LLM Specification Generator",
    description="An API for generating formal specifications for smart contracts using LLMs",
    version="1.0.0",
)

# Include API routers
app.include_router(generate_specification.router, prefix="/api/v1")
app.include_router(status.router, prefix="/api/v1")

# Run the application (if running directly)
if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)