from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ParsedDocument(BaseModel):
    file_name: str
    markdown: str
    chunks: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class SearchHit(BaseModel):
    text: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    distance: float | None = None


class FillResult(BaseModel):
    status: str
    filled_cells: int
    output_path: str
