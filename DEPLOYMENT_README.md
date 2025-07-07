# OVH Deployment System using pca-estafette

A complete deployment solution for deploying applications to OVH Object Storage with comprehensive CORS management, multi-environment support, and safety features.

## 🚀 Quick Start

### 1. Installation

```bash
# Install pca-estafette in editable mode
pip install -e /path/to/your/pca-estafette

# Or install dependencies
pip install -r requirements-deploy.txt
```

### 2. Configuration

Set up your OVH credentials using either method:

**Option A: rclone.conf file**
```ini
[StorageS3]
type = s3
provider = Other
access_key_id = your-ovh-access-key
secret_access_key = your-ovh-secret-key
acl = public-read
bucket_acl = public-read
```

**Option B: Environment variables**
```bash
export AWS_ACCESS_KEY_ID=your-ovh-access-key
export AWS_SECRET_ACCESS_KEY=your-ovh-secret-key
```

### 3. Environment Setup

Copy the example environment file:
```bash
cp env.example .env
# Edit .env with your project settings
```

### 4. Deploy!

```bash
# Simple deployment to development
python deploy.py

# Deploy to staging
python deploy.py staging

# Deploy to production with dry-run
python deploy.py production --dry-run
```

## 📁 Project Structure

```
your-project/
├── deploy/                          # Deployment modules
│   ├── __init__.py                 # Package initialization
│   ├── cors_configs.py             # CORS configuration presets
│   ├── environments.py             # Environment management
│   └── deploy_script.py            # Main deployment script
├── deploy.py                       # Simple deployment entry point
├── example_usage.py                # Usage examples
├── requirements-deploy.txt         # Deployment dependencies
├── env.example                     # Environment configuration template
└── rclone.conf                     # OVH credentials (gitignored)
```

## 🎯 Usage Examples

### Simple Command-Line Deployment

```bash
# Deploy to development (default)
python deploy.py

# Deploy specific environment
python deploy.py staging
python deploy.py production

# Deploy with assets
python deploy.py staging --assets ./public/assets

# Deploy with confirmation
python deploy.py production --confirm

# Dry run first
python deploy.py production --dry-run
```

### Advanced Command-Line Options

```bash
# Full deployment script with all options
python deploy/deploy_script.py \
    --env staging \
    --source ./dist \
    --assets ./public/assets \
    --docs ./docs/_build/html \
    --cors-type api_assets \
    --cors-origins https://custom.domain.com \
    --region EU-WEST-PAR \
    --verbose

# Management operations
python deploy/deploy_script.py --test-cors --env staging
python deploy/deploy_script.py --list-buckets --env production
python deploy/deploy_script.py --cleanup --env development  # DANGEROUS!

# Multi-environment deployment
python deploy/deploy_script.py --deploy-all
python deploy/deploy_script.py --deploy-all --include-production
```

### Programmatic Usage

```python
from deploy import DeploymentManager, CORSConfigurations

# Simple deployment
manager = DeploymentManager("staging")
result = manager.deploy_frontend("./build")

# Custom configuration
custom_config = {
    "bucket_prefix": "myapp-prod",
    "region": "GRA",
    "cors_type": "secure_api",
    "domains": ["https://myapp.com", "https://www.myapp.com"],
    "require_confirmation": True,
    "dry_run_first": True
}

manager = DeploymentManager("production", custom_config)
result = manager.deploy_frontend("./build")

# Multi-asset deployment
manager.deploy_frontend("./build")
manager.deploy_assets("./public/assets")  
manager.deploy_docs("./docs/_build/html")

# CORS testing
manager.test_cors()
```

## 🔧 Configuration Options

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DEPLOY_ENV` | Default environment | `development` |
| `DEV_BUCKET_PREFIX` | Development bucket prefix | `myapp-dev` |
| `STAGING_BUCKET_PREFIX` | Staging bucket prefix | `myapp-staging` |
| `PROD_BUCKET_PREFIX` | Production bucket prefix | `myapp-prod` |
| `DEV_REGION` | Development region | `EU-WEST-PAR` |
| `STAGING_REGION` | Staging region | `EU-WEST-PAR` |
| `PROD_REGION` | Production region | `GRA` |
| `STAGING_DOMAIN` | Staging domain | `https://staging.myapp.com` |
| `PROD_DOMAIN` | Production domain | `https://myapp.com` |
| `PROD_WWW_DOMAIN` | Production www domain | `https://www.myapp.com` |

### Custom Configuration

```python
custom_config = {
    "bucket_prefix": "custom-prefix",
    "region": "EU-WEST-PAR",
    "cors_type": "api_assets",  # CORS configuration type
    "domains": ["https://example.com"],  # Allowed CORS origins
    "rclone_config": "custom-rclone.conf",  # Custom rclone config file
    "static_website": True,  # Enable static website hosting
    "require_confirmation": True,  # Ask for confirmation
    "dry_run_first": True  # Always dry run first
}
```

## 🌐 CORS Configuration Types

The system provides several predefined CORS configurations:

### `development`
```python
# Permissive CORS for local development
CORSConfigurations.development([3000, 3001, 8080])
```
- **Origins**: All localhost variations with specified ports
- **Methods**: All HTTP methods
- **Headers**: All headers allowed
- **Cache**: 5 minutes

### `api_assets`
```python
# Restricted CORS for web applications
CORSConfigurations.api_assets(["https://myapp.com"])
```
- **Origins**: Specific domains only
- **Methods**: GET, HEAD, POST, PUT
- **Headers**: Common API headers
- **Cache**: 1 hour

### `website_hosting`
```python
# Public website CORS
CORSConfigurations.website_hosting()
```
- **Origins**: All origins (*)
- **Methods**: GET, HEAD only
- **Headers**: All headers
- **Cache**: 24 hours

### `cdn_assets`
```python
# Optimized for static asset delivery
CORSConfigurations.cdn_assets()
```
- **Origins**: All origins (*)
- **Methods**: GET, HEAD
- **Headers**: Caching headers
- **Cache**: 1 week

### `secure_api`
```python
# High-security CORS for sensitive applications
CORSConfigurations.secure_api(["https://myapp.com"])
```
- **Origins**: Strictly controlled domains
- **Methods**: GET, HEAD only
- **Headers**: Essential headers only
- **Cache**: 10 minutes

### `mobile_app_assets`
```python
# Optimized for mobile app asset loading
CORSConfigurations.mobile_app_assets(["https://myapp.com"])
```
- **Origins**: App domains + mobile development origins
- **Methods**: GET, HEAD, POST
- **Headers**: Mobile-friendly headers
- **Cache**: 2 hours

## 🎨 CORS Templates

Pre-configured CORS for common application types:

```python
from deploy.cors_configs import CORSTemplates

# React application
cors_configs = CORSTemplates.for_react_app(["myapp.com"])
# Returns: {"development": ..., "staging": ..., "production": ...}

# Vue application  
cors_configs = CORSTemplates.for_vue_app(["myapp.com"])

# Static site (Jekyll, Hugo, etc.)
cors_configs = CORSTemplates.for_static_site(["myapp.com"])
```

## 🌍 Environment Configurations

### Development
- **Bucket Prefix**: `myapp-dev`
- **Region**: `EU-WEST-PAR`
- **CORS**: Permissive (all localhost)
- **Confirmation**: Not required
- **Dry Run**: Not required

### Staging  
- **Bucket Prefix**: `myapp-staging`
- **Region**: `EU-WEST-PAR`
- **CORS**: Restricted to staging domains
- **Confirmation**: Required
- **Dry Run**: Required

### Production
- **Bucket Prefix**: `myapp-prod`
- **Region**: `GRA` (different region)
- **CORS**: Highly restricted
- **Confirmation**: Required
- **Dry Run**: Required

## 🛡️ Safety Features

### Production Safeguards
- **Dry Run First**: Always preview changes before applying
- **Manual Confirmation**: Require explicit user confirmation  
- **Different Region**: Production uses different OVH region
- **Restrictive CORS**: Minimal CORS permissions for security

### Error Handling
- **Validation**: Comprehensive input validation
- **Graceful Failures**: Detailed error messages
- **Rollback Support**: Easy environment cleanup
- **Credential Security**: Automatic credential masking

## 📦 Deployment Types

### Frontend Deployment
```python
# React, Vue, Angular, etc.
manager.deploy_frontend("./build")
```
- Static website hosting enabled
- Custom CORS applied
- Website URL generated

### Assets Deployment  
```python
# Images, fonts, static files
manager.deploy_assets("./public/assets")
```
- CDN-optimized CORS
- No website hosting
- Direct file access URLs

### Documentation Deployment
```python
# Sphinx, MkDocs, etc.
manager.deploy_docs("./docs/_build/html")
```
- Website hosting enabled
- Public CORS configuration
- Documentation-friendly setup

## 🧪 Testing

### CORS Testing
```python
# Test CORS configuration
manager.test_cors()

# Test specific domains
manager.estafette.cors_manager.test_cors(
    bucket_name="myapp-staging-frontend",
    region="EU-WEST-PAR",
    origin="https://staging.myapp.com"
)
```

### Deployment Testing
```bash
# Always test with dry-run first
python deploy.py production --dry-run

# Test CORS after deployment
python deploy/deploy_script.py --test-cors --env staging
```

## 🗂️ Management Operations

### List Buckets
```bash
python deploy/deploy_script.py --list-buckets --env production
```

### Environment Cleanup
```bash
# ⚠️ DANGEROUS: Deletes all buckets for environment
python deploy/deploy_script.py --cleanup --env development
```

### Multi-Environment Management
```python
from deploy.environments import MultiEnvironmentManager

multi_manager = MultiEnvironmentManager()

# Deploy to all environments (skips production by default)
results = multi_manager.deploy_to_all("./build")

# Test CORS for all environments
cors_results = multi_manager.test_all_cors()
```

## 📋 Best Practices

### 1. Always Use Dry Run for Production
```bash
python deploy.py production --dry-run
```

### 2. Test CORS After Deployment
```bash
python deploy/deploy_script.py --test-cors --env staging
```

### 3. Use Environment-Specific Configurations
```python
# Different regions, CORS, and safety settings per environment
dev_config = {"region": "EU-WEST-PAR", "cors_type": "development"}
prod_config = {"region": "GRA", "cors_type": "secure_api"}
```

### 4. Secure Credential Management
```bash
# Use environment variables or gitignored rclone.conf
export AWS_ACCESS_KEY_ID=your-key
export AWS_SECRET_ACCESS_KEY=your-secret
```

### 5. Multi-Asset Strategy
```python
# Deploy different asset types to different buckets
manager.deploy_frontend("./build")       # Main application
manager.deploy_assets("./public/assets") # Static assets (CDN)
manager.deploy_docs("./docs/_build")     # Documentation
```

## 🔍 Troubleshooting

### Common Issues

**1. Authentication Errors**
```bash
❌ No valid credentials found
```
- Check your `rclone.conf` file
- Verify environment variables are set
- Ensure credentials have correct permissions

**2. CORS Failures**
```bash  
❌ CORS test failed for https://myapp.com
```
- Check domain spelling in configuration
- Verify bucket exists and is deployed
- Test with curl or browser dev tools

**3. Deployment Failures**
```bash
❌ Source directory not found: ./build
```
- Verify your build process completed
- Check source directory path
- Ensure files exist in the specified directory

### Debug Mode
```bash
# Enable verbose output
python deploy/deploy_script.py --verbose --env staging --source ./build

# Check bucket contents
python deploy/deploy_script.py --list-buckets --env staging
```

## 🚀 CI/CD Integration

### GitHub Actions Example
```yaml
name: Deploy to OVH
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
          
      - name: Install dependencies
        run: |
          pip install -r requirements-deploy.txt
          
      - name: Deploy to staging
        env:
          AWS_ACCESS_KEY_ID: ${{ secrets.OVH_ACCESS_KEY }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.OVH_SECRET_KEY }}
        run: |
          python deploy.py staging
          
      - name: Test CORS
        run: |
          python deploy/deploy_script.py --test-cors --env staging
```

## 📚 API Reference

### DeploymentManager
- `deploy_frontend(source_dir, bucket_suffix, dry_run_override)`
- `deploy_assets(source_dir, bucket_suffix, dry_run_override)`
- `deploy_docs(source_dir, bucket_suffix)`
- `test_cors(bucket_suffix)`
- `list_buckets()`
- `cleanup_environment(confirm)`

### CORSConfigurations
- `development(local_ports)`
- `api_assets(allowed_domains)`
- `website_hosting()`
- `cdn_assets()`
- `secure_api(allowed_domains)`
- `mobile_app_assets(app_domains)`

### MultiEnvironmentManager
- `deploy_to_all(source_dir, skip_production)`
- `test_all_cors()`

---

## 📄 License

MIT License - see your main project license for details.

## 🤝 Contributing

This deployment system is part of the pca-estafette project. Contributions welcome! 