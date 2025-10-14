"""File model definitions."""

from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field


class Author(BaseModel):
    """Author information model."""
    id: UUID
    name: str


class File(BaseModel):
    """File or directory model."""

    # New API fields (made optional for flexibility)
    name: Optional[str] = None
    path: Optional[str] = None
    type: Optional[str] = None  # 'file' or 'folder'
    size: int = 0
    last_modified: Optional[datetime] = Field(alias="lastModified", default=None)
    etag: Optional[str] = None
    content_type: Optional[str] = Field(alias="contentType", default=None)
    storage_class: Optional[str] = Field(alias="storageClass", default=None)
    version_id: Optional[str] = Field(alias="versionId", default=None)

    # Old API fields (for backward compatibility)
    object_name: Optional[str] = Field(alias="objectName", default=None)
    is_dir: Optional[bool] = Field(alias="isDir", default=None)
    url: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    object_key: Optional[str] = Field(alias="objectKey", default=None)
    logical_path: Optional[str] = Field(alias="logicalPath", default=None)
    created_at: Optional[datetime] = Field(alias="createdAt", default=None)
    author: Optional[Author] = None
    last_modified_by: Optional[Author] = Field(alias="lastModifiedBy", default=None)

    # For backward compatibility
    hash: Optional[str] = None

    @property
    def is_directory(self) -> bool:
        """Check if this is a directory."""
        # Check is_dir field first (most reliable)
        if self.is_dir is not None:
            return self.is_dir
        # Then check type field
        elif self.type:
            return self.type == "folder"
        # Finally check path patterns
        if self.object_name and self.object_name.endswith('/'):
            return True
        if self.logical_path and self.logical_path.endswith('/'):
            return True
        if self.path and self.path.endswith('/'):
            return True
        return False

    def __init__(self, **data):
        """Initialize File with name extraction from objectName if needed."""
        super().__init__(**data)
        # Auto-set name from objectName if name is not provided
        if not self.name and self.object_name:
            # Extract filename from path-like objectName
            import os
            self.name = os.path.basename(self.object_name.rstrip('/'))
            if not self.name:  # If basename is empty (root path), use the folder name
                parts = [p for p in self.object_name.rstrip('/').split('/') if p]
                self.name = parts[-1] if parts else self.object_name

    @property
    def actual_path(self) -> str:
        """Get the actual path for API operations."""
        # For manually created ".." entries, always use path field (not name)
        if self.name == "..":
            # Use path field for navigation entries (contains parent path or special markers)
            return self.path or ""

        # For regular files, prefer logicalPath over path for new API
        if self.logical_path:
            return self.logical_path
        elif self.path:
            return self.path
        elif self.object_name:
            return self.object_name
        else:
            return self.name or ""

    class Config:
        populate_by_name = True


class FileDownloadInfo(BaseModel):
    """File download information model."""

    path: str
    name: str
    size: int
    type: str
    presigned_url: str = Field(alias="presignedUrl")

    class Config:
        populate_by_name = True