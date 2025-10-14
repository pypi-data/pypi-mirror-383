"""Pydantic models for Stack Overflow MCP server - Request validation only."""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class SortOrder(str, Enum):
    """Sort order enumeration."""

    ASC = "asc"
    DESC = "desc"


class QuestionSort(str, Enum):
    """Question sort options."""

    ACTIVITY = "activity"
    VOTES = "votes"
    CREATION = "creation"
    HOT = "hot"
    WEEK = "week"
    MONTH = "month"
    RELEVANCE = "relevance"


class AnswerSort(str, Enum):
    """Answer sort options."""

    ACTIVITY = "activity"
    VOTES = "votes"
    CREATION = "creation"


class BaseRequest(BaseModel):
    """Base request model with common pagination."""

    page: int = Field(default=1, ge=1, le=25, description="Page number (1-25)")
    page_size: int = Field(
        default=30, ge=1, le=100, description="Number of items per page (1-100)"
    )
    order: SortOrder = Field(default=SortOrder.DESC, description="Sort order")


class QuestionSearchRequest(BaseRequest):
    """Request model for searching questions."""

    q: Optional[str] = Field(default=None, description="Free-form text search")
    tagged: Optional[str] = Field(
        default=None, description="Semi-colon delimited list of tags"
    )
    intitle: Optional[str] = Field(
        default=None, description="Search in question titles"
    )
    nottagged: Optional[str] = Field(default=None, description="Exclude these tags")
    body: Optional[str] = Field(default=None, description="Text in question body")
    accepted: Optional[bool] = Field(default=None, description="Has accepted answer")
    closed: Optional[bool] = Field(default=None, description="Question is closed")
    answers: Optional[int] = Field(
        default=None, ge=0, description="Minimum number of answers"
    )
    views: Optional[int] = Field(default=None, ge=0, description="Minimum view count")
    sort: QuestionSort = Field(
        default=QuestionSort.ACTIVITY, description="Sort criteria"
    )


class QuestionAnswersFetchRequest(BaseModel):
    """Request model for fetching question and answers."""

    question_id: int = Field(..., ge=1, description="Question ID")
    sort: AnswerSort = Field(
        default=AnswerSort.VOTES, description="Answer sort criteria"
    )
    order: SortOrder = Field(default=SortOrder.DESC, description="Sort order")
    page_size: int = Field(
        default=30,
        ge=1,
        le=100,
        description="Maximum number of answers to return (1-100)",
    )


class QuestionsByTagRequest(BaseRequest):
    """Request model for getting questions by tag."""

    tag: str = Field(..., min_length=1, description="Tag name")
    sort: QuestionSort = Field(
        default=QuestionSort.ACTIVITY, description="Sort criteria"
    )
