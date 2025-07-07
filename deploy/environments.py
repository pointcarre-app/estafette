"""
Environment-specific deployment management.

This module handles deployment configurations for different environments
(development, staging, production) with customizable settings for:
- Bucket naming strategies
- Region selection
- CORS policies
- Security settings
"""

import os
from typing import Dict, List, Optional
from pathlib import Path
from dataclasses import dataclass

from estafettes.ovh import OVHEstafette
from estafettes.ovh.models import DeploymentResult
from .cors_configs import CORSConfigurations


@dataclass
class EnvironmentConfig:
    """Configuration for a specific deployment environment."""

    bucket_prefix: str
    region: str
    cors_type: str
    domains: List[str]
    rclone_config: Optional[str] = None
    static_website: bool = True
    require_confirmation: bool = False
    dry_run_first: bool = False


class DeploymentManager:
    """
    Manages deployments across different environments with customizable configurations.

    Features:
    - Environment-specific bucket naming
    - Automatic CORS configuration
    - Multi-bucket deployment strategies
    - Built-in testing and validation
    - CI/CD friendly
    """

    def __init__(self, environment: str = "development", custom_config: Optional[Dict] = None):
        """
        Initialize deployment manager for a specific environment.

        Args:
            environment: Target environment (development, staging, production)
            custom_config: Optional custom configuration to override defaults
        """
        self.environment = environment
        self.config = self._get_environment_config(custom_config)
        self.estafette = OVHEstafette(
            region=self.config.region, config_file=self.config.rclone_config or "rclone.conf"
        )

    def _get_environment_config(self, custom_config: Optional[Dict] = None) -> EnvironmentConfig:
        """Get configuration for the specified environment."""

        # Default configurations
        default_configs = {
            "development": EnvironmentConfig(
                bucket_prefix=os.getenv("DEV_BUCKET_PREFIX", "myapp-dev"),
                region=os.getenv("DEV_REGION", "EU-WEST-PAR"),
                cors_type="development",
                domains=[
                    "http://localhost:3000",
                    "http://localhost:8080",
                    "http://127.0.0.1:3000",
                    "http://127.0.0.1:8080",
                ],
                static_website=True,
                require_confirmation=False,
                dry_run_first=False,
            ),
            "staging": EnvironmentConfig(
                bucket_prefix=os.getenv("STAGING_BUCKET_PREFIX", "myapp-staging"),
                region=os.getenv("STAGING_REGION", "EU-WEST-PAR"),
                cors_type="api_assets",
                domains=[os.getenv("STAGING_DOMAIN", "https://staging.myapp.com")],
                static_website=True,
                require_confirmation=True,
                dry_run_first=True,
            ),
            "production": EnvironmentConfig(
                bucket_prefix=os.getenv("PROD_BUCKET_PREFIX", "myapp-prod"),
                region=os.getenv("PROD_REGION", "GRA"),
                cors_type="api_assets",
                domains=[
                    os.getenv("PROD_DOMAIN", "https://myapp.com"),
                    os.getenv("PROD_WWW_DOMAIN", "https://www.myapp.com"),
                ],
                static_website=True,
                require_confirmation=True,
                dry_run_first=True,
            ),
        }

        if self.environment not in default_configs:
            raise ValueError(
                f"Unknown environment: {self.environment}. Available: {list(default_configs.keys())}"
            )

        config = default_configs[self.environment]

        # Apply custom overrides
        if custom_config:
            for key, value in custom_config.items():
                if hasattr(config, key):
                    setattr(config, key, value)

        return config

    def _get_cors_settings(self):
        """Get CORS settings based on environment configuration."""
        if self.config.cors_type == "development":
            return CORSConfigurations.development()
        elif self.config.cors_type == "api_assets":
            return CORSConfigurations.api_assets(self.config.domains)
        elif self.config.cors_type == "website_hosting":
            return CORSConfigurations.website_hosting()
        elif self.config.cors_type == "cdn_assets":
            return CORSConfigurations.cdn_assets()
        elif self.config.cors_type == "secure_api":
            return CORSConfigurations.secure_api(self.config.domains)
        elif self.config.cors_type == "mobile_app_assets":
            return CORSConfigurations.mobile_app_assets(self.config.domains)
        else:
            # Default to website hosting
            return CORSConfigurations.website_hosting()

    def _confirm_deployment(self, bucket_name: str, source_dir: str) -> bool:
        """Ask for user confirmation before deployment."""
        if not self.config.require_confirmation:
            return True

        print("\n🎯 Deployment Confirmation")
        print(f"Environment: {self.environment}")
        print(f"Bucket: {bucket_name}")
        print(f"Source: {source_dir}")
        print(f"Region: {self.config.region}")
        print(f"Domains: {', '.join(self.config.domains)}")

        response = input("\nProceed with deployment? (y/N): ").strip().lower()
        return response in ["y", "yes"]

    def deploy_frontend(
        self,
        source_dir: str = "./build",
        bucket_suffix: str = "frontend",
        dry_run_override: Optional[bool] = None,
    ) -> Optional[DeploymentResult]:
        """
        Deploy frontend assets (React, Vue, Angular, etc.).

        Args:
            source_dir: Directory containing built frontend assets
            bucket_suffix: Suffix to add to bucket name (e.g., "frontend")
            dry_run_override: Override the environment's dry_run_first setting

        Returns:
            DeploymentResult if deployment succeeds, None if cancelled
        """
        bucket_name = f"{self.config.bucket_prefix}-{bucket_suffix}"

        # Check if source directory exists
        if not Path(source_dir).exists():
            print(f"❌ Source directory not found: {source_dir}")
            return None

        # Confirmation check
        if not self._confirm_deployment(bucket_name, source_dir):
            print("❌ Deployment cancelled by user")
            return None

        # Determine dry run mode
        dry_run = dry_run_override if dry_run_override is not None else self.config.dry_run_first

        if dry_run:
            print(f"🔍 Running dry-run first for {self.environment} environment...")

        try:
            # Deploy with environment-specific settings
            result = self.estafette.deploy(
                bucket_name=bucket_name,
                source_dir=source_dir,
                static_website=self.config.static_website,
                dry_run=dry_run,
            )

            if dry_run:
                print(f"📋 Dry run completed for {bucket_name}")
                print(f"📁 Would upload {len(result.files_uploaded)} files")

                # Ask if user wants to proceed with actual deployment
                proceed = input("Proceed with actual deployment? (y/N): ").strip().lower()
                if proceed not in ["y", "yes"]:
                    print("❌ Actual deployment cancelled")
                    return result

                # Run actual deployment
                result = self.estafette.deploy(
                    bucket_name=bucket_name,
                    source_dir=source_dir,
                    static_website=self.config.static_website,
                    dry_run=False,
                )

            # Apply custom CORS settings
            cors_settings = self._get_cors_settings()
            self.estafette.cors_manager.apply_cors_policy(
                bucket_name=bucket_name, region=self.config.region, cors_settings=cors_settings
            )

            print("✅ Frontend deployed successfully!")
            print(f"🌐 Website URL: {result.website_url}")
            print(f"📁 Files uploaded: {len(result.files_uploaded)}")

            return result

        except Exception as e:
            print(f"❌ Frontend deployment failed: {e}")
            return None

    def deploy_assets(
        self,
        source_dir: str = "./assets",
        bucket_suffix: str = "assets",
        dry_run_override: Optional[bool] = None,
    ) -> Optional[DeploymentResult]:
        """
        Deploy static assets (images, fonts, etc.).

        Args:
            source_dir: Directory containing static assets
            bucket_suffix: Suffix to add to bucket name (e.g., "assets")
            dry_run_override: Override the environment's dry_run_first setting

        Returns:
            DeploymentResult if deployment succeeds, None if cancelled
        """
        bucket_name = f"{self.config.bucket_prefix}-{bucket_suffix}"

        # Check if source directory exists
        if not Path(source_dir).exists():
            print(f"❌ Assets directory not found: {source_dir}")
            return None

        # Confirmation check
        if not self._confirm_deployment(bucket_name, source_dir):
            print("❌ Assets deployment cancelled by user")
            return None

        # Determine dry run mode
        dry_run = dry_run_override if dry_run_override is not None else self.config.dry_run_first

        try:
            # Deploy assets (not as static website, just file hosting)
            result = self.estafette.deploy(
                bucket_name=bucket_name,
                source_dir=source_dir,
                static_website=False,  # Assets don't need website hosting
                dry_run=dry_run,
            )

            if dry_run:
                print(f"📋 Assets dry run completed for {bucket_name}")
                proceed = input("Proceed with actual assets deployment? (y/N): ").strip().lower()
                if proceed not in ["y", "yes"]:
                    return result

                result = self.estafette.deploy(
                    bucket_name=bucket_name,
                    source_dir=source_dir,
                    static_website=False,
                    dry_run=False,
                )

            # Apply CDN-optimized CORS for assets
            cdn_cors = CORSConfigurations.cdn_assets()
            self.estafette.cors_manager.apply_cors_policy(
                bucket_name=bucket_name, region=self.config.region, cors_settings=cdn_cors
            )

            print("✅ Assets deployed successfully!")
            print(f"📁 Files uploaded: {len(result.files_uploaded)}")

            return result

        except Exception as e:
            print(f"❌ Assets deployment failed: {e}")
            return None

    def deploy_docs(
        self, source_dir: str = "./docs/_build/html", bucket_suffix: str = "docs"
    ) -> Optional[DeploymentResult]:
        """
        Deploy documentation site (Sphinx, MkDocs, etc.).

        Args:
            source_dir: Directory containing built documentation
            bucket_suffix: Suffix to add to bucket name

        Returns:
            DeploymentResult if deployment succeeds, None if cancelled
        """
        bucket_name = f"{self.config.bucket_prefix}-{bucket_suffix}"

        if not Path(source_dir).exists():
            print(f"❌ Documentation directory not found: {source_dir}")
            return None

        if not self._confirm_deployment(bucket_name, source_dir):
            print("❌ Documentation deployment cancelled by user")
            return None

        try:
            result = self.estafette.deploy(
                bucket_name=bucket_name,
                source_dir=source_dir,
                static_website=True,  # Docs sites need website hosting
                dry_run=self.config.dry_run_first,
            )

            if self.config.dry_run_first:
                proceed = input("Proceed with actual docs deployment? (y/N): ").strip().lower()
                if proceed not in ["y", "yes"]:
                    return result

                result = self.estafette.deploy(
                    bucket_name=bucket_name,
                    source_dir=source_dir,
                    static_website=True,
                    dry_run=False,
                )

            # Use website hosting CORS for documentation
            docs_cors = CORSConfigurations.website_hosting()
            self.estafette.cors_manager.apply_cors_policy(
                bucket_name=bucket_name, region=self.config.region, cors_settings=docs_cors
            )

            print("✅ Documentation deployed successfully!")
            print(f"🌐 Docs URL: {result.website_url}")

            return result

        except Exception as e:
            print(f"❌ Documentation deployment failed: {e}")
            return None

    def test_cors(self, bucket_suffix: str = "frontend") -> bool:
        """
        Test CORS configuration for a deployed bucket.

        Args:
            bucket_suffix: Suffix of the bucket to test

        Returns:
            True if all CORS tests pass, False otherwise
        """
        bucket_name = f"{self.config.bucket_prefix}-{bucket_suffix}"

        print(f"\n🧪 Testing CORS for {bucket_name}")

        all_passed = True
        for domain in self.config.domains:
            try:
                cors_works = self.estafette.cors_manager.test_cors(
                    bucket_name=bucket_name,
                    region=self.config.region,
                    origin=domain,
                    file_path="index.html",
                )

                status = "✅ PASSED" if cors_works else "❌ BLOCKED"
                print(f"{status} CORS test for {domain}")

                if not cors_works:
                    all_passed = False

            except Exception as e:
                print(f"❌ CORS test failed for {domain}: {e}")
                all_passed = False

        return all_passed

    def list_buckets(self) -> List[str]:
        """List all buckets for this environment."""
        try:
            buckets = self.estafette.list_buckets()
            env_buckets = [
                bucket.name
                for bucket in buckets
                if bucket.name.startswith(self.config.bucket_prefix)
            ]

            print(f"\n📦 Buckets for {self.environment} environment:")
            for bucket in env_buckets:
                print(f"  • {bucket}")

            return env_buckets

        except Exception as e:
            print(f"❌ Failed to list buckets: {e}")
            return []

    def cleanup_environment(self, confirm: bool = True) -> bool:
        """
        Delete all buckets for this environment.

        ⚠️ DANGEROUS: This will delete all data!

        Args:
            confirm: Whether to ask for confirmation

        Returns:
            True if cleanup succeeds, False otherwise
        """
        env_buckets = self.list_buckets()

        if not env_buckets:
            print(f"✅ No buckets found for {self.environment} environment")
            return True

        if confirm:
            print(
                f"\n⚠️  WARNING: This will DELETE all {len(env_buckets)} buckets and their contents!"
            )
            print(f"Environment: {self.environment}")
            print("Buckets to delete:")
            for bucket in env_buckets:
                print(f"  • {bucket}")

            confirm_text = f"DELETE-{self.environment}"
            user_input = input(f"\nType '{confirm_text}' to confirm deletion: ").strip()

            if user_input != confirm_text:
                print("❌ Cleanup cancelled")
                return False

        print(f"🗑️  Deleting {len(env_buckets)} buckets...")

        success_count = 0
        for bucket in env_buckets:
            try:
                success = self.estafette.delete_bucket(bucket, force=True)
                if success:
                    print(f"✅ Deleted {bucket}")
                    success_count += 1
                else:
                    print(f"❌ Failed to delete {bucket}")
            except Exception as e:
                print(f"❌ Error deleting {bucket}: {e}")

        print(f"\n🎯 Cleanup complete: {success_count}/{len(env_buckets)} buckets deleted")
        return success_count == len(env_buckets)


class MultiEnvironmentManager:
    """Manage deployments across multiple environments."""

    def __init__(self, environments: List[str] = None):
        """
        Initialize multi-environment manager.

        Args:
            environments: List of environments to manage (default: all)
        """
        self.environments = environments or ["development", "staging", "production"]
        self.managers = {env: DeploymentManager(env) for env in self.environments}

    def deploy_to_all(
        self, source_dir: str = "./build", skip_production: bool = True
    ) -> Dict[str, Optional[DeploymentResult]]:
        """
        Deploy to multiple environments.

        Args:
            source_dir: Source directory to deploy
            skip_production: Whether to skip production deployment for safety

        Returns:
            Dict mapping environment names to deployment results
        """
        results = {}

        for env in self.environments:
            if env == "production" and skip_production:
                print("⏭️  Skipping production deployment (safety)")
                results[env] = None
                continue

            print(f"\n🚀 Deploying to {env}...")
            manager = self.managers[env]
            result = manager.deploy_frontend(source_dir)
            results[env] = result

            if result:
                print(f"✅ {env} deployment successful")
            else:
                print(f"❌ {env} deployment failed")
                break  # Stop on first failure

        return results

    def test_all_cors(self) -> Dict[str, bool]:
        """Test CORS for all environments."""
        results = {}

        for env in self.environments:
            print(f"\n🧪 Testing {env} CORS...")
            manager = self.managers[env]
            results[env] = manager.test_cors()

        return results
