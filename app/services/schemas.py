from pydantic import BaseModel, Field
from typing import List

class LLMResponse(BaseModel):
    answer: str = Field(..., description="Final answer to the user query")
    page_number: List[int] = Field(default_factory=list, description="Page numbers where answer is found")