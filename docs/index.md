# Estafettes

A comprehensive Python toolkit for **Brevo** email automation and **OVH Object-Storage** deployments with type-safe models and rich CLI interfaces.

## Quick Start

### Brevo Email

```python
from estafettes.brevo.models import Email, Sender, Recipient
from estafettes.brevo import BrevoEstafette

# Create an email
email = Email(
    to=Recipient(email="user@example.com", name="John Doe"),
    sender=Sender(email="sender@example.com", name="John Doe"),
    subject="Hello World",
    body="This is a test email"
)

# Send it
service = BrevoEstafette(api_key="your-brevo-api-key")
service.send(email)
```

### OVH Object-Storage

```python
from estafettes.ovh import OVHEstafette

# Deploy static website
estafette = OVHEstafette(config_file="rclone.conf", region="EU-WEST-PAR")
result = estafette.deploy(
    bucket_name="my-website",
    source_dir="./build",
    static_website=True
)

print(f"Website URL: {result.website_url}")
```

## Features

### 📧 Brevo Email Module
- ✅ **Pydantic Models** - Type-safe Email, Sender, Recipient models
- ✅ **Template Rendering** - Jinja2 templates with context variables
- ✅ **Attachment Processing** - Automatic handling of files and URLs
- ✅ **Environment Config** - Secure API key management
- ✅ **Validation** - Comprehensive input validation

### 🪣 OVH Object-Storage Module
- ✅ **Multi-Region Support** - EU-WEST-PAR, GRA, RBX, SBG regions
- ✅ **Bucket Management** - Create, delete, list with ACL support
- ✅ **File Synchronization** - Progress bars, filtering, path management
- ✅ **Static Website Hosting** - Complete setup with public ACL
- ✅ **Dynamic CORS Policies** - Multi-origin support with testing
- ✅ **Smart URL Generation** - Direct HTTPS and website HTTP URLs
- ✅ **Rich CLI Interface** - Dry-run mode, colored output, progress tracking
- ✅ **Flexible Configuration** - rclone.conf, environment variables, direct credentials
- ⚠️ **Danger Zone** - Mass bucket deletion script (development use only)

## Architecture

### Modular Design

The toolkit is organized into two main modules:

| Module | Purpose | Key Features |
|--------|---------|-------------|
| **estafettes.brevo** | Email automation | Pydantic models, template rendering, secure API integration |
| **estafettes.ovh** | Object-Storage deployment | Multi-region support, static website hosting, rich CLI |

### Key Components

#### OVH Object-Storage Components
- **OVHEstafette** - Main orchestrator class
- **BucketManager** - Bucket operations (create, delete, list)
- **FileManager** - File synchronization with progress tracking
- **CORSManager** - Dynamic CORS policy generation and testing
- **WebsiteManager** - Static website hosting configuration
- **URLGenerator** - Smart URL generation for different access patterns

#### Brevo Email Components
- **BrevoEstafette** - Main email service class
- **Email Model** - Type-safe email representation
- **Template Renderer** - Jinja2 template processing
- **Attachment Handler** - File and URL attachment processing

## CLI Usage

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
```

## What Makes Estafettes Different?

1. **Type Safety First** - Comprehensive Pydantic models throughout
2. **Rich User Experience** - Progress bars, colored output, dry-run modes
3. **Flexible Configuration** - Multiple credential sources with automatic fallback
4. **Production Ready** - Comprehensive error handling and validation
5. **Multi-Region Support** - Full OVH region coverage with automatic endpoint resolution
6. **Complete Feature Set** - From basic file uploads to full static website hosting

Head to **Examples** to see detailed usage patterns and advanced configurations.