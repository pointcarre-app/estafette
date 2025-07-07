from __future__ import annotations

from typing import List, Dict, Any

from pydantic import BaseModel

from .cors_settings import CORSSettings


class CORSPolicy(BaseModel):
    """CORS policy configuration for AWS S3 format."""

    allowed_origins: List[str]
    allowed_methods: List[str]
    allowed_headers: List[str]
    expose_headers: List[str]
    max_age_seconds: int

    def to_aws_format(self) -> Dict[str, Any]:
        """Convert to AWS S3 CORS configuration format."""
        return {
            "CORSRules": [
                {
                    "AllowedOrigins": self.allowed_origins,
                    "AllowedMethods": self.allowed_methods,
                    "AllowedHeaders": self.allowed_headers,
                    "ExposeHeaders": self.expose_headers,
                    "MaxAgeSeconds": self.max_age_seconds,
                }
            ]
        }

    @classmethod
    def from_cors_settings(cls, settings: CORSSettings) -> "CORSPolicy":
        """Create CORSPolicy from CORSSettings."""
        return cls(
            allowed_origins=settings.allowed_origins,
            allowed_methods=settings.allowed_methods,
            allowed_headers=settings.allowed_headers,
            expose_headers=settings.expose_headers,
            max_age_seconds=settings.max_age,
        )
