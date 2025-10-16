from datetime import datetime

from pydantic import BaseModel, Field


class SummaryRead(BaseModel):
    id: int = Field(..., description="Summary ID")
    note_id: int = Field(..., description="Related note ID")
    summary_text: str = Field(..., description="Summary text")
    created_at: datetime = Field(..., description="Created timestamp")

    class Config:
        from_attributes = True
