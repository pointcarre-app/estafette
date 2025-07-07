"""
CORS configuration presets for different deployment scenarios.

This module provides predefined CORS settings for common use cases:
- Website hosting (public sites)
- API assets (restricted domains)
- CDN assets (optimized for performance)
- Development (localhost-friendly)
"""

from typing import List
from estafettes.ovh.models import CORSSettings


class CORSConfigurations:
    """Predefined CORS configurations for different use cases."""

    @staticmethod
    def website_hosting() -> CORSSettings:
        """
        Standard website hosting CORS.

        Suitable for:
        - Public websites
        - Marketing sites
        - Documentation sites

        Features:
        - Allows all origins (*)
        - Read-only methods
        - Long cache duration
        """
        return CORSSettings(
            allowed_origins=["*"],  # Allow all origins for public sites
            allowed_methods=["GET", "HEAD"],
            allowed_headers=["*"],
            expose_headers=["ETag", "Content-Length", "Content-Type"],
            max_age=86400,  # 24 hours cache
        )

    @staticmethod
    def api_assets(allowed_domains: List[str]) -> CORSSettings:
        """
        CORS for API assets with specific domains.

        Suitable for:
        - Web applications
        - SPA frontends
        - Mobile app assets

        Args:
            allowed_domains: List of allowed origin domains

        Features:
        - Restricted to specific domains
        - Supports API methods
        - Shorter cache for flexibility
        """
        return CORSSettings(
            allowed_origins=allowed_domains,
            allowed_methods=["GET", "HEAD", "POST", "PUT"],
            allowed_headers=[
                "Authorization",
                "Content-Type",
                "X-API-Key",
                "X-Requested-With",
                "Accept",
                "Origin",
            ],
            expose_headers=["ETag", "Content-Length", "Content-Type", "X-RateLimit-Remaining"],
            max_age=3600,  # 1 hour cache
        )

    @staticmethod
    def cdn_assets() -> CORSSettings:
        """
        CORS for CDN/asset hosting.

        Suitable for:
        - Static assets (images, CSS, JS)
        - Public file hosting
        - Content delivery

        Features:
        - Open access for assets
        - Optimized for caching
        - Range request support
        """
        return CORSSettings(
            allowed_origins=["*"],
            allowed_methods=["GET", "HEAD"],
            allowed_headers=["Range", "If-Modified-Since", "If-None-Match", "Accept"],
            expose_headers=[
                "Content-Length",
                "Content-Type",
                "Last-Modified",
                "ETag",
                "Accept-Ranges",
            ],
            max_age=604800,  # 1 week cache for assets
        )

    @staticmethod
    def development(local_ports: List[int] = None) -> CORSSettings:
        """
        Development-friendly CORS.

        Suitable for:
        - Local development
        - Testing environments
        - Staging with various ports

        Args:
            local_ports: List of local ports to allow (default: [3000, 3001, 8000, 8080])

        Features:
        - Localhost origins
        - All methods allowed
        - Short cache for rapid iteration
        """
        if local_ports is None:
            local_ports = [3000, 3001, 8000, 8080, 9000]

        origins = ["http://localhost", "http://127.0.0.1", "https://localhost", "https://127.0.0.1"]

        # Add specific ports
        for port in local_ports:
            origins.extend(
                [
                    f"http://localhost:{port}",
                    f"http://127.0.0.1:{port}",
                    f"https://localhost:{port}",
                    f"https://127.0.0.1:{port}",
                ]
            )

        return CORSSettings(
            allowed_origins=origins,
            allowed_methods=["GET", "HEAD", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
            allowed_headers=["*"],
            expose_headers=["*"],
            max_age=300,  # 5 minutes cache for rapid development
        )

    @staticmethod
    def secure_api(allowed_domains: List[str]) -> CORSSettings:
        """
        High-security CORS for sensitive APIs.

        Suitable for:
        - Admin panels
        - Financial applications
        - Healthcare apps

        Args:
            allowed_domains: Strictly controlled list of allowed domains

        Features:
        - Very restrictive origins
        - Limited methods
        - Specific headers only
        - Short cache duration
        """
        return CORSSettings(
            allowed_origins=allowed_domains,  # No wildcards allowed
            allowed_methods=["GET", "HEAD"],  # Read-only by default
            allowed_headers=["Authorization", "Content-Type", "X-CSRF-Token", "X-Requested-With"],
            expose_headers=["Content-Type", "Content-Length"],
            max_age=600,  # 10 minutes cache only
        )

    @staticmethod
    def mobile_app_assets(app_domains: List[str]) -> CORSSettings:
        """
        CORS optimized for mobile app asset loading.

        Suitable for:
        - React Native apps
        - Ionic apps
        - Cordova/PhoneGap apps

        Args:
            app_domains: List of app domains and localhost for development

        Features:
        - Mobile-friendly headers
        - Caching optimized for mobile
        - Support for app protocols
        """
        # Add common mobile development origins
        mobile_origins = app_domains + [
            "http://localhost",
            "https://localhost",
            "file://",
            "ionic://localhost",
            "http://localhost:8100",  # Ionic default
            "capacitor://localhost",  # Capacitor apps
        ]

        return CORSSettings(
            allowed_origins=mobile_origins,
            allowed_methods=["GET", "HEAD", "POST"],
            allowed_headers=[
                "Content-Type",
                "Authorization",
                "X-Requested-With",
                "Accept",
                "Origin",
                "User-Agent",
            ],
            expose_headers=["Content-Length", "Content-Type", "ETag"],
            max_age=7200,  # 2 hours cache for mobile efficiency
        )


class CORSTemplates:
    """Common CORS configuration templates with sensible defaults."""

    @staticmethod
    def for_react_app(production_domains: List[str]) -> dict:
        """CORS configurations for a typical React application across environments."""
        return {
            "development": CORSConfigurations.development([3000, 3001]),
            "staging": CORSConfigurations.api_assets(
                [f"https://staging.{domain}" for domain in production_domains]
            ),
            "production": CORSConfigurations.api_assets(
                [f"https://{domain}" for domain in production_domains]
                + [f"https://www.{domain}" for domain in production_domains]
            ),
        }

    @staticmethod
    def for_vue_app(production_domains: List[str]) -> dict:
        """CORS configurations for a typical Vue application across environments."""
        return {
            "development": CORSConfigurations.development([8080, 8081]),
            "staging": CORSConfigurations.api_assets(
                [f"https://staging.{domain}" for domain in production_domains]
            ),
            "production": CORSConfigurations.api_assets(
                [f"https://{domain}" for domain in production_domains]
                + [f"https://www.{domain}" for domain in production_domains]
            ),
        }

    @staticmethod
    def for_static_site(domains: List[str]) -> dict:
        """CORS configurations for static websites (Jekyll, Hugo, etc.)."""
        return {
            "development": CORSConfigurations.development([4000, 1313]),  # Jekyll, Hugo defaults
            "staging": CORSConfigurations.website_hosting(),
            "production": CORSConfigurations.website_hosting(),
        }
