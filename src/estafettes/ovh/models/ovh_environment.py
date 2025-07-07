from __future__ import annotations

import os
from typing import Dict

from pydantic import BaseModel, Field

from .ovh_credentials import OVHCredentials
from .ovh_region_config import OVHRegionConfig


class OVHEnvironment(BaseModel):
    """AWS environment variables setup for OVH."""

    credentials: OVHCredentials
    region_config: OVHRegionConfig
    additional_env: Dict[str, str] = Field(default_factory=dict)

    def to_env_dict(self) -> Dict[str, str]:
        """Generate environment variables dictionary for subprocess calls."""
        env = os.environ.copy()
        env.update(
            {
                "AWS_ACCESS_KEY_ID": self.credentials.access_key,
                "AWS_SECRET_ACCESS_KEY": self.credentials.secret_key,
                "AWS_DEFAULT_REGION": self.region_config.region_code,
                **self.additional_env,
            }
        )
        return env
