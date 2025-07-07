#!/usr/bin/env python3
"""
Example usage of the pca-estafette deployment system.

This script demonstrates various ways to use the deployment system
both programmatically and via command-line interfaces.

To use this example:
1. Install pca-estafette: pip install -e /path/to/pca-estafette
2. Set up your rclone.conf or environment variables
3. Customize the configurations below
4. Run: python example_usage.py
"""

from pathlib import Path

# Import the deployment modules
from deploy import DeploymentManager, CORSConfigurations


def example_1_simple_deployment():
    """Example 1: Simple deployment to development environment."""
    print("🚀 Example 1: Simple Development Deployment")

    # Create a deployment manager for development
    manager = DeploymentManager("development")

    # Deploy frontend assets
    result = manager.deploy_frontend(
        source_dir="./build",  # Your built React/Vue/Angular app
        dry_run_override=False,  # Skip dry run for this example
    )

    if result:
        print("✅ Deployed successfully!")
        print(f"🌐 Website URL: {result.website_url}")
        print(f"📁 Uploaded {len(result.files_uploaded)} files")

        # Test CORS after deployment
        manager.test_cors()
    else:
        print("❌ Deployment failed")


def example_2_custom_cors_configuration():
    """Example 2: Deployment with custom CORS configuration."""
    print("\n🔧 Example 2: Custom CORS Configuration")

    # Custom configuration for staging environment
    custom_config = {
        "bucket_prefix": "myproject-staging",
        "region": "EU-WEST-PAR",
        "cors_type": "api_assets",
        "domains": [
            "https://staging.myproject.com",
            "https://admin.myproject.com",
            "http://localhost:3000",  # For local development
        ],
        "require_confirmation": False,  # Skip confirmation for this example
        "dry_run_first": False,
    }

    manager = DeploymentManager("staging", custom_config)

    # Deploy with custom configuration
    result = manager.deploy_frontend("./dist")

    if result:
        print("✅ Custom staging deployment successful!")
        print(f"🌐 URL: {result.website_url}")


def example_3_multi_asset_deployment():
    """Example 3: Deploy multiple types of assets."""
    print("\n📦 Example 3: Multi-Asset Deployment")

    manager = DeploymentManager("staging")

    # Deploy frontend
    frontend_result = manager.deploy_frontend("./build")

    # Deploy static assets separately (for CDN optimization)
    assets_result = manager.deploy_assets("./public/assets")

    # Deploy documentation
    docs_result = manager.deploy_docs("./docs/_build/html")

    print("\n📊 Deployment Summary:")
    print(f"Frontend: {'✅' if frontend_result else '❌'}")
    print(f"Assets: {'✅' if assets_result else '❌'}")
    print(f"Docs: {'✅' if docs_result else '❌'}")


def example_4_environment_specific_cors():
    """Example 4: Different CORS settings per environment."""
    print("\n🌍 Example 4: Environment-Specific CORS")

    # Development: Allow all localhost variations
    dev_cors = CORSConfigurations.development([3000, 3001, 8080, 9000])

    # Staging: Restrict to staging domains
    staging_cors = CORSConfigurations.api_assets(
        ["https://staging.myapp.com", "https://staging-admin.myapp.com"]
    )

    # Production: Very restrictive
    prod_cors = CORSConfigurations.secure_api(["https://myapp.com", "https://www.myapp.com"])

    # Deploy to development with custom CORS
    dev_manager = DeploymentManager("development", {"cors_type": "development"})

    print("Deploying to development with permissive CORS...")
    dev_result = dev_manager.deploy_frontend("./build")

    if dev_result:
        print("✅ Development deployment with custom CORS successful!")


def example_5_production_deployment_with_safety():
    """Example 5: Production deployment with safety checks."""
    print("\n🛡️ Example 5: Safe Production Deployment")

    # Production configuration with all safety features enabled
    prod_config = {
        "bucket_prefix": "myapp-prod",
        "region": "GRA",  # Different region for production
        "cors_type": "secure_api",
        "domains": ["https://myapp.com", "https://www.myapp.com"],
        "require_confirmation": True,  # Always ask for confirmation
        "dry_run_first": True,  # Always dry run first
    }

    manager = DeploymentManager("production", prod_config)

    print("🔒 Production deployment with safety checks enabled...")
    print("Note: This will require manual confirmation and do dry-run first")

    # This would require user confirmation in a real scenario
    # result = manager.deploy_frontend("./build")


def example_6_cors_testing():
    """Example 6: Comprehensive CORS testing."""
    print("\n🧪 Example 6: CORS Testing")

    manager = DeploymentManager("staging")

    # Test CORS for multiple domains
    test_domains = [
        "https://staging.myapp.com",  # Should pass
        "https://myapp.com",  # Should pass
        "http://localhost:3000",  # Should pass
        "https://evil-domain.com",  # Should fail
        "http://random-site.org",  # Should fail
    ]

    print("Testing CORS for various domains:")
    for domain in test_domains:
        try:
            cors_works = manager.estafette.cors_manager.test_cors(
                bucket_name=f"{manager.config.bucket_prefix}-frontend",
                region=manager.config.region,
                origin=domain,
                file_path="index.html",
            )

            status = "✅ ALLOWED" if cors_works else "❌ BLOCKED"
            print(f"{status} {domain}")

        except Exception as e:
            print(f"❌ ERROR testing {domain}: {e}")


def example_7_bucket_management():
    """Example 7: Bucket listing and cleanup."""
    print("\n🗂️ Example 7: Bucket Management")

    manager = DeploymentManager("development")

    # List buckets for this environment
    print("📦 Current buckets:")
    buckets = manager.list_buckets()

    # Cleanup example (commented out for safety)
    # WARNING: This would delete all buckets!
    # print("🗑️ Cleanup example (NOT EXECUTED):")
    # print("manager.cleanup_environment() would delete all development buckets")


def example_8_custom_file_usage():
    """Example 8: Using the deployment system as a library."""
    print("\n📚 Example 8: Library Usage")

    # Import the core components directly
    from estafettes.ovh import OVHEstafette
    from estafettes.ovh.models import CORSSettings

    # Use the low-level API directly
    estafette = OVHEstafette(region="EU-WEST-PAR")

    # Custom CORS settings
    custom_cors = CORSSettings(
        allowed_origins=["https://myapp.com"],
        allowed_methods=["GET", "HEAD"],
        allowed_headers=["Content-Type"],
        max_age=3600,
    )

    # Deploy using the low-level API
    print("Using low-level OVHEstafette API...")

    # This would deploy if you have actual files to deploy
    # result = estafette.deploy(
    #     bucket_name="my-custom-bucket",
    #     source_dir="./build",
    #     static_website=True,
    #     dry_run=True  # Safe dry run
    # )


def main():
    """Run all examples."""
    print("🎯 pca-estafette Deployment Examples")
    print("=" * 50)

    # Check if build directory exists
    if not Path("./build").exists():
        print("⚠️  Note: ./build directory not found - creating dummy for examples")
        Path("./build").mkdir(exist_ok=True)
        Path("./build/index.html").write_text("<html><body>Hello World</body></html>")

    try:
        # Run examples (comment out any you don't want to run)
        example_1_simple_deployment()
        # example_2_custom_cors_configuration()
        # example_3_multi_asset_deployment()
        # example_4_environment_specific_cors()
        # example_5_production_deployment_with_safety()
        # example_6_cors_testing()
        # example_7_bucket_management()
        # example_8_custom_file_usage()

        print("\n✅ Examples completed!")

    except Exception as e:
        print(f"\n❌ Example failed: {e}")
        print("Make sure you have:")
        print("1. Installed pca-estafette: pip install -e /path/to/pca-estafette")
        print("2. Set up your rclone.conf with OVH credentials")
        print("3. Created the directories referenced in the examples")


if __name__ == "__main__":
    main()
