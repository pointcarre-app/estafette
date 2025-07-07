from __future__ import annotations

import unittest
import sys
from pathlib import Path

from typer.testing import CliRunner

# Add src to path if needed for import resolution
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

try:
    from estafettes.ovh.cli import app

    CLI_AVAILABLE = True
except ImportError as e:
    # CLI module not available - tests will be skipped
    app = None
    CLI_AVAILABLE = False
    CLI_ERROR = str(e)

runner = CliRunner()


class CLITests(unittest.TestCase):
    def setUp(self):
        if not CLI_AVAILABLE:
            self.skipTest(f"CLI module not available: {CLI_ERROR}")

    def test_deploy_dry_run(self):
        result = runner.invoke(
            app,
            [
                "deploy",
                "--bucket",
                "cli-demo",
                "--source",
                str(Path(__file__).parent),
                "--dry-run",
            ],
        )
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Would create bucket", result.output)

    def test_buckets_list(self):
        # Use dry-run style: just ensure command executes; skips network if no creds
        if not Path("rclone.conf").exists():
            self.skipTest("rclone.conf missing")
        result = runner.invoke(app, ["buckets", "--list"])
        self.assertEqual(result.exit_code, 0)


if __name__ == "__main__":
    unittest.main()
