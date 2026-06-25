from __future__ import annotations

from pydantic import BaseModel, Field


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=60)
    description: str = Field(default="")
    priority: str | None = Field(default=None, pattern="^[LMH]$")
    due_date: str | None = Field(default=None)
    tags: list[str] = Field(default_factory=list)
    project: str | None = Field(default=None)


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=60)
    description: str | None = Field(default=None)
    priority: str | None = Field(default=None, pattern="^[LMH]$")
    due_date: str | None = Field(default=None)
    tags: list[str] | None = Field(default=None)
    project: str | None = Field(default=None)


class TaskResponse(BaseModel):
    id: int
    title: str
    description: str = ""
    done: bool = False
    created_at: str = ""
    priority: str = ""
    due_date: str | None = None
    tags: list[str] = Field(default_factory=list)
    project: str | None = None


class ImportPayload(BaseModel):
    """Raw JSON list of task dicts — validated at use-case level."""

    model_config = {"arbitrary_types_allowed": True}


class ClearResponse(BaseModel):
    deleted: int


class ImportResponse(BaseModel):
    inserted: int
    updated: int
