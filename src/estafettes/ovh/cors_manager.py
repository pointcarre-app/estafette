"""CORS management for OVH buckets."""

from __future__ import annotations
from typing import List, Optional

import boto3
import botocore
import requests
from rich.console import Console

from .config import OVHConfig
from .models import CORSPolicy, CORSSettings


class CORSManager:
    """Manages CORS configuration for OVH buckets."""

    def __init__(self, config: OVHConfig, console: Optional[Console] = None) -> None:
        self.config = config
        self.console = console or Console()

    # ------------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------------

    def create_cors_policy(
        self,
        bucket_name: Optional[str] = None,
        region: str = "EU-WEST-PAR",
        additional_origins: Optional[List[str]] = None,
    ) -> CORSPolicy:
        """Generate a CORSPolicy for a bucket.

        If *bucket_name* is provided, automatically add its website & direct
        endpoints to the allowed origins list.
        """
        origins = self._get_default_origins()

        if additional_origins:
            origins.extend(additional_origins)

        if bucket_name:
            origins = self._add_bucket_origins(origins, bucket_name, region)

        # ensure uniqueness
        origins = sorted(set(origins))

        settings = CORSSettings(allowed_origins=origins)
        return CORSPolicy.from_cors_settings(settings)

    def apply_cors_policy(
        self,
        bucket_name: str,
        region: str = "EU-WEST-PAR",
        cors_policy: Optional[CORSPolicy] = None,
    ) -> bool:
        """Apply the given CORS policy to a bucket via boto3."""
        bucket_name = self.config.validate_bucket_name(bucket_name)
        if cors_policy is None:
            cors_policy = self.create_cors_policy(bucket_name, region)

        s3 = self._get_s3(region)
        try:
            s3.put_bucket_cors(Bucket=bucket_name, CORSConfiguration=cors_policy.to_aws_format())
            self.console.print(
                f"✅ Applied CORS to [green]{bucket_name}[/green] (origins: {cors_policy.allowed_origins})"
            )
            return True
        except botocore.exceptions.ClientError as e:
            self.console.print(f"❌ Failed to apply CORS: {e}")
            return False

    def test_cors(
        self,
        bucket_name: str,
        region: str,
        origin: str,
        file_path: str = "",
    ) -> bool:
        """Make an OPTIONS request to test CORS headers for a given origin."""
        bucket_name = self.config.validate_bucket_name(bucket_name)
        url = f"https://{bucket_name}.{self.config.get_region_config(region).endpoint.replace('https://', '')}/{file_path}"
        headers = {
            "Origin": origin,
            "Access-Control-Request-Method": "GET",
        }
        try:
            resp = requests.options(url, headers=headers, timeout=10)
            allowed = resp.headers.get("Access-Control-Allow-Origin")
            success = allowed == origin or allowed == "*"
            self.console.print(
                f"CORS test to {url} from origin '{origin}': {'✅' if success else '❌'} (header={allowed})"
            )
            return success
        except requests.exceptions.RequestException as e:
            self.console.print(f"❌ CORS test request failed: {e}")
            return False

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get_default_origins(self) -> List[str]:
        return [
            "http://localhost:8000",
            "http://127.0.0.1:8000",
        ]

    def _add_bucket_origins(self, origins: List[str], bucket_name: str, region: str) -> List[str]:
        region_cfg = self.config.get_region_config(region)
        direct = f"https://{bucket_name}.{region_cfg.endpoint.replace('https://', '')}"
        website = f"https://{bucket_name}.{region_cfg.website_suffix}"
        origins.extend([direct, website])
        return origins

    def _get_s3(self, region: str):
        env = self.config.create_environment(region=region).to_env_dict()
        session = boto3.session.Session()
        return session.client(
            "s3",
            endpoint_url=self.config.get_region_config(region).endpoint,
            region_name=self.config.get_region_config(region).region_code,
            aws_access_key_id=env["AWS_ACCESS_KEY_ID"],
            aws_secret_access_key=env["AWS_SECRET_ACCESS_KEY"],
        )
