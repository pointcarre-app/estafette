"""Website configuration management for OVH buckets."""

from __future__ import annotations

import boto3
import botocore
from rich.console import Console

from .config import OVHConfig


class WebsiteManager:
    """Manages static website configuration for OVH buckets."""

    def __init__(self, config: OVHConfig, console: Console | None = None) -> None:
        self.config = config
        self.console = console or Console()

    # ------------------------------------------------------------------
    # Public methods
    # ------------------------------------------------------------------

    def apply_website_configuration(
        self,
        bucket_name: str,
        region: str = "EU-WEST-PAR",
        index_document: str = "index.html",
        error_document: str = "error.html",
    ) -> bool:
        """Enable static website hosting on the bucket."""
        bucket_name = self.config.validate_bucket_name(bucket_name)
        s3 = self._get_s3(region)
        try:
            s3.put_bucket_website(
                Bucket=bucket_name,
                WebsiteConfiguration={
                    "IndexDocument": {"Suffix": index_document},
                    "ErrorDocument": {"Key": error_document},
                },
            )
            self.console.print(
                f"🌐 Static website enabled for [green]{bucket_name}[/green] (index={index_document})"
            )
            return True
        except botocore.exceptions.ClientError as e:
            self.console.print(f"❌ Failed to set website configuration: {e}")
            return False

    def set_bucket_public_read(self, bucket_name: str, region: str = "EU-WEST-PAR") -> bool:
        """Set bucket ACL to public-read."""
        bucket_name = self.config.validate_bucket_name(bucket_name)
        s3 = self._get_s3(region)
        try:
            s3.put_bucket_acl(Bucket=bucket_name, ACL="public-read")
            return True
        except botocore.exceptions.ClientError as e:
            self.console.print(f"❌ Failed to set bucket ACL: {e}")
            return False

    def set_objects_public_read(self, bucket_name: str, region: str = "EU-WEST-PAR") -> bool:
        """Iterate over objects and set ACL public-read."""
        bucket_name = self.config.validate_bucket_name(bucket_name)
        s3 = self._get_s3(region)
        paginator = s3.get_paginator("list_objects_v2")
        try:
            for page in paginator.paginate(Bucket=bucket_name):
                for obj in page.get("Contents", []):
                    s3.put_object_acl(Bucket=bucket_name, Key=obj["Key"], ACL="public-read")
            return True
        except botocore.exceptions.ClientError as e:
            self.console.print(f"❌ Failed to set object ACLs: {e}")
            return False

    def create_default_website_files(self, bucket_name: str) -> bool:  # placeholder
        self.console.print("⚠️ create_default_website_files not yet implemented")
        return True

    def test_website(self, bucket_name: str, region: str, path: str = "") -> bool:  # placeholder
        return True

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

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

    def _copy_template_file(
        self, template_path: str, bucket_name: str, remote_filename: str
    ) -> bool:
        pass
