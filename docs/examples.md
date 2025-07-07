# Examples

## Brevo Email Examples

### Basic Email Usage

```python
from estafettes.brevo import BrevoEstafette
from estafettes.brevo.models import Email, Sender, Recipient

# Initialize client with API key
client = BrevoEstafette(api_key="your-brevo-api-key")

# Create and send email
email = Email(
    to=Recipient(email="user@example.com", name="John"),
    sender=Sender(email="sender@example.com", name="Company"),
    subject="Hello World",
    body="This is a test email"
)

client.send(email)
```

### Email with Attachments

```python
from estafettes.brevo.models import Email, Sender, Recipient

email = Email(
    to=Recipient(email="user@example.com", name="John"),
    sender=Sender(email="sender@example.com", name="John"),
    subject="Files attached",
    body="Please find attached files",
    attachment_sources={
        "invoice.pdf": "/path/to/invoice.pdf",
        "report.xlsx": "https://example.com/report.xlsx"
    }
)

# Attachments are automatically processed!
print(f"Created {len(email.attachments)} attachments")
```

### Email with HTML Templates

```python
from estafettes.brevo.models import Email, Sender, Recipient

email = Email(
    to=Recipient(email="user@example.com", name="John"),
    sender=Sender(email="sender@example.com", name="Company"),
    subject="Welcome to our service",
    body="Welcome! Please see the HTML version of this email.",
    template_name="welcome.html",
    template_dir="/path/to/templates",  # Required when using templates
    context={
        "user_name": "John",
        "company_name": "Your Company",
        "activation_link": "https://example.com/activate"
    }
)

# HTML content is automatically rendered from template
print(f"HTML generated: {len(email.html_content)} characters")
```

### Environment Configuration

```python
import os
from dotenv import load_dotenv
from estafettes.brevo import BrevoEstafette

# Load environment variables
load_dotenv()

# Initialize client with API key from environment
client = BrevoEstafette(api_key=os.getenv("SIB_API_KEY"))
```

## OVH Object-Storage Examples

### Quick CLI Deployment

```bash
# Dry-run deployment (no network changes)
python -m estafettes.ovh.cli deploy \
    --bucket demo-dryrun \
    --source ./build \
    --static-website --dry-run

# Real deployment with CORS
python -m estafettes.ovh.cli deploy \
    --bucket demo-site \
    --source ./build \
    --static-website

# List buckets
python -m estafettes.ovh.cli buckets --list

# Delete bucket with contents
python -m estafettes.ovh.cli buckets --delete old-bucket --force
```

### Programmatic Usage

```python
from estafettes.ovh import OVHEstafette

# Initialize with automatic credential discovery
estafette = OVHEstafette(
    config_file="rclone.conf",
    region="EU-WEST-PAR"
)

# Deploy static website
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

### Multi-Region Deployment

```python
from estafettes.ovh import OVHEstafette

# Deploy to multiple regions
regions = ["EU-WEST-PAR", "GRA", "RBX", "SBG"]

for region in regions:
    estafette = OVHEstafette(region=region)
    result = estafette.deploy(
        bucket_name=f"my-site-{region.lower()}",
        source_dir="./build",
        static_website=True
    )
    print(f"Deployed to {region}: {result.website_url}")
```

### Advanced Configuration

```python
from estafettes.ovh import OVHEstafette

# Multiple credential sources
estafette = OVHEstafette(
    config_file="rclone.conf",  # Try rclone.conf first
    region="EU-WEST-PAR"
)

# Or use environment variables
import os
os.environ["AWS_ACCESS_KEY_ID"] = "your-access-key"
os.environ["AWS_SECRET_ACCESS_KEY"] = "your-secret-key"

estafette = OVHEstafette(region="EU-WEST-PAR")
```

### Bucket Management

```python
from estafettes.ovh import OVHEstafette

estafette = OVHEstafette()

# Create bucket
estafette.bucket_manager.create_bucket(
    bucket_name="my-new-bucket",
    region="EU-WEST-PAR",
    acl="public-read"
)

# List all buckets
buckets = estafette.list_buckets()
for bucket in buckets:
    print(f"Bucket: {bucket.name} (created: {bucket.creation_date})")

# Delete bucket
estafette.delete_bucket("old-bucket", force=True)
```

### CORS Configuration

```python
from estafettes.ovh import OVHEstafette

estafette = OVHEstafette()

# Apply CORS policy
estafette.cors_manager.apply_cors_policy(
    bucket_name="my-bucket",
    region="EU-WEST-PAR"
)

# Test CORS from different origins
origins = [
    "https://mysite.com",
    "https://staging.mysite.com",
    "http://localhost:3000"
]

for origin in origins:
    success = estafette.cors_manager.test_cors(
        bucket_name="my-bucket",
        region="EU-WEST-PAR",
        origin=origin
    )
    print(f"CORS test for {origin}: {'✅' if success else '❌'}")
```

### File Operations

```python
from estafettes.ovh import OVHEstafette

estafette = OVHEstafette()

# Upload single file
estafette.file_manager.upload_file(
    local_path="./document.pdf",
    bucket_name="my-bucket",
    remote_key="documents/document.pdf"
)

# Sync entire directory
uploaded_files = estafette.file_manager.sync_files(
    source_path="./build",
    bucket_name="my-bucket",
    destination_prefix="assets/",
    static_website=True
)

print(f"Uploaded {len(uploaded_files)} files")

# List remote files
remote_files = estafette.file_manager.list_remote_files(
    bucket_name="my-bucket",
    prefix="assets/",
    recursive=True
)
```

### URL Generation

```python
from estafettes.ovh import OVHEstafette

estafette = OVHEstafette()

# Generate direct access URLs
direct_url = estafette.url_generator.generate_direct_url(
    bucket_name="my-bucket",
    file_path="assets/image.jpg",
    region="EU-WEST-PAR"
)

# Generate website URLs
website_url = estafette.url_generator.generate_website_url(
    bucket_name="my-bucket",
    file_path="index.html",
    region="EU-WEST-PAR"
)

print(f"Direct URL: {direct_url}")
print(f"Website URL: {website_url}")
```

### Website Hosting

```python
from estafettes.ovh import OVHEstafette

estafette = OVHEstafette()

# Configure static website hosting
estafette.website_manager.apply_website_configuration(
    bucket_name="my-website",
    region="EU-WEST-PAR",
    index_document="index.html",
    error_document="error.html"
)

# Set public read permissions
estafette.website_manager.set_bucket_public_read("my-website")
estafette.website_manager.set_objects_public_read("my-website")
```

### Complete Deployment Pipeline

```python
from estafettes.ovh import OVHEstafette
from pathlib import Path

def deploy_website(source_dir: str, bucket_name: str, region: str = "EU-WEST-PAR"):
    """Complete deployment pipeline with error handling."""
    
    estafette = OVHEstafette(region=region)
    
    try:
        # 1. Validate source directory
        if not Path(source_dir).exists():
            raise ValueError(f"Source directory not found: {source_dir}")
        
        # 2. Deploy with dry-run first
        print("🔍 Dry-run deployment...")
        dry_result = estafette.deploy(
            bucket_name=bucket_name,
            source_dir=source_dir,
            static_website=True,
            dry_run=True
        )
        
        # 3. Confirm and deploy
        print("🚀 Deploying...")
        result = estafette.deploy(
            bucket_name=bucket_name,
            source_dir=source_dir,
            static_website=True,
            dry_run=False
        )
        
        # 4. Test CORS
        print("🔗 Testing CORS...")
        cors_success = estafette.cors_manager.test_cors(
            bucket_name=bucket_name,
            region=region,
            origin="https://example.com"
        )
        
        # 5. Report results
        print(f"✅ Deployment successful!")
        print(f"📁 Files uploaded: {len(result.files_uploaded)}")
        print(f"🌐 Website URL: {result.website_url}")
        print(f"🔗 CORS test: {'✅' if cors_success else '❌'}")
        
        return result
        
    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        raise

# Usage
deploy_website("./build", "my-production-site", "EU-WEST-PAR")
```

## ⚠️ Danger Zone - Mass Bucket Deletion

### 🚨 EXTREMELY DANGEROUS FEATURE 🚨

**USE ONLY IN DEVELOPMENT/TESTING - NEVER IN PRODUCTION**

For scenarios where you need to completely clean up all buckets (e.g., development cleanup, testing reset):

```bash
# ⚠️ NUCLEAR OPTION: Delete ALL buckets and contents
python src/estafettes/ovh/delete_all_buckets.py
```

**What this script does:**
1. 🔍 Lists all buckets in your configured region
2. 📅 Requires you to type today's date (YYYY-MM-DD) for confirmation
3. 🔄 Asks for final "yes/no" confirmation
4. 🗑️ Deletes ALL buckets and their contents with `force=True`
5. 📊 Shows deletion progress and error handling

**Example execution:**
```
🔍 Fetching bucket list...

📋 Found 8 buckets:
  1. test-bucket-abc123
  2. demo-site-staging
  3. my-old-project
  4. experiment-bucket
  ... (and 4 more)

⚠️  This will DELETE ALL 8 buckets and their contents!
🗓️  To confirm, please type today's date: 2024-01-15
Enter date (YYYY-MM-DD): 2024-01-15

🚨 Final confirmation: Delete 8 buckets? (yes/no): yes

🗑️  Deleting 8 buckets...
  [1/8] Deleting test-bucket-abc123... ✅
  [2/8] Deleting demo-site-staging... ✅
  [3/8] Deleting my-old-project... ✅
  ...
  
✅ Deleted 8/8 buckets successfully
```

### Multi-Region Cleanup

The script targets your configured region (default: EU-WEST-PAR). To clean all regions:

```python
# Custom script for all regions (EVEN MORE DANGEROUS)
from estafettes.ovh import OVHEstafette

regions = ["EU-WEST-PAR", "GRA", "RBX", "SBG"]
for region in regions:
    print(f"🌍 Cleaning {region}...")
    # Use the delete_all_buckets.py script per region
```

### 🛡️ Safety Features

- **Date Verification**: Must type exact current date
- **Double Confirmation**: Two separate confirmation steps
- **No Accidents**: Cannot be run accidentally or in batch
- **Progress Tracking**: Shows which buckets are being deleted
- **Error Handling**: Continues if some deletions fail

### ⚠️ Critical Warnings

!!! danger "Data Loss Warning"
    **THIS ACTION CANNOT BE UNDONE!** All bucket contents will be permanently deleted. There is no recovery mechanism.

!!! danger "Production Safety"
    **NEVER use this in production environments.** This is intended only for development/testing cleanup scenarios.

!!! danger "Backup First"
    **Always backup important data** before running this script, even in development environments.

## Email Models Reference

::: estafettes.brevo.models.Email
    options:
      show_root_heading: false
      show_source: false

## API Notes

!!! note "Brevo API Key"
    The API key is required when initializing BrevoEstafette. You can pass it directly or load it from environment variables.

!!! note "Template Directory"
    When using templates (`template_name` and `context`), you must explicitly provide the `template_dir` parameter.

!!! note "OVH Credentials"
    OVH credentials are discovered automatically in this order:
    1. Direct parameters to OVHEstafette
    2. Environment variables (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
    3. rclone.conf file (multiple search paths)

!!! tip "Static Website Hosting"
    When deploying static websites, the `--static-website` flag automatically:
    - Flattens directory structure to root
    - Sets public-read ACL on bucket and objects
    - Configures index.html and error.html documents
    - Applies appropriate CORS policies

!!! tip "Dry-Run Mode"
    Always use `--dry-run` first to preview changes before deploying to production buckets.

