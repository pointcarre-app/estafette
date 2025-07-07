#!/usr/bin/env python3
"""
Working deployment system tests - focused on CORS functionality.

This tests the parts of the deployment system that actually work.
"""

import unittest
import sys
from pathlib import Path
import unittest.mock as mock

# Add paths
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent))

# Mock problematic modules before any imports
sys.modules["estafettes.ovh"] = mock.MagicMock()
sys.modules["estafettes.ovh.models"] = mock.MagicMock()


# Create a working mock for CORSSettings
class WorkingCORSSettings:
    def __init__(
        self,
        allowed_origins=None,
        allowed_methods=None,
        allowed_headers=None,
        expose_headers=None,
        max_age=300,
    ):
        self.allowed_origins = allowed_origins or []
        self.allowed_methods = allowed_methods or []
        self.allowed_headers = allowed_headers or []
        self.expose_headers = expose_headers or []
        self.max_age = max_age


# Set up the mock properly
sys.modules["estafettes.ovh.models"].CORSSettings = WorkingCORSSettings

# Now import the working modules
from deploy.cors_configs import CORSConfigurations, CORSTemplates


class TestWorkingCORSConfigurations(unittest.TestCase):
    """Test CORS configurations that actually work."""

    def test_development_cors_basic(self):
        """Test basic development CORS configuration."""
        cors = CORSConfigurations.development()

        # Check it's the right type
        self.assertIsInstance(cors, WorkingCORSSettings)

        # Check it has localhost origins
        self.assertGreater(len(cors.allowed_origins), 10)
        self.assertIn("http://localhost:3000", cors.allowed_origins)
        self.assertIn("https://localhost:3000", cors.allowed_origins)

        # Check methods include common ones
        self.assertIn("GET", cors.allowed_methods)
        self.assertIn("POST", cors.allowed_methods)

        # Check reasonable cache time
        self.assertEqual(cors.max_age, 300)

    def test_development_cors_custom_ports(self):
        """Test development CORS with custom ports."""
        custom_ports = [4000, 5000]
        cors = CORSConfigurations.development(custom_ports)

        # Check custom ports are included
        self.assertIn("http://localhost:4000", cors.allowed_origins)
        self.assertIn("https://localhost:5000", cors.allowed_origins)

    def test_api_assets_cors(self):
        """Test API assets CORS configuration."""
        domains = ["https://myapp.com", "https://api.myapp.com"]
        cors = CORSConfigurations.api_assets(domains)

        # Check domains are set correctly
        self.assertEqual(cors.allowed_origins, domains)

        # Check API-appropriate methods
        self.assertIn("GET", cors.allowed_methods)
        self.assertIn("POST", cors.allowed_methods)
        self.assertIn("PUT", cors.allowed_methods)

        # Check longer cache time for API
        self.assertEqual(cors.max_age, 3600)

    def test_website_hosting_cors(self):
        """Test website hosting CORS configuration."""
        cors = CORSConfigurations.website_hosting()

        # Check wildcard origin for public website
        self.assertEqual(cors.allowed_origins, ["*"])

        # Check read-only methods for static site
        self.assertEqual(cors.allowed_methods, ["GET", "HEAD"])

        # Check long cache time
        self.assertEqual(cors.max_age, 86400)

    def test_cdn_assets_cors(self):
        """Test CDN assets CORS configuration."""
        cors = CORSConfigurations.cdn_assets()

        # Check wildcard for public assets
        self.assertEqual(cors.allowed_origins, ["*"])

        # Check read-only methods
        self.assertEqual(cors.allowed_methods, ["GET", "HEAD"])

        # Check very long cache time
        self.assertEqual(cors.max_age, 604800)  # 1 week

    def test_secure_api_cors(self):
        """Test secure API CORS configuration."""
        domains = ["https://secure.myapp.com"]
        cors = CORSConfigurations.secure_api(domains)

        # Check restricted origins
        self.assertEqual(cors.allowed_origins, domains)

        # Check read-only for security
        self.assertEqual(cors.allowed_methods, ["GET", "HEAD"])

        # Check short cache time for security
        self.assertEqual(cors.max_age, 600)

    def test_mobile_app_assets_cors(self):
        """Test mobile app assets CORS configuration."""
        app_domains = ["https://myapp.com"]
        cors = CORSConfigurations.mobile_app_assets(app_domains)

        # Check app domains are included
        for domain in app_domains:
            self.assertIn(domain, cors.allowed_origins)

        # Check mobile-specific origins
        self.assertIn("http://localhost", cors.allowed_origins)
        self.assertIn("file://", cors.allowed_origins)
        self.assertIn("ionic://localhost", cors.allowed_origins)
        self.assertIn("capacitor://localhost", cors.allowed_origins)

        # Check mobile-appropriate cache time
        self.assertEqual(cors.max_age, 7200)


class TestWorkingCORSTemplates(unittest.TestCase):
    """Test CORS templates that actually work."""

    def test_react_app_template(self):
        """Test React app CORS template."""
        domains = ["myapp.com", "example.com"]
        templates = CORSTemplates.for_react_app(domains)

        # Check all environments present
        self.assertEqual(set(templates.keys()), {"development", "staging", "production"})

        # Check development has React ports
        dev_cors = templates["development"]
        self.assertIn("http://localhost:3000", dev_cors.allowed_origins)
        self.assertIn("http://localhost:3001", dev_cors.allowed_origins)

        # Check staging has staging domains
        staging_cors = templates["staging"]
        for domain in domains:
            self.assertIn(f"https://staging.{domain}", staging_cors.allowed_origins)

        # Check production has production domains
        prod_cors = templates["production"]
        for domain in domains:
            self.assertIn(f"https://{domain}", prod_cors.allowed_origins)
            self.assertIn(f"https://www.{domain}", prod_cors.allowed_origins)

    def test_vue_app_template(self):
        """Test Vue app CORS template."""
        domains = ["vueapp.com"]
        templates = CORSTemplates.for_vue_app(domains)

        # Check all environments present
        self.assertEqual(set(templates.keys()), {"development", "staging", "production"})

        # Check Vue-specific development ports
        dev_cors = templates["development"]
        self.assertIn("http://localhost:8080", dev_cors.allowed_origins)
        self.assertIn("http://localhost:8081", dev_cors.allowed_origins)

    def test_static_site_template(self):
        """Test static site CORS template."""
        domains = ["staticsite.com"]
        templates = CORSTemplates.for_static_site(domains)

        # Check all environments present
        self.assertEqual(set(templates.keys()), {"development", "staging", "production"})

        # Check static site development ports
        dev_cors = templates["development"]
        self.assertIn("http://localhost:4000", dev_cors.allowed_origins)  # Jekyll
        self.assertIn("http://localhost:1313", dev_cors.allowed_origins)  # Hugo

        # Check staging and production use wildcard for static sites
        self.assertEqual(templates["staging"].allowed_origins, ["*"])
        self.assertEqual(templates["production"].allowed_origins, ["*"])

    def test_template_structure_consistency(self):
        """Test that all templates have consistent structure."""
        test_domains = ["test.com"]

        templates = [
            CORSTemplates.for_react_app(test_domains),
            CORSTemplates.for_vue_app(test_domains),
            CORSTemplates.for_static_site(test_domains),
        ]

        for template in templates:
            # All should have the same environment keys
            self.assertEqual(set(template.keys()), {"development", "staging", "production"})

            # All values should be WorkingCORSSettings
            for env, cors in template.items():
                self.assertIsInstance(cors, WorkingCORSSettings)

    def test_empty_domains_template(self):
        """Test templates with empty domains list."""
        empty_domains = []

        # Should not raise errors
        react_template = CORSTemplates.for_react_app(empty_domains)
        vue_template = CORSTemplates.for_vue_app(empty_domains)
        static_template = CORSTemplates.for_static_site(empty_domains)

        # Development should still work (has localhost)
        self.assertIsInstance(react_template["development"], WorkingCORSSettings)
        self.assertIsInstance(vue_template["development"], WorkingCORSSettings)
        self.assertIsInstance(static_template["development"], WorkingCORSSettings)


class TestCORSEdgeCases(unittest.TestCase):
    """Test edge cases for CORS configurations."""

    def test_empty_domains_api_assets(self):
        """Test API assets with empty domains."""
        cors = CORSConfigurations.api_assets([])
        self.assertEqual(cors.allowed_origins, [])

    def test_duplicate_domains(self):
        """Test handling of duplicate domains."""
        domains = ["https://myapp.com", "https://myapp.com"]
        cors = CORSConfigurations.api_assets(domains)
        self.assertEqual(cors.allowed_origins, domains)  # Should preserve duplicates

    def test_mixed_protocol_domains(self):
        """Test domains with mixed protocols."""
        domains = ["http://dev.com", "https://prod.com"]
        cors = CORSConfigurations.api_assets(domains)

        for domain in domains:
            self.assertIn(domain, cors.allowed_origins)

    def test_special_characters_in_domains(self):
        """Test domains with special characters."""
        domains = ["https://my-app.com", "https://my_app.com", "https://my.app.com"]
        cors = CORSConfigurations.api_assets(domains)

        for domain in domains:
            self.assertIn(domain, cors.allowed_origins)


if __name__ == "__main__":
    print("🧪 Running focused CORS tests...")

    # Set up unittest to be less verbose
    unittest.main(verbosity=2, buffer=True)
