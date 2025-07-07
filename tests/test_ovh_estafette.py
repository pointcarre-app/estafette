from __future__ import annotations

import os
import random
import string
import tempfile
import unittest
from pathlib import Path

from estafettes.ovh.config import OVHConfig
from estafettes.ovh.bucket_manager import BucketManager
from estafettes.ovh.file_manager import FileManager

from _utils import panel, track_bucket, untrack_bucket


def _random_suffix(length: int = 6) -> str:
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))


class IntegrationOVHBucketTests(unittest.TestCase):
    """Live tests against OVH Object Storage.

    These tests perform real network calls. They are skipped unless
    OVH_LIVE_TESTS=true is set in the environment *and* credentials are present.
    """

    @classmethod
    def setUpClass(cls) -> None:  # noqa: D401
        if os.getenv("OVH_LIVE_TESTS") != "true":
            raise unittest.SkipTest("Set OVH_LIVE_TESTS=true to enable live integration tests.")

        # Ensure rclone.conf exists
        conf_path = Path("rclone.conf")
        if not conf_path.exists():
            raise unittest.SkipTest(
                "rclone.conf not found – live tests require it for credentials."
            )

        cls.config = OVHConfig(config_file="rclone.conf")
        cls.bucket_manager = BucketManager(cls.config)
        cls.file_manager = FileManager(cls.config)

        cls.test_bucket = f"estafette-it-{_random_suffix()}"

        # Create bucket for the suite
        created = cls.bucket_manager.create_bucket(bucket_name=cls.test_bucket, acl="private")
        if not created:
            raise RuntimeError("Failed to create test bucket; aborting integration tests.")

        # Track the bucket for cleanup
        track_bucket(cls.test_bucket)

        panel(f"[bold]{cls.test_bucket}[/bold]", title="Integration Bucket", style="cyan")

    @classmethod
    def tearDownClass(cls) -> None:  # noqa: D401
        # Clean up bucket
        success = cls.bucket_manager.delete_bucket(bucket_name=cls.test_bucket, force=True)
        if success:
            # Remove from tracking since we successfully deleted it
            untrack_bucket(cls.test_bucket)

    # ------------------------------------------------------------------
    # Tests
    # ------------------------------------------------------------------

    def test_bucket_exists(self) -> None:
        self.assertTrue(self.bucket_manager.bucket_exists(self.test_bucket))

    def test_file_upload_and_list(self) -> None:
        # Create a temporary file to upload
        with tempfile.NamedTemporaryFile("w", delete=False) as tmp:
            tmp.write("hello ovh")
            tmp_path = Path(tmp.name)

        try:
            key = "test/hello.txt"
            uploaded = self.file_manager.upload_file(tmp_path, self.test_bucket, key)
            self.assertTrue(uploaded)

            files = self.file_manager.list_remote_files(self.test_bucket, prefix="test/")
            self.assertIn(key, files)

            metadata = self.file_manager.get_file_metadata(self.test_bucket, key)
            self.assertIsNotNone(metadata)

            # Show URL panel
            reg_cfg = self.config.get_region_config("EU-WEST-PAR")
            url = f"https://{self.test_bucket}.{reg_cfg.endpoint.replace('https://', '')}/{key}"
            panel(f"[link={url}]{url}[/link]", title="Uploaded File", style="cyan")
        finally:
            # Cleanup remote and local
            self.file_manager.delete_remote_file(self.test_bucket, key)
            tmp_path.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
