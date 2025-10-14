"""Repository model definitions."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class Repository(BaseModel):
    """Repository model."""

    id: int
    name: str
    description: Optional[str] = None
    is_public: bool = Field(alias="isPublic")
    owner_id: str = Field(alias="ownerId")
    owner_name: str = Field(alias="ownerName")
    user_role: Optional[str] = Field(alias="userRole", default="VIEWER")  # OWNER, ADMIN, VIEWER, NONE
    created_at: datetime = Field(alias="createdAt")

    class Config:
        populate_by_name = True