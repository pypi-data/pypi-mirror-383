from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field
from datetime import datetime


class Pagination(BaseModel):
    """Represents pagination information."""
    page_number: Optional[int] = Field(alias="pageNumber", default=None)
    count: Optional[int] = Field(alias="count", default=None)
    total: Optional[int] = Field(alias="total", default=None)
    current_url: Optional[str] = Field(alias="currentUrl", default=None)
    next_url: Optional[str] = Field(alias="nextUrl", default=None)
    previous_url: Optional[str] = Field(alias="previousUrl", default=None)


class Meta(BaseModel):
    """Represents metadata for an API response."""
    pagination: Optional[Pagination] = Field(alias="pagination", default=None)
    status: Optional[int] = Field(alias="status", default=None)
    message: Optional[str] = Field(alias="message", default=None)
    error: Optional[str] = Field(alias="error", default=None)


class Error(BaseModel):
    """Represents an error response from the API."""
    code: Optional[int] = Field(alias="code", default=None)
    message: Optional[str] = Field(alias="message", default=None)


class APIResponse(BaseModel):
    """Generic API response structure with meta and results."""
    meta: Optional[Meta] = Field(alias="meta", default=None)
    results: List[Any] = Field(alias="results", default_factory=list) # Use Any for dynamic content
