"""URL generation for OVH buckets."""

from __future__ import annotations
from typing import List, Dict

from .config import OVHConfig


class URLGenerator:
    """Generates URLs for OVH bucket resources."""

    def __init__(self, config: OVHConfig) -> None:
        self.config = config

    # ------------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------------

    def generate_direct_url(
        self,
        bucket_name: str,
        file_path: str,
        region: str = "EU-WEST-PAR",
    ) -> str:
        bucket_name = self.config.validate_bucket_name(bucket_name)
        endpoint_host = self.config.get_region_config(region).endpoint.replace("https://", "")
        clean_path = self._clean_url_path(file_path)
        return f"https://{bucket_name}.{endpoint_host}/{clean_path}"

    def generate_website_url(
        self,
        bucket_name: str,
        file_path: str = "",
        region: str = "EU-WEST-PAR",
    ) -> str:
        bucket_name = self.config.validate_bucket_name(bucket_name)
        website_host = self.config.get_region_config(region).website_suffix
        clean_path = self._clean_url_path(file_path)
        base = f"http://{bucket_name}.{website_host}"
        return f"{base}/{clean_path}" if clean_path else base

    def generate_base_url(self, bucket_name: str, region: str = "EU-WEST-PAR") -> str:
        bucket_name = self.config.validate_bucket_name(bucket_name)
        host = self.config.get_region_config(region).endpoint.replace("https://", "")
        return f"https://{bucket_name}.{host}"

    def generate_file_urls(
        self,
        bucket_name: str,
        files: List[str],
        region: str = "EU-WEST-PAR",
        static_website: bool = False,
        source_dir: str = "",
    ) -> List[Dict[str, str]]:
        urls: List[Dict[str, str]] = []
        for file in files:
            direct = self.generate_direct_url(bucket_name, file, region)
            website = None
            if static_website:
                website = self.generate_website_url(bucket_name, file, region)
            urls.append({"file": file, "direct": direct, "website": website})
        return urls

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _clean_url_path(self, path: str) -> str:
        return path.lstrip("/")
