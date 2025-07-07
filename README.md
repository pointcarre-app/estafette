# Estafettes

A comprehensive Python toolkit for **Brevo** email automation and **OVH Object-Storage** deployments with type-safe models and rich CLI interfaces.

## Features

### 📧 Brevo Email
- 🎯 **Simple Email API** – intuitive `send()` method
- 🔒 **Type Safety** – Pydantic models with validation
- 📎 **Attachments** – files, URLs, and automatic processing
- 🎨 **HTML Templates** – Jinja2 rendering with context variables
- 🔐 **Secure Config** – API key management and environment support

### 🪣 OVH Object-Storage
- 🏗️ **Complete Bucket Management** – create, delete, list with region support
- 📁 **Advanced File Sync** – progress bars, filtering, path management
- 🌐 **Static Website Hosting** – full setup with ACL management
- 🔗 **Smart URL Generation** – direct HTTPS + website HTTP URLs
- 🛂 **Dynamic CORS Policies** – multi-origin support with testing
- 🖥️ **Rich CLI Interface** – dry-run mode, colored output, confirmation prompts
- 🔧 **Flexible Configuration** – rclone.conf, environment variables, direct credentials
- 🌍 **Multi-Region Support** – EU-WEST-PAR, GRA, RBX, SBG with automatic endpoint resolution

## Installation

```bash
pip install pca-estafette
```

## Quick Start

### Brevo Email

```python
from estafettes.brevo import BrevoEstafette
from estafettes.brevo.models import Email, Sender, Recipient

# Initialize client with API key
client = BrevoEstafette(api_key="your-brevo-api-key")

# Create email
email = Email(
    to=Recipient(email="user@example.com", name="John Doe"),
    sender=Sender(email="sender@yourdomain.com", name="Your Name"),
    subject="Hello from Estafettes",
    body="This is a test email"
)

# Send email
client.send(email)
```

### OVH Object-Storage (CLI)

```bash
# Deploy static website with dry-run preview
python -m estafettes.ovh.cli deploy \
    --bucket my-website \
    --source ./build \
    --static-website \
    --dry-run

# Real deployment with CORS
python -m estafettes.ovh.cli deploy \
    --bucket my-website \
    --source ./build \
    --static-website

# List all buckets
python -m estafettes.ovh.cli buckets --list

# Delete bucket with contents
python -m estafettes.ovh.cli buckets --delete my-old-bucket --force
```

### OVH Object-Storage (Programmatic)

```python
from estafettes.ovh import OVHEstafette

# Initialize with automatic credential discovery
estafette = OVHEstafette(
    config_file="rclone.conf",  # or use environment variables
    region="EU-WEST-PAR"
)

# Deploy with full website setup
result = estafette.deploy(
    bucket_name="my-website",
    source_dir="./build",
    static_website=True,
    dry_run=False
)

# Access generated URLs
print(f"Website URL: {result.website_url}")
for url in result.direct_urls:
    print(f"Direct URL: {url}")
```

## Configuration

### Brevo Configuration

Store your API key in a `.env` file:

```env
SIB_API_KEY=your-brevo-api-key
```

```python
import os
from dotenv import load_dotenv
from estafettes.brevo import BrevoEstafette

load_dotenv()
client = BrevoEstafette(api_key=os.getenv("SIB_API_KEY"))
```

### OVH Configuration

Multiple credential sources are supported with automatic fallback:

1. **Direct credentials**:
```python
estafette = OVHEstafette(
    access_key="your-access-key",
    secret_key="your-secret-key"
)
```

2. **Environment variables**:
```bash
export AWS_ACCESS_KEY_ID=your-access-key
export AWS_SECRET_ACCESS_KEY=your-secret-key
```

3. **rclone.conf file**:
```ini
[StorageS3]
type = s3
provider = Other
access_key_id = your-access-key
secret_access_key = your-secret-key
endpoint = https://s3.eu-west-par.scw.cloud
region = eu-west-par
```

## Advanced Features

### Email Templates

```python
from estafettes.brevo.models import Email, Sender, Recipient

# Email with HTML template
email = Email(
    to=Recipient(email="user@example.com", name="John Doe"),
    sender=Sender(email="sender@yourdomain.com", name="Your Name"),
    subject="Welcome to our service",
    body="Welcome! Please see the HTML version.",
    template_name="welcome.html",
    template_dir="./templates",
    context={
        "user_name": "John Doe",
        "company_name": "Your Company",
        "activation_link": "https://example.com/activate"
    }
)

client.send(email)
```

### OVH Region Configuration

```python
# Supported regions with automatic endpoint resolution
regions = ["EU-WEST-PAR", "GRA", "RBX", "SBG"]

for region in regions:
    estafette = OVHEstafette(region=region)
    result = estafette.deploy(
        bucket_name=f"my-site-{region.lower()}",
        source_dir="./build",
        static_website=True
    )
```

### CORS Configuration

```python
# Manual CORS application
estafette.cors_manager.apply_cors_policy(
    bucket_name="my-bucket",
    region="EU-WEST-PAR"
)

# Test CORS from different origins
estafette.cors_manager.test_cors(
    bucket_name="my-bucket",
    region="EU-WEST-PAR",
    origin="https://mysite.com"
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

### Bucket Management

```bash
# List buckets
python -m estafettes.ovh.cli buckets --list

# Delete bucket
python -m estafettes.ovh.cli buckets --delete BUCKET_NAME [--force]

# Apply CORS policy
python -m estafettes.ovh.cli cors-apply --bucket BUCKET_NAME
```

## ⚠️ Danger Zone

### Mass Bucket Deletion

**🚨 EXTREMELY DANGEROUS - USE WITH EXTREME CAUTION 🚨**

For development/testing scenarios where you need to delete ALL buckets:

```bash
# ⚠️ DANGER: This will DELETE ALL BUCKETS and their contents!
python src/estafettes/ovh/delete_all_buckets.py
```

**Safety Features:**
- 📅 Requires typing today's date (YYYY-MM-DD format)
- 🔄 Double confirmation required
- 📊 Shows progress and handles errors gracefully
- 🛡️ No accidental execution - multiple confirmation steps

**⚠️ THIS CANNOT BE UNDONE - ALL DATA WILL BE LOST ⚠️**

## Development

### Running Tests

```bash
# Unit tests
python -m pytest tests/

# Integration tests (requires credentials)
OVH_LIVE_TESTS=true python -m pytest tests/test_ovh_estafette.py

# CLI tests
python -m pytest tests/test_ovh_estafette_cli.py
```

### Documentation

```bash
# Build documentation
mkdocs build

# Serve locally
mkdocs serve

# Deploy to GitHub Pages
mkdocs gh-deploy
```

## Architecture

### Modular Design

- **estafettes.brevo**: Complete email automation with Pydantic models
- **estafettes.ovh**: Full-featured OVH Object-Storage deployment toolkit
- **Rich CLI**: User-friendly command-line interface with progress bars
- **Flexible Configuration**: Multiple credential sources and validation
- **Type Safety**: Comprehensive Pydantic models throughout

### Key Components

- **OVHEstafette**: Main orchestrator class
- **BucketManager**: Bucket operations (create, delete, list)
- **FileManager**: File synchronization with progress tracking
- **CORSManager**: Dynamic CORS policy generation and testing
- **WebsiteManager**: Static website hosting configuration
- **URLGenerator**: Smart URL generation for different access patterns

## License

MIT License