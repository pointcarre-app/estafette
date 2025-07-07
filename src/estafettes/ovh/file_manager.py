"""File management and synchronization for OVH."""

from __future__ import annotations

import os
from pathlib import Path
from typing import List, Optional, Dict

import boto3
import botocore
import mimetypes
from rich.console import Console
from rich.progress import Progress, BarColumn, TimeRemainingColumn, TaskID

from .config import OVHConfig


class FileManager:
    """Manages file operations for OVH deployments (uploads, sync, deletes)."""

    EXCLUDE_PATTERNS = {".DS_Store", "__pycache__"}

    def __init__(self, config: OVHConfig, console: Optional[Console] = None) -> None:
        self.config = config
        self.console = console or Console()

    # ------------------------------------------------------------------
    # Public operations
    # ------------------------------------------------------------------

    def sync_files(
        self,
        source_path: str | Path,
        bucket_name: str,
        destination_prefix: str = "",
        region: str = "EU-WEST-PAR",
        static_website: bool = False,
        dry_run: bool = False,
    ) -> List[str]:
        """Upload all files under *source_path*.

        Returns the list of uploaded destination keys.
        """
        bucket_name = self.config.validate_bucket_name(bucket_name)
        source_path = self._prepare_source_path(Path(source_path), static_website)
        dest_prefix_clean = self._clean_file_path(destination_prefix)

        files_to_upload = self._collect_local_files(source_path)
        files_to_upload = self._filter_files(files_to_upload)

        if not files_to_upload:
            self.console.print("⚠️ No files to upload – nothing matched after filtering.")
            return []

        uploaded_keys: List[str] = []

        if dry_run:
            for f in files_to_upload:
                remote_key = self._build_remote_key(
                    f, source_path, dest_prefix_clean, static_website
                )
                self.console.print(f"[dry-run] Would upload: {f} → s3://{bucket_name}/{remote_key}")
            return []

        s3 = self._get_s3(region)

        progress = Progress(
            "{task.description}",
            BarColumn(),
            "{task.completed}/{task.total}",
            TimeRemainingColumn(),
        )
        with progress:
            task_id: TaskID = progress.add_task("Uploading", total=len(files_to_upload))
            for local_file in files_to_upload:
                remote_key = self._build_remote_key(
                    local_file, source_path, dest_prefix_clean, static_website
                )
                success = self.upload_file(local_file, bucket_name, remote_key, s3_client=s3)
                if success:
                    uploaded_keys.append(remote_key)
                progress.update(task_id, advance=1)

        return uploaded_keys

    def upload_file(
        self,
        local_path: str | Path,
        bucket_name: str,
        remote_key: str,
        s3_client=None,
    ) -> bool:
        """Upload a single file. Returns True if successful."""
        bucket_name = self.config.validate_bucket_name(bucket_name)
        local_path = Path(local_path)
        if not local_path.is_file():
            self.console.print(f"⚠️ Skipping non-file: {local_path}")
            return False

        s3 = s3_client or self._get_s3("EU-WEST-PAR")  # region not critical for endpoint URL
        try:
            content_type, _ = mimetypes.guess_type(str(local_path))
            extra = {"ACL": "public-read"}
            if content_type:
                extra["ContentType"] = content_type
            s3.upload_file(
                str(local_path),
                bucket_name,
                remote_key,
                ExtraArgs=extra,
            )
            return True
        except botocore.exceptions.ClientError as e:
            self.console.print(f"❌ Upload failed for {local_path}: {e}")
            return False

    def list_remote_files(
        self,
        bucket_name: str,
        prefix: str = "",
        recursive: bool = True,
        region: str = "EU-WEST-PAR",
    ) -> List[str]:
        bucket_name = self.config.validate_bucket_name(bucket_name)
        s3 = self._get_s3(region)
        paginator = s3.get_paginator("list_objects_v2")
        keys: List[str] = []
        for page in paginator.paginate(Bucket=bucket_name, Prefix=prefix):
            for obj in page.get("Contents", []):
                keys.append(obj["Key"])
        if not recursive:
            # Remove keys containing additional '/'
            keys = [k for k in keys if "/" not in k[len(prefix) :]]
        return keys

    def delete_remote_file(
        self,
        bucket_name: str,
        remote_key: str,
        region: str = "EU-WEST-PAR",
    ) -> bool:
        bucket_name = self.config.validate_bucket_name(bucket_name)
        s3 = self._get_s3(region)
        try:
            s3.delete_object(Bucket=bucket_name, Key=remote_key)
            return True
        except botocore.exceptions.ClientError as e:
            self.console.print(f"❌ Failed to delete {remote_key}: {e}")
            return False

    def get_file_metadata(
        self,
        bucket_name: str,
        remote_key: str,
        region: str = "EU-WEST-PAR",
    ) -> Optional[Dict]:
        bucket_name = self.config.validate_bucket_name(bucket_name)
        s3 = self._get_s3(region)
        try:
            resp = s3.head_object(Bucket=bucket_name, Key=remote_key)
            return resp
        except botocore.exceptions.ClientError:
            return None

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

    def _prepare_source_path(self, source_path: Path, static_website: bool) -> Path:
        """Return path resolved & validated."""
        if not source_path.exists():
            raise FileNotFoundError(f"Source path not found: {source_path}")
        return source_path.resolve()

    def _collect_local_files(self, root: Path) -> List[Path]:
        files: List[Path] = []
        if root.is_file():
            return [root]
        for dirpath, _, filenames in os.walk(root):
            for fname in filenames:
                files.append(Path(dirpath) / fname)
        return files

    def _build_remote_key(
        self,
        local_file: Path,
        source_root: Path,
        dest_prefix: str,
        static_website: bool,
    ) -> str:
        relative = local_file.relative_to(source_root)
        if static_website:
            relative = relative.name  # flatten to root
        key = "/".join([p for p in [dest_prefix, str(relative)] if p])
        return self._clean_file_path(key)

    def _filter_files(self, files: List[Path]) -> List[Path]:
        return [
            f for f in files if f.name not in self.EXCLUDE_PATTERNS and not f.name.startswith(".")
        ]

    def _clean_file_path(self, file_path: str) -> str:
        return file_path.lstrip("/|")
