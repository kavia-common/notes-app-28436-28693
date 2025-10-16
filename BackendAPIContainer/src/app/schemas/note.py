from datetime import datetime

from pydantic import BaseModel, Field


class NoteCreate(BaseModel):
    title: str = Field(..., description="Note title")
    content: str = Field(..., description="Note content")


class NoteUpdate(BaseModel):
    title: str = Field(..., description="Updated title")
    content: str = Field(..., description="Updated content")


class NoteRead(BaseModel):
    id: int = Field(..., description="Note ID")
    user_id: int = Field(..., description="Owner user ID")
    title: str = Field(..., description="Title")
    content: str = Field(..., description="Content")
    created_at: datetime = Field(..., description="Created timestamp")
    updated_at: datetime = Field(..., description="Updated timestamp")

    class Config:
        from_attributes = True
