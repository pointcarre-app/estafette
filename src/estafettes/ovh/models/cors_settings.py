from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field


class CORSSettings(BaseModel):
    """CORS configuration settings for rclone."""

    allowed_origins: List[str] = Field(
        default_factory=lambda: [
            "http://localhost:8000",
            "http://127.0.0.1:8000",
            "https://forge.pointcarre.app",
        ],
        description="Origins allowed to access bucket from browsers",
    )
    allowed_methods: List[str] = Field(
        default_factory=lambda: ["GET", "HEAD"],
        description="HTTP methods allowed for cross-origin requests",
    )
    allowed_headers: List[str] = Field(
        default_factory=lambda: ["*"], description="Headers allowed in cross-origin requests"
    )
    expose_headers: List[str] = Field(
        default_factory=lambda: ["ETag", "Content-Length", "Content-Type"],
        description="Headers exposed to browser scripts",
    )
    max_age: int = Field(
        default=3600, ge=0, description="Cache duration for preflight requests (seconds)"
    )
