from __future__ import annotations

import os
import random
import string
import unittest
from pathlib import Path

# Import only what we need to avoid Brevo dependencies
import sys

sys.path.append(str(Path(__file__).parent.parent / "src"))

from _utils import panel, track_bucket, untrack_bucket

from estafettes.ovh.config import OVHConfig
from estafettes.ovh.bucket_manager import BucketManager


def _random_suffix(length: int = 6) -> str:
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))


class BucketListingTests(unittest.TestCase):
    """Verify BucketManager.list_buckets works correctly."""

    @classmethod
    def setUpClass(cls) -> None:  # noqa: D401
        if os.getenv("OVH_LIVE_TESTS") != "true":
            raise unittest.SkipTest("Set OVH_LIVE_TESTS=true to enable live bucket listing test.")

        if not Path("rclone.conf").exists():
            raise unittest.SkipTest("rclone.conf not found – credentials required.")

        cfg = OVHConfig(config_file="rclone.conf")
        cls.manager = BucketManager(cfg)

    def test_list_buckets(self) -> None:
        """Test bucket listing by creating a bucket, listing, then cleaning up."""
        # Create a test bucket
        test_bucket = f"estafette-list-test-{_random_suffix()}"

        try:
            # Create and track the bucket
            created = self.manager.create_bucket(test_bucket, acl="private")
            self.assertTrue(created, "Failed to create test bucket")
            track_bucket(test_bucket)

            # List buckets and verify our bucket appears
            buckets = self.manager.list_buckets()
            bucket_names = [b.name for b in buckets]

            # Display the list
            panel("\n".join(bucket_names), title="Buckets", style="yellow")

            # Test that our bucket appears in the list
            self.assertIn(
                test_bucket, bucket_names, f"Test bucket {test_bucket} not found in bucket list"
            )

            # Test that list_buckets returns a list (basic functionality test)
            self.assertIsInstance(buckets, list, "list_buckets should return a list")

            # Test that each bucket has the expected attributes
            for bucket in buckets:
                self.assertTrue(hasattr(bucket, "name"), "Bucket should have name attribute")
                self.assertTrue(hasattr(bucket, "region"), "Bucket should have region attribute")
                self.assertIsInstance(bucket.name, str, "Bucket name should be a string")

        finally:
            # Clean up the test bucket
            try:
                success = self.manager.delete_bucket(test_bucket, force=True)
                if success:
                    untrack_bucket(test_bucket)
            except Exception as e:
                # Log the error but don't fail the test
                print(f"Warning: Failed to cleanup test bucket {test_bucket}: {e}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
