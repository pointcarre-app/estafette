#!/usr/bin/env python3
"""
Main deployment script for OVH Object Storage.

This script provides a command-line interface for deploying applications
to different environments with full CORS and bucket management.

Usage:
    python deploy/deploy_script.py --env development --source ./build
    python deploy/deploy_script.py --env staging --source ./dist --dry-run
    python deploy/deploy_script.py --env production --source ./build --confirm
    python deploy/deploy_script.py --test-cors --env staging
    python deploy/deploy_script.py --list-buckets --env production
"""

import sys
import os
import argparse
from pathlib import Path

# Add the project root to the path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from deploy.environments import DeploymentManager, MultiEnvironmentManager


def setup_argument_parser() -> argparse.ArgumentParser:
    """Set up command-line argument parsing."""
    parser = argparse.ArgumentParser(
        description="Deploy applications to OVH Object Storage",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Deploy to development (no confirmation needed)
  python deploy/deploy_script.py --env development --source ./build

  # Deploy to staging with dry-run first
  python deploy/deploy_script.py --env staging --source ./dist --dry-run

  # Deploy to production with manual confirmation
  python deploy/deploy_script.py --env production --source ./build --confirm

  # Deploy multiple assets types
  python deploy/deploy_script.py --env staging --frontend ./build --assets ./public/assets

  # Test CORS configuration
  python deploy/deploy_script.py --test-cors --env staging

  # List buckets for an environment
  python deploy/deploy_script.py --list-buckets --env production

  # Clean up an environment (DANGEROUS!)
  python deploy/deploy_script.py --cleanup --env development

Environment variables:
  DEPLOY_ENV         - Default environment (development, staging, production)
  DEV_BUCKET_PREFIX  - Bucket prefix for development
  STAGING_BUCKET_PREFIX - Bucket prefix for staging  
  PROD_BUCKET_PREFIX - Bucket prefix for production
  DEV_REGION         - OVH region for development
  STAGING_REGION     - OVH region for staging
  PROD_REGION        - OVH region for production
        """,
    )

    # Environment selection
    parser.add_argument(
        "--env",
        "--environment",
        choices=["development", "staging", "production"],
        default=os.getenv("DEPLOY_ENV", "development"),
        help="Target environment (default: development)",
    )

    # Deployment options
    parser.add_argument(
        "--source",
        "--frontend",
        type=str,
        help="Source directory for frontend assets (default: ./build)",
    )

    parser.add_argument(
        "--assets", type=str, help="Source directory for static assets (images, fonts, etc.)"
    )

    parser.add_argument(
        "--docs", type=str, help="Source directory for documentation (Sphinx, MkDocs, etc.)"
    )

    # Deployment behavior
    parser.add_argument(
        "--dry-run", action="store_true", help="Preview deployment without making changes"
    )

    parser.add_argument(
        "--no-dry-run", action="store_true", help="Skip dry-run even for production environment"
    )

    parser.add_argument(
        "--confirm", action="store_true", help="Require manual confirmation before deployment"
    )

    parser.add_argument("--no-confirm", action="store_true", help="Skip confirmation prompts")

    # CORS options
    parser.add_argument(
        "--cors-type",
        choices=[
            "development",
            "api_assets",
            "website_hosting",
            "cdn_assets",
            "secure_api",
            "mobile_app_assets",
        ],
        help="CORS configuration type to use",
    )

    parser.add_argument("--cors-origins", nargs="*", help="Additional CORS origins to allow")

    # Management operations
    parser.add_argument(
        "--test-cors", action="store_true", help="Test CORS configuration for deployed buckets"
    )

    parser.add_argument(
        "--list-buckets", action="store_true", help="List all buckets for the environment"
    )

    parser.add_argument(
        "--cleanup", action="store_true", help="Delete all buckets for the environment (DANGEROUS!)"
    )

    # Multi-environment operations
    parser.add_argument(
        "--deploy-all",
        action="store_true",
        help="Deploy to all environments (skips production by default)",
    )

    parser.add_argument(
        "--include-production",
        action="store_true",
        help="Include production in --deploy-all operations",
    )

    # Bucket customization
    parser.add_argument("--bucket-prefix", type=str, help="Override default bucket prefix")

    parser.add_argument(
        "--region", choices=["EU-WEST-PAR", "GRA", "RBX", "SBG"], help="Override default OVH region"
    )

    # Verbosity
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")

    parser.add_argument("--quiet", "-q", action="store_true", help="Suppress non-essential output")

    return parser


def validate_arguments(args) -> bool:
    """Validate command-line arguments."""

    # Check for conflicting options
    if args.dry_run and args.no_dry_run:
        print("❌ Error: Cannot specify both --dry-run and --no-dry-run")
        return False

    if args.confirm and args.no_confirm:
        print("❌ Error: Cannot specify both --confirm and --no-confirm")
        return False

    # Check if source directories exist
    if args.source and not Path(args.source).exists():
        print(f"❌ Error: Source directory not found: {args.source}")
        return False

    if args.assets and not Path(args.assets).exists():
        print(f"❌ Error: Assets directory not found: {args.assets}")
        return False

    if args.docs and not Path(args.docs).exists():
        print(f"❌ Error: Documentation directory not found: {args.docs}")
        return False

    # Check for required arguments for deployment
    has_deployment_operation = any([args.source, args.assets, args.docs, args.deploy_all])
    has_management_operation = any([args.test_cors, args.list_buckets, args.cleanup])

    if not has_deployment_operation and not has_management_operation:
        print(
            "❌ Error: No operation specified. Use --source, --assets, --docs, --test-cors, --list-buckets, or --cleanup"
        )
        return False

    return True


def create_deployment_manager(args) -> DeploymentManager:
    """Create a DeploymentManager with custom configuration based on arguments."""

    # Build custom configuration
    custom_config = {}

    if args.bucket_prefix:
        custom_config["bucket_prefix"] = args.bucket_prefix

    if args.region:
        custom_config["region"] = args.region

    if args.cors_type:
        custom_config["cors_type"] = args.cors_type

    if args.cors_origins:
        # Get existing domains from environment config first
        manager = DeploymentManager(args.env)
        existing_domains = manager.config.domains
        custom_config["domains"] = existing_domains + args.cors_origins

    if args.confirm:
        custom_config["require_confirmation"] = True
    elif args.no_confirm:
        custom_config["require_confirmation"] = False

    if args.dry_run:
        custom_config["dry_run_first"] = True
    elif args.no_dry_run:
        custom_config["dry_run_first"] = False

    return DeploymentManager(args.env, custom_config)


def deploy_frontend(manager: DeploymentManager, args) -> bool:
    """Deploy frontend assets."""
    source_dir = args.source or "./build"

    if args.verbose:
        print(f"🚀 Deploying frontend from {source_dir}")

    result = manager.deploy_frontend(
        source_dir=source_dir, dry_run_override=args.dry_run if args.dry_run else None
    )

    if result:
        if not args.quiet:
            print("✅ Frontend deployment successful!")
            if result.website_url:
                print(f"🌐 Website: {result.website_url}")
        return True
    else:
        print("❌ Frontend deployment failed")
        return False


def deploy_assets(manager: DeploymentManager, args) -> bool:
    """Deploy static assets."""
    if args.verbose:
        print(f"🚀 Deploying assets from {args.assets}")

    result = manager.deploy_assets(
        source_dir=args.assets, dry_run_override=args.dry_run if args.dry_run else None
    )

    if result:
        if not args.quiet:
            print("✅ Assets deployment successful!")
        return True
    else:
        print("❌ Assets deployment failed")
        return False


def deploy_docs(manager: DeploymentManager, args) -> bool:
    """Deploy documentation."""
    if args.verbose:
        print(f"🚀 Deploying documentation from {args.docs}")

    result = manager.deploy_docs(source_dir=args.docs)

    if result:
        if not args.quiet:
            print("✅ Documentation deployment successful!")
            if result.website_url:
                print(f"📚 Docs: {result.website_url}")
        return True
    else:
        print("❌ Documentation deployment failed")
        return False


def test_cors(manager: DeploymentManager, args) -> bool:
    """Test CORS configuration."""
    if args.verbose:
        print(f"🧪 Testing CORS for {args.env} environment")

    success = manager.test_cors()

    if success:
        if not args.quiet:
            print(f"✅ All CORS tests passed for {args.env}")
        return True
    else:
        print(f"❌ CORS tests failed for {args.env}")
        return False


def list_buckets(manager: DeploymentManager, args) -> bool:
    """List buckets for the environment."""
    if args.verbose:
        print(f"📦 Listing buckets for {args.env} environment")

    buckets = manager.list_buckets()

    if not args.quiet:
        if buckets:
            print(f"Found {len(buckets)} buckets for {args.env}")
        else:
            print(f"No buckets found for {args.env}")

    return True


def cleanup_environment(manager: DeploymentManager, args) -> bool:
    """Clean up environment buckets."""
    if args.verbose:
        print(f"🗑️  Cleaning up {args.env} environment")

    # Force confirmation for cleanup unless explicitly disabled
    require_confirmation = not args.no_confirm

    success = manager.cleanup_environment(confirm=require_confirmation)

    if success:
        if not args.quiet:
            print(f"✅ Environment {args.env} cleaned up successfully")
        return True
    else:
        print(f"❌ Environment cleanup failed for {args.env}")
        return False


def deploy_to_all_environments(args) -> bool:
    """Deploy to multiple environments."""
    if args.verbose:
        print("🚀 Deploying to all environments")

    multi_manager = MultiEnvironmentManager()

    source_dir = args.source or "./build"
    skip_production = not args.include_production

    results = multi_manager.deploy_to_all(source_dir=source_dir, skip_production=skip_production)

    # Summary
    successful_deployments = [env for env, result in results.items() if result is not None]
    failed_deployments = [
        env for env, result in results.items() if result is None and env != "production"
    ]

    if not args.quiet:
        print("\n📊 Deployment Summary:")
        print(
            f"✅ Successful: {', '.join(successful_deployments) if successful_deployments else 'None'}"
        )
        print(f"❌ Failed: {', '.join(failed_deployments) if failed_deployments else 'None'}")

        if skip_production:
            print("⏭️  Skipped: production (use --include-production to deploy)")

    return len(failed_deployments) == 0


def main():
    """Main entry point."""
    parser = setup_argument_parser()
    args = parser.parse_args()

    # Validate arguments
    if not validate_arguments(args):
        sys.exit(1)

    # Set up verbosity
    if args.verbose:
        print(f"🎯 Environment: {args.env}")
        print(
            f"🔧 Operation: {
                ', '.join(
                    [
                        op
                        for op in [
                            'frontend' if args.source else None,
                            'assets' if args.assets else None,
                            'docs' if args.docs else None,
                            'test-cors' if args.test_cors else None,
                            'list-buckets' if args.list_buckets else None,
                            'cleanup' if args.cleanup else None,
                            'deploy-all' if args.deploy_all else None,
                        ]
                        if op
                    ]
                )
            }"
        )

    try:
        # Handle multi-environment operations
        if args.deploy_all:
            success = deploy_to_all_environments(args)
            sys.exit(0 if success else 1)

        # Create deployment manager for single environment operations
        manager = create_deployment_manager(args)

        # Execute requested operations
        success = True

        # Management operations
        if args.test_cors:
            success &= test_cors(manager, args)

        if args.list_buckets:
            success &= list_buckets(manager, args)

        if args.cleanup:
            success &= cleanup_environment(manager, args)

        # Deployment operations
        if args.source:
            success &= deploy_frontend(manager, args)

        if args.assets:
            success &= deploy_assets(manager, args)

        if args.docs:
            success &= deploy_docs(manager, args)

        # Test CORS after deployments (unless explicitly testing CORS)
        if (args.source or args.assets or args.docs) and not args.test_cors and not args.quiet:
            if args.verbose:
                print("🧪 Running post-deployment CORS tests...")
            test_cors(manager, args)

        sys.exit(0 if success else 1)

    except KeyboardInterrupt:
        print("\n❌ Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        if args.verbose:
            import traceback

            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
