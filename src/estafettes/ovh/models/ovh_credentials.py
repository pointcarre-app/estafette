from __future__ import annotations

from pydantic import BaseModel, Field, field_validator


class OVHCredentials(BaseModel):
    """OVH S3 credentials with validation."""

    access_key: str = Field(..., min_length=20, description="OVH S3 access key")
    secret_key: str = Field(..., min_length=20, description="OVH S3 secret key")

    @field_validator("access_key", "secret_key")
    @classmethod
    def validate_credentials(cls, v: str) -> str:
        if not v.replace("_", "").replace("-", "").isalnum():
            raise ValueError("Credentials must be alphanumeric with dashes/underscores")
        return v

    def mask_access_key(self, visible_chars: int = 4) -> str:
        """Return masked access key for logging."""
        if len(self.access_key) <= visible_chars:
            return "*" * 8
        return f"{self.access_key[:visible_chars]}{'*' * (len(self.access_key) - visible_chars)}"

    def mask_secret_key(self, visible_chars: int = 4) -> str:
        """Return masked secret key for logging."""
        if len(self.secret_key) <= visible_chars:
            return "*" * 8
        return f"{self.secret_key[:visible_chars]}{'*' * (len(self.secret_key) - visible_chars)}"
