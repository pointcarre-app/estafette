"""Website deployment result models."""

from __future__ import annotations
from typing import Optional, List
from pydantic import BaseModel


class DeploymentResult(BaseModel):
    """Deployment operation result."""

    success: bool
    bucket_name: str
    region: str
    files_uploaded: List[str]
    website_url: Optional[str] = None
    direct_urls: List[str]
    errors: List[str]
