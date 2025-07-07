from __future__ import annotations

import os
import random
import string
import tempfile
import unittest
from pathlib import Path

from _utils import console, panel, track_bucket, untrack_bucket

from estafettes.ovh.ovh_estafette import OVHEstafette


def _rand_bucket() -> str:
    return f"estafette-demo-{''.join(random.choices(string.ascii_lowercase + string.digits, k=6))}"


class DemoDeployTests(unittest.TestCase):
    """Deploy two buckets (regular + static website) and print access URLs."""

    @classmethod
    def setUpClass(cls) -> None:  # noqa: D401
        if os.getenv("OVH_LIVE_TESTS") != "true":
            raise unittest.SkipTest("Set OVH_LIVE_TESTS=true to run deployment demo tests.")

        conf_path = Path("rclone.conf")
        if not conf_path.exists():
            raise unittest.SkipTest(
                "rclone.conf not found – live tests require it for credentials."
            )

        cls.estafette = OVHEstafette(
            config_file="rclone.conf", region="EU-WEST-PAR", console=console
        )

        # Prepare buckets
        cls.bucket_regular = _rand_bucket()
        cls.bucket_site = _rand_bucket()

        # Track buckets for cleanup
        track_bucket(cls.bucket_regular)
        track_bucket(cls.bucket_site)

        # Prepare test assets directory first
        cls.temp_dir = tempfile.TemporaryDirectory()
        html_path = Path(cls.temp_dir.name) / "test.html"
        html_path.write_text(
            "<html><body><h1>OVH Estafette Test</h1><script src='test.js'></script></body></html>"
        )

        js_path = Path(cls.temp_dir.name) / "test.js"
        js_path.write_text("console.log('OVH Estafette JS');")

        console.rule("[bold green]Deploy regular bucket")
        cls.estafette.deploy(
            bucket_name=cls.bucket_regular,
            source_dir=cls.temp_dir.name,
            static_website=False,
            skip_cors=True,
        )

        console.rule("[bold green]Deploy website bucket")
        cls.estafette.deploy(
            bucket_name=cls.bucket_site,
            source_dir=cls.temp_dir.name,
            static_website=True,
            skip_cors=False,
        )

        # Build URLs
        reg_cfg = cls.estafette.config.get_region_config(cls.estafette.region)
        endpoint_base = reg_cfg.endpoint.replace("https://", "")
        cls.url_regular_html = f"https://{cls.bucket_regular}.{endpoint_base}/test.html"
        cls.url_regular_js = f"https://{cls.bucket_regular}.{endpoint_base}/test.js"

        website_base = reg_cfg.website_suffix
        cls.url_website_http_html = f"http://{cls.bucket_site}.{website_base}/test.html"
        cls.url_website_http_js = f"http://{cls.bucket_site}.{website_base}/test.js"

    @classmethod
    def tearDownClass(cls) -> None:  # noqa: D401
        """Clean up created buckets and temporary directory."""
        console.rule("[bold yellow]Cleanup Deploy Test Resources")

        # Clean up buckets
        try:
            console.print(f"🗑️ Deleting bucket: {cls.bucket_regular}")
            success = cls.estafette.delete_bucket(cls.bucket_regular, force=True)
            if success:
                untrack_bucket(cls.bucket_regular)
        except Exception as e:
            console.print(f"❌ Failed to delete {cls.bucket_regular}: {e}")

        try:
            console.print(f"🗑️ Deleting bucket: {cls.bucket_site}")
            success = cls.estafette.delete_bucket(cls.bucket_site, force=True)
            if success:
                untrack_bucket(cls.bucket_site)
        except Exception as e:
            console.print(f"❌ Failed to delete {cls.bucket_site}: {e}")

        # Clean up temporary directory
        try:
            cls.temp_dir.cleanup()
        except Exception as e:
            console.print(f"❌ Failed to cleanup temp dir: {e}")

    def test_direct_html_url(self):
        panel(
            f"[link={self.url_regular_html}]{self.url_regular_html}[/link]",
            title="Direct HTML",
            style="cyan",
        )
        self.assertTrue(self.url_regular_html.startswith("https://"))

    def test_direct_js_url(self):
        panel(
            f"[link={self.url_regular_js}]{self.url_regular_js}[/link]",
            title="Direct JS",
            style="cyan",
        )
        self.assertTrue(self.url_regular_js.startswith("https://"))

    def test_website_html_url(self):
        panel(
            f"[link={self.url_website_http_html}]{self.url_website_http_html}[/link]",
            title="Website HTML",
            style="magenta",
        )
        self.assertTrue(self.url_website_http_html.startswith("http://"))

    def test_website_js_url(self):
        panel(
            f"[link={self.url_website_http_js}]{self.url_website_http_js}[/link]",
            title="Website JS",
            style="magenta",
        )
        self.assertTrue(self.url_website_http_js.startswith("http://"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
