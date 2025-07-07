from __future__ import annotations

from pydantic import BaseModel, Field, field_validator


class OVHRegionConfig(BaseModel):
    """Configuration for OVH regions with validation."""

    endpoint: str = Field(..., description="S3 endpoint URL")
    website_suffix: str = Field(..., description="Static website domain suffix")
    region_code: str = Field(..., description="AWS region code")
    description: str = Field(..., description="Human-readable region description")

    @field_validator("endpoint")
    @classmethod
    def validate_endpoint(cls, v: str) -> str:
        if not v.startswith("https://"):
            raise ValueError("Endpoint must start with https://")
        return v

    @field_validator("region_code")
    @classmethod
    def validate_region_code(cls, v: str) -> str:
        if not v.replace("-", "").replace("_", "").isalnum():
            raise ValueError("Region code must be alphanumeric with dashes/underscores")
        return v
