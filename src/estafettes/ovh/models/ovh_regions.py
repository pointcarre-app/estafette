from __future__ import annotations

from typing import Dict, List

from pydantic import BaseModel, Field

from .ovh_region_config import OVHRegionConfig


class OVHRegions(BaseModel):
    """All available OVH regions configuration."""

    regions: Dict[str, OVHRegionConfig] = Field(
        default_factory=lambda: {
            "EU-WEST-PAR": OVHRegionConfig(
                endpoint="https://s3.eu-west-par.io.cloud.ovh.net",
                website_suffix="s3-website.eu-west-par.io.cloud.ovh.net",
                region_code="eu-west-par",
                description="Europe (France - Paris)",
            ),
            "GRA": OVHRegionConfig(
                endpoint="https://s3.gra.io.cloud.ovh.net",
                website_suffix="s3-website.gra.io.cloud.ovh.net",
                region_code="gra",
                description="Europe (France - Gravelines)",
            ),
            "RBX": OVHRegionConfig(
                endpoint="https://s3.rbx.io.cloud.ovh.net",
                website_suffix="s3-website.rbx.io.cloud.ovh.net",
                region_code="rbx",
                description="Europe (France - Roubaix)",
            ),
            "SBG": OVHRegionConfig(
                endpoint="https://s3.sbg.io.cloud.ovh.net",
                website_suffix="s3-website.sbg.io.cloud.ovh.net",
                region_code="sbg",
                description="Europe (France - Strasbourg)",
            ),
            "DE": OVHRegionConfig(
                endpoint="https://s3.de.io.cloud.ovh.net",
                website_suffix="s3-website.de.io.cloud.ovh.net",
                region_code="de",
                description="Europe (Germany - Frankfurt)",
            ),
            "UK": OVHRegionConfig(
                endpoint="https://s3.uk.io.cloud.ovh.net",
                website_suffix="s3-website.uk.io.cloud.ovh.net",
                region_code="uk",
                description="Europe (United Kingdom - London)",
            ),
            "WAW": OVHRegionConfig(
                endpoint="https://s3.waw.io.cloud.ovh.net",
                website_suffix="s3-website.waw.io.cloud.ovh.net",
                region_code="waw",
                description="Europe (Poland - Warsaw)",
            ),
            "BHS": OVHRegionConfig(
                endpoint="https://s3.bhs.io.cloud.ovh.net",
                website_suffix="s3-website.bhs.io.cloud.ovh.net",
                region_code="bhs",
                description="North America (Canada - Beauharnois)",
            ),
            "CA-EAST-TOR": OVHRegionConfig(
                endpoint="https://s3.ca-east-tor.io.cloud.ovh.net",
                website_suffix="s3-website.ca-east-tor.io.cloud.ovh.net",
                region_code="ca-east-tor",
                description="North America (Canada - Toronto)",
            ),
            "SGP": OVHRegionConfig(
                endpoint="https://s3.sgp.io.cloud.ovh.net",
                website_suffix="s3-website.sgp.io.cloud.ovh.net",
                region_code="sgp",
                description="Asia-Pacific (Singapore)",
            ),
            "AP-SOUTHEAST-SYD": OVHRegionConfig(
                endpoint="https://s3.ap-southeast-syd.io.cloud.ovh.net",
                website_suffix="s3-website.ap-southeast-syd.io.cloud.ovh.net",
                region_code="ap-southeast-syd",
                description="Asia-Pacific (Australia - Sydney)",
            ),
            "AP-SOUTH-MUM": OVHRegionConfig(
                endpoint="https://s3.ap-south-mum.io.cloud.ovh.net",
                website_suffix="s3-website.ap-south-mum.io.cloud.ovh.net",
                region_code="ap-south-mum",
                description="Asia-Pacific (India - Mumbai)",
            ),
        }
    )

    def get_region(self, region_name: str) -> OVHRegionConfig:
        """Get region configuration by name."""
        if region_name not in self.regions:
            available = ", ".join(self.regions.keys())
            raise ValueError(f"Unknown region '{region_name}'. Available: {available}")
        return self.regions[region_name]

    def list_regions(self) -> List[str]:
        """List all available region names."""
        return list(self.regions.keys())
