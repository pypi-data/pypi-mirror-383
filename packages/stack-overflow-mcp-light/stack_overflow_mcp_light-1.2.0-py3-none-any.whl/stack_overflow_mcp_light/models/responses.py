"""Pydantic models for Stack Overflow MCP server - Response validation only."""

from typing import Optional

from pydantic import BaseModel, Field


class QuestionItem(BaseModel):
    """Model for a question item."""

    question_id: Optional[int] = Field(default=None, description="Question ID")
    is_answered: Optional[bool] = Field(
        default=None, description="Whether the question has answers"
    )
    score: Optional[int] = Field(default=None, description="Question score")
    link: Optional[str] = Field(default=None, description="Link to the question")
    title: Optional[str] = Field(default=None, description="Question title")
    answers: Optional[list["AnswerItem"]] = Field(
        default=None, description="List of answers for the question"
    )


class AnswerItem(BaseModel):
    """Model for an answer item."""

    answer_id: Optional[int] = Field(default=None, description="Answer ID")
    is_accepted: Optional[bool] = Field(
        None, description="Whether the answer is accepted"
    )
    score: Optional[int] = Field(default=None, description="Answer score")
    body: Optional[str] = Field(default=None, description="Answer body content")
