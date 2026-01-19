"""Data models for Interview Agent."""

from datetime import datetime
from typing import List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field


class Question(BaseModel):
    """Interview question model."""

    id: str = Field(default_factory=lambda: str(uuid4()), description="Unique ID")
    question: str = Field(..., description="Question text")
    answer: Optional[str] = Field(default=None, description="Answer text")
    has_original_answer: bool = Field(
        default=False, description="Whether answer was in original text"
    )
    tags: List[str] = Field(default_factory=list, description="Question tags")


class InterviewExperience(BaseModel):
    """Interview experience model."""

    id: str = Field(default_factory=lambda: str(uuid4()), description="Unique ID")
    created_at: datetime = Field(
        default_factory=datetime.now, description="Creation timestamp"
    )
    source_type: str = Field(..., description="Source type: text|image|audio")

    # Company Information
    company_name: Optional[str] = Field(default=None, description="Company name")
    company_scale: Optional[str] = Field(
        default=None, description="Company scale: 大厂|中厂|小厂|初创"
    )
    position: Optional[str] = Field(default=None, description="Position title")
    interview_stage: Optional[str] = Field(
        default=None, description="Interview stage: 一面|二面|终面"
    )
    interview_experience: Optional[str] = Field(
        default=None, description="Interview experience description"
    )

    # Content
    questions: List[Question] = Field(default_factory=list, description="Questions list")
    tags: List[str] = Field(default_factory=list, description="Overall tags")
    raw_content: str = Field(..., description="Raw input content")

    class Config:
        """Pydantic config."""

        json_encoders = {datetime: lambda v: v.isoformat()}


class ProcessingResult(BaseModel):
    """Processing result model."""

    success: bool = Field(..., description="Whether processing succeeded")
    experience: Optional[InterviewExperience] = Field(
        default=None, description="Processed interview experience"
    )
    output_files: List[str] = Field(default_factory=list, description="Exported file paths")
    error: Optional[str] = Field(default=None, description="Error message if failed")
    processing_time: float = Field(..., description="Processing time in seconds")
