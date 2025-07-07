"""OVH configuration settings - dynamic operations only."""

from __future__ import annotations
from typing import Optional, List
from pathlib import Path
import configparser
import os
import typer
from rich.console import Console
from rich.theme import Theme

from .models.ovh_credentials import OVHCredentials
from .models.ovh_regions import OVHRegions
from .models.ovh_region_config import OVHRegionConfig
from .models.ovh_environment import OVHEnvironment
from .models.rclone_config import RcloneConfig
from .models.cors_settings import CORSSettings


class OVHConfig:
    """OVH configuration manager - handles dynamic operations only."""

    def __init__(
        self,
        config_file: str = "rclone.conf",
        console: Optional[Console] = None,
    ) -> None:
        self.config_file = config_file
        theme = Theme(
            {
                "info": "cyan",
                "success": "green",
                "warning": "yellow",
                "error": "bold red",
            }
        )
        self.console = console or Console(theme=theme)
        self.regions = OVHRegions()
        self._cached_credentials: Optional[OVHCredentials] = None

    def get_region_config(self, region: str) -> OVHRegionConfig:
        """Get region configuration or raise error if region not supported."""
        try:
            return self.regions.get_region(region)
        except ValueError as e:
            raise typer.Exit(f"❌ {str(e)}")

    def validate_region(self, region: str) -> bool:
        """Validate if region is supported."""
        return region in self.regions.list_regions()

    def _get_config_paths(self) -> List[Path]:
        """Get list of possible rclone configuration file paths."""
        return [
            Path(self.config_file),  # Current directory
            Path.home() / ".config/rclone/rclone.conf",  # User config
            Path("~/.config/rclone/rclone.conf").expanduser(),  # User config alternative
            Path("/etc/rclone/rclone.conf"),  # System config
        ]

    def _find_config_file(self) -> Optional[Path]:
        """Find the first existing rclone configuration file."""
        for path in self._get_config_paths():
            if path.exists():
                return path
        return None

    def read_rclone_credentials(self) -> OVHCredentials:
        """Read credentials from rclone configuration file."""
        config_path = self._find_config_file()

        if not config_path:
            searched_paths = [str(p) for p in self._get_config_paths()]
            raise typer.Exit(f"❌ rclone.conf not found. Searched: {searched_paths}")

        self.console.print(f"📖 Reading credentials from: [blue]{config_path}[/blue]")

        config = configparser.ConfigParser()
        config.read(config_path)

        # Try different section names
        section_names = ["StorageS3", "ovh", "s3"]
        storage_config = None

        for section_name in section_names:
            if section_name in config:
                storage_config = config[section_name]
                break

        if not storage_config:
            available_sections = list(config.sections())
            raise typer.Exit(
                f"❌ No valid storage section found in rclone.conf. "
                f"Available sections: {available_sections}. "
                f"Expected one of: {section_names}"
            )

        access_key = storage_config.get("access_key_id")
        secret_key = storage_config.get("secret_access_key")

        if not access_key or not secret_key:
            raise typer.Exit("❌ Missing credentials in rclone.conf")

        try:
            credentials = OVHCredentials(access_key=access_key, secret_key=secret_key)
            self._cached_credentials = credentials
            return credentials
        except Exception as e:
            raise typer.Exit(f"❌ Invalid credentials format: {e}")

    def get_credentials_from_env(self) -> Optional[OVHCredentials]:
        """Get credentials from environment variables."""
        access_key = os.getenv("AWS_ACCESS_KEY_ID") or os.getenv("OVH_ACCESS_KEY_ID")
        secret_key = os.getenv("AWS_SECRET_ACCESS_KEY") or os.getenv("OVH_SECRET_ACCESS_KEY")

        if access_key and secret_key:
            try:
                return OVHCredentials(access_key=access_key, secret_key=secret_key)
            except Exception as e:
                self.console.print(f"⚠️ Invalid environment credentials: {e}")
                return None
        return None

    def get_credentials(
        self,
        access_key: Optional[str] = None,
        secret_key: Optional[str] = None,
    ) -> OVHCredentials:
        """Get credentials from multiple sources with fallback chain."""
        # 1. Use provided credentials
        if access_key and secret_key:
            try:
                return OVHCredentials(access_key=access_key, secret_key=secret_key)
            except Exception as e:
                raise typer.Exit(f"❌ Invalid provided credentials: {e}")

        # 2. Try cached credentials
        if self._cached_credentials:
            return self._cached_credentials

        # 3. Try environment variables
        env_credentials = self.get_credentials_from_env()
        if env_credentials:
            self._cached_credentials = env_credentials
            return env_credentials

        # 4. Try rclone configuration file
        try:
            return self.read_rclone_credentials()
        except typer.Exit:
            # If all methods fail, raise error
            raise typer.Exit(
                "❌ No valid credentials found. Please provide credentials via:\n"
                "  1. Function parameters\n"
                "  2. Environment variables (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)\n"
                "  3. rclone.conf file\n"
            )

    def create_environment(
        self,
        region: str = "EU-WEST-PAR",
        credentials: Optional[OVHCredentials] = None,
        additional_env: Optional[dict] = None,
    ) -> OVHEnvironment:
        """Create OVH environment with AWS variables."""
        if credentials is None:
            credentials = self.get_credentials()

        region_config = self.get_region_config(region)

        return OVHEnvironment(
            credentials=credentials,
            region_config=region_config,
            additional_env=additional_env or {},
        )

    def create_rclone_config(
        self,
        bucket_name: str,
        region: str = "EU-WEST-PAR",
        credentials: Optional[OVHCredentials] = None,
        cors_settings: Optional[CORSSettings] = None,
        acl: str = "public-read",
        bucket_acl: str = "public-read",
    ) -> RcloneConfig:
        """Create rclone configuration model."""
        if credentials is None:
            credentials = self.get_credentials()

        region_config = self.get_region_config(region)

        if cors_settings is None:
            cors_settings = CORSSettings()

        return RcloneConfig(
            bucket_name=bucket_name,
            credentials=credentials,
            region_config=region_config,
            cors_settings=cors_settings,
            acl=acl,
            bucket_acl=bucket_acl,
        )

    def log_credentials_info(self, credentials: Optional[OVHCredentials] = None) -> None:
        """Log credential information (masked for security)."""
        if credentials is None:
            credentials = self.get_credentials()

        self.console.print(f"🔑 Access Key: [yellow]{credentials.mask_access_key()}[/yellow]")
        self.console.print(f"🔑 Secret Key: [yellow]{credentials.mask_secret_key()}[/yellow]")

    # ---------------------------------------------------------------------
    # Additional helpers for dynamic configuration management
    # ---------------------------------------------------------------------

    @staticmethod
    def validate_bucket_name(bucket_name: str) -> str:
        """Return a validated bucket name or raise typer.Exit on failure."""
        cleaned = bucket_name.strip()
        if not cleaned.replace("-", "").replace("_", "").isalnum():
            raise typer.Exit(
                "❌ Bucket name must be alphanumeric and can include dashes/underscores"
            )
        if len(cleaned) < 3 or len(cleaned) > 63:
            raise typer.Exit("❌ Bucket name length must be between 3 and 63 characters")
        return cleaned.lower()

    def write_rclone_config(
        self,
        bucket_name: str,
        output_path: Optional[Path | str] = None,
        region: str = "EU-WEST-PAR",
        overwrite: bool = False,
        **kwargs,
    ) -> Path:
        """Generate an rclone section for the bucket and write/append it to a file.

        Parameters
        ----------
        bucket_name: str
            Target bucket name (validated).
        output_path: Path | str | None
            File to write to. Defaults to ``self.config_file``.
        region: str
            OVH region key (must exist).
        overwrite: bool
            If True and the section already exists, it will be replaced. Otherwise an
            error is raised to avoid duplicating conflicting configs.
        kwargs: dict
            Forwarded to ``create_rclone_config`` (cors_settings, acl, etc.).
        """

        # Validate inputs first
        bucket_name = self.validate_bucket_name(bucket_name)
        self.validate_region(region)

        rclone_config = self.create_rclone_config(
            bucket_name=bucket_name,
            region=region,
            **kwargs,
        )

        section_header = f"[StorageS3-{bucket_name}]"

        target_file = Path(output_path or self.config_file)
        # Ensure parent directory exists if writing to custom path
        target_file.parent.mkdir(parents=True, exist_ok=True)

        # Read existing contents (if any) to check duplicates
        existing_text = ""
        if target_file.exists():
            existing_text = target_file.read_text()

        if section_header in existing_text:
            if not overwrite:
                raise typer.Exit(
                    f"❌ Section {section_header} already exists in {target_file}. "
                    "Use overwrite=True to replace it."
                )
            # Remove existing section (naïve but effective: split on header)
            parts = existing_text.split(section_header)
            # keep everything before the first occurrence; drop until next header
            if len(parts) > 1:
                # Reconstruct text without old section
                pre = parts[0]
                # Find where the old section ended (next '[')
                rest = section_header.join(parts[1:])
                if "[" in rest:
                    rest = rest[rest.index("[") :]
                else:
                    rest = ""
                existing_text = (pre + rest).rstrip() + "\n\n"

        # Append new section at the end
        new_text = existing_text + rclone_config.generate_config().strip() + "\n"
        target_file.write_text(new_text)

        self.console.print(
            f"✅ Rclone configuration for bucket '[green]{bucket_name}[/green]' "
            f"written to [blue]{target_file}[/blue] (overwrite={overwrite})."
        )

        return target_file
