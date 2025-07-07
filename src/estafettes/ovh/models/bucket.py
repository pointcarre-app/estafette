"""Bucket configuration models."""

from __future__ import annotations
from typing import Optional
from pydantic import BaseModel
from datetime import datetime


class BucketInfo(BaseModel):
    """Bucket information."""

    name: str
    region: str
    creation_date: Optional[datetime] = None
    website_enabled: bool = False
    cors_enabled: bool = False
