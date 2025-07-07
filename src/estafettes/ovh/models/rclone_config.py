from __future__ import annotations

from pydantic import BaseModel, Field, field_validator

from .ovh_credentials import OVHCredentials
from .ovh_region_config import OVHRegionConfig
from .cors_settings import CORSSettings


class RcloneConfig(BaseModel):
    """Rclone configuration generation."""

    bucket_name: str = Field(..., description="S3 bucket name")
    credentials: OVHCredentials
    region_config: OVHRegionConfig
    cors_settings: CORSSettings = Field(default_factory=CORSSettings)
    acl: str = Field(default="public-read", description="Default object ACL")
    bucket_acl: str = Field(default="public-read", description="Default bucket ACL")

    @field_validator("bucket_name")
    @classmethod
    def validate_bucket_name(cls, v: str) -> str:
        if not v.replace("-", "").replace("_", "").isalnum():
            raise ValueError("Bucket name must be alphanumeric with dashes/underscores")
        return v.lower()

    def generate_config(self) -> str:
        """Generate rclone configuration string."""
        return f"""[StorageS3-{self.bucket_name}]
type = s3
provider = Other
env_auth = true
access_key_id = {self.credentials.access_key}
secret_access_key = {self.credentials.secret_key}
acl = {self.acl}
bucket_acl = {self.bucket_acl}
region = {self.region_config.region_code}
location_constraint = {self.region_config.region_code}
endpoint = {self.region_config.endpoint}
cors_allowed_origins = {self.cors_settings.allowed_origins}
cors_allowed_methods = {self.cors_settings.allowed_methods}
cors_allowed_headers = {self.cors_settings.allowed_headers}
cors_expose_headers = {self.cors_settings.expose_headers}
cors_max_age = {self.cors_settings.max_age}
"""
