#!/usr/bin/env python3
"""Test runner for estafettes with bucket cleanup management."""

import sys
import os
import argparse
from pathlib import Path
import unittest

# Add src directory to Python path
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

# Auto-enable live tests if rclone.conf is present
if Path("rclone.conf").exists():
    os.environ.setdefault("OVH_LIVE_TESTS", "true")


def main():
    """Run tests with optional bucket preservation."""
    parser = argparse.ArgumentParser(description="Run estafettes test suite")
    parser.add_argument(
        "--dont-delete-created-test-buckets",
        action="store_true",
        help="Preserve test buckets after completion (for inspection)",
    )
    parser.add_argument(
        "--pattern", default="test_*.py", help="Test file pattern (default: test_*.py)"
    )
    parser.add_argument(
        "--verbosity", type=int, default=2, help="Test verbosity level (default: 2)"
    )

    args = parser.parse_args()

    # Import bucket tracking utilities
    from _utils import disable_cleanup, console

    # Configure bucket cleanup
    if args.dont_delete_created_test_buckets:
        disable_cleanup()
        console.print("🛡️ Test buckets will be preserved for inspection")
    else:
        console.print("🧹 Test buckets will be automatically cleaned up")

    # Discover and run tests
    tests_root = Path(__file__).parent
    suite = unittest.defaultTestLoader.discover(start_dir=str(tests_root), pattern=args.pattern)

    runner = unittest.TextTestRunner(verbosity=args.verbosity)
    result = runner.run(suite)

    # Show final bucket status
    from _utils import get_tracked_buckets

    tracked = get_tracked_buckets()
    if tracked:
        console.print(f"\n📊 Test created {len(tracked)} buckets: {', '.join(tracked)}")

    sys.exit(not result.wasSuccessful())


if __name__ == "__main__":
    main()
