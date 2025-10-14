"""API response model definitions."""

from typing import Any, Optional

from pydantic import BaseModel


class ApiResponse(BaseModel):
    """Generic API response model."""

    success: bool
    message: Optional[str] = None
    data: Optional[Any] = None

    class Config:
        populate_by_name = True