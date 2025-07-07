# OVH Object-Storage API Reference

## Overview

The OVH Object-Storage module provides a comprehensive toolkit for deploying and managing static websites and files on OVH's S3-compatible object storage service.

## Core Classes

### OVHEstafette

The main orchestrator class that coordinates all OVH operations.

```python
from estafettes.ovh import OVHEstafette

estafette = OVHEstafette(
    config_file="rclone.conf",  # Configuration file path
    region="EU-WEST-PAR",       # OVH region
    console=None                # Optional Rich console instance
)
```

**Key Methods:**

- `deploy()` - Complete deployment orchestration
- `list_buckets()` - List all buckets
- `delete_bucket()` - Delete bucket with optional force

### Configuration Management

#### OVHConfig

Handles configuration, credentials, and region management.

```python
from estafettes.ovh.config import OVHConfig

config = OVHConfig(config_file="rclone.conf")

# Get credentials from multiple sources
credentials = config.get_credentials()

# Validate regions
is_valid = config.validate_region("EU-WEST-PAR")

# Get region configuration
region_config = config.get_region_config("EU-WEST-PAR")
```

#### Supported Regions

| Region | Code | Endpoint |
|--------|------|----------|
| EU-WEST-PAR | `EU-WEST-PAR` | `https://s3.eu-west-par.scw.cloud` |
| GRA | `GRA` | `https://s3.gra.cloud.ovh.net` |
| RBX | `RBX` | `https://s3.rbx.cloud.ovh.net` |
| SBG | `SBG` | `https://s3.sbg.cloud.ovh.net` |

### Bucket Management

#### BucketManager

Handles all bucket operations.

```python
from estafettes.ovh.bucket_manager import BucketManager
from estafettes.ovh.config import OVHConfig

config = OVHConfig()
bucket_manager = BucketManager(config)

# Create bucket
bucket_manager.create_bucket(
    bucket_name="my-bucket",
    region="EU-WEST-PAR",
    acl="public-read"
)

# List buckets
buckets = bucket_manager.list_buckets()

# Delete bucket
bucket_manager.delete_bucket(
    bucket_name="old-bucket",
    force=True  # Delete all contents first
)

# Check if bucket exists
exists = bucket_manager.bucket_exists("my-bucket")
```

### File Management

#### FileManager

Handles file synchronization and uploads.

```python
from estafettes.ovh.file_manager import FileManager
from estafettes.ovh.config import OVHConfig

config = OVHConfig()
file_manager = FileManager(config)

# Sync entire directory
uploaded_files = file_manager.sync_files(
    source_path="./build",
    bucket_name="my-bucket",
    destination_prefix="assets/",
    region="EU-WEST-PAR",
    static_website=True,  # Flatten directory structure
    dry_run=False
)

# Upload single file
success = file_manager.upload_file(
    local_path="./document.pdf",
    bucket_name="my-bucket",
    remote_key="documents/document.pdf"
)

# List remote files
remote_files = file_manager.list_remote_files(
    bucket_name="my-bucket",
    prefix="assets/",
    recursive=True
)

# Get file metadata
metadata = file_manager.get_file_metadata(
    bucket_name="my-bucket",
    remote_key="assets/index.html"
)
```

### CORS Management

#### CORSManager

Dynamic CORS policy generation and testing.

```python
from estafettes.ovh.cors_manager import CORSManager
from estafettes.ovh.config import OVHConfig

config = OVHConfig()
cors_manager = CORSManager(config)

# Create CORS policy
cors_policy = cors_manager.create_cors_policy(
    bucket_name="my-bucket",
    region="EU-WEST-PAR",
    additional_origins=["https://mysite.com", "https://staging.mysite.com"]
)

# Apply CORS policy
success = cors_manager.apply_cors_policy(
    bucket_name="my-bucket",
    region="EU-WEST-PAR",
    cors_policy=cors_policy
)

# Test CORS
cors_works = cors_manager.test_cors(
    bucket_name="my-bucket",
    region="EU-WEST-PAR",
    origin="https://mysite.com",
    file_path="index.html"
)
```

### Website Management

#### WebsiteManager

Static website hosting configuration.

```python
from estafettes.ovh.website_manager import WebsiteManager
from estafettes.ovh.config import OVHConfig

config = OVHConfig()
website_manager = WebsiteManager(config)

# Configure static website hosting
website_manager.apply_website_configuration(
    bucket_name="my-website",
    region="EU-WEST-PAR",
    index_document="index.html",
    error_document="error.html"
)

# Set public read permissions
website_manager.set_bucket_public_read("my-website")
website_manager.set_objects_public_read("my-website")
```

### URL Generation

#### URLGenerator

Generate access URLs for different use cases.

```python
from estafettes.ovh.url_generator import URLGenerator
from estafettes.ovh.config import OVHConfig

config = OVHConfig()
url_generator = URLGenerator(config)

# Direct HTTPS access URL
direct_url = url_generator.generate_direct_url(
    bucket_name="my-bucket",
    file_path="assets/image.jpg",
    region="EU-WEST-PAR"
)

# Static website HTTP URL
website_url = url_generator.generate_website_url(
    bucket_name="my-bucket",
    file_path="index.html",
    region="EU-WEST-PAR"
)

# Base URL for bucket
base_url = url_generator.generate_base_url(
    bucket_name="my-bucket",
    region="EU-WEST-PAR"
)

# Multiple file URLs
file_urls = url_generator.generate_file_urls(
    bucket_name="my-bucket",
    files=["index.html", "style.css", "script.js"],
    region="EU-WEST-PAR",
    static_website=True
)
```

## Data Models

### Core Models

#### BucketInfo

```python
from estafettes.ovh.models import BucketInfo

bucket = BucketInfo(
    name="my-bucket",
    region="EU-WEST-PAR",
    creation_date=datetime.now()
)
```

#### DeploymentResult

```python
from estafettes.ovh.models import DeploymentResult

result = DeploymentResult(
    success=True,
    bucket_name="my-bucket",
    region="EU-WEST-PAR",
    files_uploaded=["index.html", "style.css"],
    direct_urls=["https://..."],
    website_url="http://...",
    errors=[]
)
```

#### CORSPolicy

```python
from estafettes.ovh.models import CORSPolicy

policy = CORSPolicy(
    allowed_origins=["https://mysite.com", "*"],
    allowed_methods=["GET", "POST"],
    allowed_headers=["*"],
    max_age_seconds=3600
)
```

### Configuration Models

#### OVHCredentials

```python
from estafettes.ovh.models import OVHCredentials

credentials = OVHCredentials(
    access_key="your-access-key",
    secret_key="your-secret-key"
)

# Masked display
print(credentials.mask_access_key())  # "your-a***-key"
print(credentials.mask_secret_key())  # "your-s***-key"
```

#### OVHRegionConfig

```python
from estafettes.ovh.models import OVHRegionConfig

region_config = OVHRegionConfig(
    region_code="eu-west-par",
    endpoint="https://s3.eu-west-par.scw.cloud",
    website_suffix="s3-website.eu-west-par.scw.cloud"
)
```

## CLI Reference

### Deploy Command

```bash
python -m estafettes.ovh.cli deploy \
    --bucket BUCKET_NAME \
    --source SOURCE_DIR \
    [--static-website] \
    [--skip-cors] \
    [--dry-run] \
    [--region REGION] \
    [--config CONFIG_FILE]
```

**Options:**
- `--bucket`: Target bucket name (required)
- `--source`: Source directory to upload (required)
- `--static-website`: Enable static website hosting
- `--skip-cors`: Skip CORS policy application
- `--dry-run`: Preview actions without executing
- `--region`: OVH region (default: EU-WEST-PAR)
- `--config`: Path to rclone.conf file

### Bucket Commands

```bash
# List all buckets
python -m estafettes.ovh.cli buckets --list

# Delete bucket
python -m estafettes.ovh.cli buckets --delete BUCKET_NAME

# Force delete with contents
python -m estafettes.ovh.cli buckets --delete BUCKET_NAME --force
```

### CORS Commands

```bash
# Apply CORS policy
python -m estafettes.ovh.cli cors-apply --bucket BUCKET_NAME
```

## Configuration Files

### rclone.conf Format

```ini
[StorageS3]
type = s3
provider = Other
access_key_id = your-access-key
secret_access_key = your-secret-key
endpoint = https://s3.eu-west-par.scw.cloud
region = eu-west-par
```

### Environment Variables

```bash
# AWS-compatible environment variables
export AWS_ACCESS_KEY_ID=your-access-key
export AWS_SECRET_ACCESS_KEY=your-secret-key

# OVH-specific environment variables
export OVH_ACCESS_KEY_ID=your-access-key
export OVH_SECRET_ACCESS_KEY=your-secret-key
```

## Error Handling

### Common Exceptions

```python
import typer
from botocore.exceptions import ClientError

try:
    result = estafette.deploy(
        bucket_name="my-bucket",
        source_dir="./build",
        static_website=True
    )
except typer.Exit as e:
    print(f"Configuration error: {e}")
except ClientError as e:
    print(f"AWS/OVH API error: {e}")
except FileNotFoundError as e:
    print(f"File not found: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

### Validation Errors

The library performs extensive validation:

- Bucket name format validation
- Region code validation
- File path validation
- Credential format validation

## Best Practices

### 1. Use Dry-Run First

```python
# Always test first
result = estafette.deploy(
    bucket_name="production-site",
    source_dir="./build",
    static_website=True,
    dry_run=True
)

# Then deploy for real
result = estafette.deploy(
    bucket_name="production-site",
    source_dir="./build",
    static_website=True,
    dry_run=False
)
```

### 2. Handle Credentials Securely

```python
# Use environment variables or rclone.conf
# Avoid hardcoding credentials
estafette = OVHEstafette()  # Auto-discovery

# If you must use direct credentials, use environment variables
import os
access_key = os.getenv("OVH_ACCESS_KEY")
secret_key = os.getenv("OVH_SECRET_KEY")
```

### 3. Test CORS After Deployment

```python
# Always test CORS if using for web applications
cors_success = estafette.cors_manager.test_cors(
    bucket_name="my-bucket",
    region="EU-WEST-PAR",
    origin="https://mysite.com"
)

if not cors_success:
    print("⚠️ CORS test failed - check configuration")
```

### 4. Use Appropriate ACLs

```python
# For public websites
estafette.bucket_manager.create_bucket(
    bucket_name="public-site",
    acl="public-read"
)

# For private storage
estafette.bucket_manager.create_bucket(
    bucket_name="private-files",
    acl="private"
)
```

## Advanced Usage

### Custom Deployment Pipeline

```python
from estafettes.ovh import OVHEstafette
from pathlib import Path

class CustomDeployment:
    def __init__(self, region="EU-WEST-PAR"):
        self.estafette = OVHEstafette(region=region)
    
    def deploy_with_validation(self, bucket_name, source_dir):
        # 1. Validate source
        if not Path(source_dir).exists():
            raise ValueError(f"Source not found: {source_dir}")
        
        # 2. Check if bucket exists
        if not self.estafette.bucket_manager.bucket_exists(bucket_name):
            print(f"Creating bucket: {bucket_name}")
            self.estafette.bucket_manager.create_bucket(bucket_name)
        
        # 3. Deploy
        result = self.estafette.deploy(
            bucket_name=bucket_name,
            source_dir=source_dir,
            static_website=True
        )
        
        # 4. Validate deployment
        for url in result.direct_urls:
            print(f"✅ Available: {url}")
        
        return result
```

### Multi-Region Deployment

```python
from estafettes.ovh import OVHEstafette

def deploy_to_all_regions(bucket_base_name, source_dir):
    regions = ["EU-WEST-PAR", "GRA", "RBX", "SBG"]
    results = {}
    
    for region in regions:
        estafette = OVHEstafette(region=region)
        bucket_name = f"{bucket_base_name}-{region.lower()}"
        
        try:
            result = estafette.deploy(
                bucket_name=bucket_name,
                source_dir=source_dir,
                static_website=True
            )
            results[region] = result
            print(f"✅ {region}: {result.website_url}")
        except Exception as e:
            print(f"❌ {region}: {e}")
            results[region] = None
    
    return results
```

## ⚠️ Danger Zone

### Mass Bucket Deletion Script

**🚨 EXTREMELY DANGEROUS - DEVELOPMENT USE ONLY 🚨**

Located at `src/estafettes/ovh/delete_all_buckets.py`, this script provides nuclear-level cleanup for development environments.

```bash
# ⚠️ DANGER: Deletes ALL buckets and contents
python src/estafettes/ovh/delete_all_buckets.py
```

**Safety mechanisms:**
- Date verification (must type current date YYYY-MM-DD)
- Double confirmation required
- Progress tracking with error handling
- Cannot be automated or batched

**Critical Warnings:**
- ❌ **NEVER use in production**
- ❌ **All data is permanently lost**
- ❌ **No recovery mechanism exists**
- ✅ **Only for development cleanup**

---

This comprehensive API reference covers all the implemented functionality in the OVH Object-Storage module. The library provides a complete toolkit for deploying static websites and managing files on OVH's object storage service. 