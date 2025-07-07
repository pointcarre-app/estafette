"""Bucket management for OVH."""

from __future__ import annotations
from typing import List, Optional
import boto3
import botocore
from rich.console import Console
from rich.progress import Progress

from .config import OVHConfig
from .models import BucketInfo


class BucketManager:
    """Manages OVH bucket operations via boto3."""

    def __init__(self, config: OVHConfig, console: Optional[Console] = None) -> None:
        self.config = config
        self.console = console or Console()

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

    # ------------------------------------------------------------------
    # Public methods
    # ------------------------------------------------------------------

    def create_bucket(
        self,
        bucket_name: str,
        region: str = "EU-WEST-PAR",
        acl: str = "public-read",
    ) -> bool:
        """Create a bucket with the given ACL. Returns True if created."""
        bucket_name = self.config.validate_bucket_name(bucket_name)
        s3 = self._get_s3(region)
        try:
            s3.create_bucket(
                Bucket=bucket_name,
                ACL=acl,
                CreateBucketConfiguration={
                    "LocationConstraint": self.config.get_region_config(region).region_code
                },
            )
            self.console.log(f"[success]✅ Created bucket[/] [info]{bucket_name}[/] in {region}")
            return True
        except botocore.exceptions.ClientError as e:
            self.console.print(f"❌ Failed to create bucket: {e}")
            return False

    def delete_bucket(
        self,
        bucket_name: str,
        region: str = "EU-WEST-PAR",
        force: bool = False,
    ) -> bool:
        """Delete a bucket; if force, remove all objects first."""
        bucket_name = self.config.validate_bucket_name(bucket_name)
        s3 = self._get_s3(region)
        try:
            if force:
                paginator = s3.get_paginator("list_object_versions")
                with Progress(console=self.console) as progress:
                    task = progress.add_task("Deleting objects", total=None)
                    for page in paginator.paginate(Bucket=bucket_name):
                        objs = [
                            {"Key": v["Key"], "VersionId": v.get("VersionId")}
                            for v in page.get("Versions", []) + page.get("DeleteMarkers", [])
                        ]
                        if objs:
                            s3.delete_objects(Bucket=bucket_name, Delete={"Objects": objs})
                            progress.update(task, advance=len(objs))
            s3.delete_bucket(Bucket=bucket_name)
            self.console.log(f"[warning]🗑️ Deleted bucket[/] [info]{bucket_name}[/]")
            return True
        except botocore.exceptions.ClientError as e:
            self.console.print(f"❌ Failed to delete bucket: {e}")
            return False

    def list_buckets(self, region: str = "EU-WEST-PAR") -> List[BucketInfo]:
        """List all buckets (no filtering by region, API returns all)."""
        s3 = self._get_s3(region)
        resp = s3.list_buckets()
        buckets: List[BucketInfo] = []
        for b in resp.get("Buckets", []):
            buckets.append(
                BucketInfo(name=b["Name"], region=region, creation_date=b.get("CreationDate"))
            )
        return buckets

    def bucket_exists(self, bucket_name: str, region: str = "EU-WEST-PAR") -> bool:
        bucket_name = self.config.validate_bucket_name(bucket_name)
        s3 = self._get_s3(region)
        try:
            s3.head_bucket(Bucket=bucket_name)
            return True
        except botocore.exceptions.ClientError:
            return False

    def get_bucket_info(
        self, bucket_name: str, region: str = "EU-WEST-PAR"
    ) -> Optional[BucketInfo]:
        if not self.bucket_exists(bucket_name, region):
            return None
        s3 = self._get_s3(region)
        creation = None
        try:
            resp = s3.list_buckets()
            for b in resp.get("Buckets", []):
                if b["Name"] == bucket_name:
                    creation = b.get("CreationDate")
                    break
        except botocore.exceptions.ClientError:
            pass
        return BucketInfo(name=bucket_name, region=region, creation_date=creation)
