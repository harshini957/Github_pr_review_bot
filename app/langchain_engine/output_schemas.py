from pydantic import BaseModel, Field
from typing import List, Literal

class ReviewComment(BaseModel):
    line: int = Field(description="Absolute line number in the file")
    severity: Literal["critical", "suggestion", "nitpick"]
    comment: str = Field(description="The review comment")

class ReviewOutput(BaseModel):
    comments: List[ReviewComment]
    summary: str = Field(description="One sentence summary of the code quality")