"""
Deployment package for OVH Object Storage using pca-estafette.

This package provides a complete deployment solution with:
- Environment-specific configurations
- Custom CORS policies
- Multi-bucket deployment strategies
- CORS testing and validation
"""

from .environments import DeploymentManager
from .cors_configs import CORSConfigurations

__all__ = ["DeploymentManager", "CORSConfigurations"]
