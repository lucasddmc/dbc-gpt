from pydantic import BaseModel
from typing import Optional, List

class SpecificationRequest(BaseModel):
    llm_model: str  # "chatgpt", "llama", or "claude"

class VerificationResult(BaseModel):
    status: int
    output: str

class VerificationRunResult(BaseModel):
    run: int
    time_taken: float
    iterations: int
    verified: bool
    annotated_contract: str
    status_messages: List[str]