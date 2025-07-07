"""OVH models package."""

from __future__ import annotations

from .cors_policy import CORSPolicy
from .cors_settings import CORSSettings
from .website import DeploymentResult
from .bucket import BucketInfo
from .ovh_region_config import OVHRegionConfig
from .ovh_credentials import OVHCredentials
from .ovh_environment import OVHEnvironment
from .rclone_config import RcloneConfig
from .ovh_regions import OVHRegions

__all__ = [
    # Core configuration models
    "OVHRegionConfig",
    "OVHCredentials",
    "OVHEnvironment",
    "RcloneConfig",
    "OVHRegions",
    # CORS models
    "CORSSettings",
    "CORSPolicy",
    # Operational models
    "BucketInfo",
    "DeploymentResult",
]
