"""OVH package for estafette."""

from __future__ import annotations

from .config import OVHConfig
from .ovh_estafette import OVHEstafette
from .cors_manager import CORSManager
from .website_manager import WebsiteManager
from .bucket_manager import BucketManager
from .file_manager import FileManager
from .url_generator import URLGenerator
from .testing import DeploymentTester
from .models import (
    # Core configuration models
    OVHRegionConfig,
    OVHCredentials,
    OVHEnvironment,
    RcloneConfig,
    OVHRegions,
    # CORS models (all in cors.py)
    CORSSettings,
    CORSPolicy,
    # Operational models
    BucketInfo,
    DeploymentResult,
)

__all__ = [
    # Main classes
    "OVHConfig",
    "OVHEstafette",
    # Manager classes
    "CORSManager",
    "WebsiteManager",
    "BucketManager",
    "FileManager",
    "URLGenerator",
    "DeploymentTester",
    # Core configuration models
    "OVHRegionConfig",
    "OVHCredentials",
    "OVHEnvironment",
    "RcloneConfig",
    "OVHRegions",
    # CORS models (all in cors.py)
    "CORSSettings",
    "CORSPolicy",
    # Operational models
    "BucketInfo",
    "DeploymentResult",
]
