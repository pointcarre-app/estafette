"""
Basic test to verify deployment system imports and core functionality.
"""

import unittest
import sys
from pathlib import Path

# Add both src and current directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent))

# Mock the modules before importing deploy modules
import unittest.mock as mock

# Mock the OVH modules to avoid import errors
sys.modules["estafettes.ovh"] = mock.MagicMock()
sys.modules["estafettes.ovh.models"] = mock.MagicMock()


class TestBasicImports(unittest.TestCase):
    """Test basic imports work correctly."""

    def test_cors_configs_import(self):
        """Test that CORS configurations can be imported."""
        from deploy.cors_configs import CORSConfigurations, CORSTemplates

        # Test that classes are available
        self.assertTrue(hasattr(CORSConfigurations, "development"))
        self.assertTrue(hasattr(CORSTemplates, "for_react_app"))

    def test_cors_configurations_mock(self):
        """Test CORS configurations with mocked dependencies."""
        from deploy.cors_configs import CORSConfigurations

        # This should work with mocked models
        cors = CORSConfigurations.development()
        self.assertIsNotNone(cors)

    def test_cors_templates_mock(self):
        """Test CORS templates with mocked dependencies."""
        from deploy.cors_configs import CORSTemplates

        # This should work with mocked models
        templates = CORSTemplates.for_react_app(["example.com"])
        self.assertIsNotNone(templates)
        self.assertIn("development", templates)
        self.assertIn("staging", templates)
        self.assertIn("production", templates)

    def test_argument_parser_import(self):
        """Test that argument parser functionality can be imported."""
        from deploy.deploy_script import setup_argument_parser

        parser = setup_argument_parser()
        self.assertIsNotNone(parser)

    def test_argument_parser_basic_args(self):
        """Test argument parser with basic arguments."""
        from deploy.deploy_script import setup_argument_parser

        parser = setup_argument_parser()

        # Test default arguments
        args = parser.parse_args([])
        self.assertEqual(args.env, "development")

        # Test environment argument
        args = parser.parse_args(["--env", "staging"])
        self.assertEqual(args.env, "staging")

    def test_validation_functions(self):
        """Test validation functions."""
        from deploy.deploy_script import validate_arguments

        # Mock args object
        args = mock.MagicMock()
        args.dry_run = False
        args.no_dry_run = False
        args.confirm = False
        args.no_confirm = False
        args.source = None
        args.assets = None
        args.docs = None
        args.deploy_all = False
        args.test_cors = True  # At least one operation
        args.list_buckets = False
        args.cleanup = False

        # Should return True for valid args
        result = validate_arguments(args)
        self.assertTrue(result)


class TestDirectCORSUsage(unittest.TestCase):
    """Test direct CORS configuration usage without OVH dependencies."""

    def test_development_cors_direct(self):
        """Test development CORS configuration directly."""
        from deploy.cors_configs import CORSConfigurations

        # Test with default ports
        cors = CORSConfigurations.development()
        self.assertIsNotNone(cors)

        # Test with custom ports
        cors = CORSConfigurations.development([4000, 5000])
        self.assertIsNotNone(cors)

    def test_api_assets_cors_direct(self):
        """Test API assets CORS configuration directly."""
        from deploy.cors_configs import CORSConfigurations

        domains = ["https://example.com", "https://api.example.com"]
        cors = CORSConfigurations.api_assets(domains)
        self.assertIsNotNone(cors)

    def test_react_template_direct(self):
        """Test React app template directly."""
        from deploy.cors_configs import CORSTemplates

        domains = ["example.com", "test.com"]
        templates = CORSTemplates.for_react_app(domains)

        self.assertIsNotNone(templates)
        self.assertIn("development", templates)
        self.assertIn("staging", templates)
        self.assertIn("production", templates)

    def test_vue_template_direct(self):
        """Test Vue app template directly."""
        from deploy.cors_configs import CORSTemplates

        domains = ["vueapp.com"]
        templates = CORSTemplates.for_vue_app(domains)

        self.assertIsNotNone(templates)
        self.assertIn("development", templates)
        self.assertIn("staging", templates)
        self.assertIn("production", templates)

    def test_static_site_template_direct(self):
        """Test static site template directly."""
        from deploy.cors_configs import CORSTemplates

        domains = ["staticsite.com"]
        templates = CORSTemplates.for_static_site(domains)

        self.assertIsNotNone(templates)
        self.assertIn("development", templates)
        self.assertIn("staging", templates)
        self.assertIn("production", templates)


if __name__ == "__main__":
    unittest.main(verbosity=2)
