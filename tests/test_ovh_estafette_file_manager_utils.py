from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from estafettes.ovh.config import OVHConfig
from estafettes.ovh.file_manager import FileManager


class TestFileManagerHelpers(unittest.TestCase):
    """Unit tests for FileManager internal path helpers (offline)."""

    def setUp(self) -> None:  # noqa: D401
        self.fm = FileManager(OVHConfig())

    def test_clean_file_path(self) -> None:
        self.assertEqual(self.fm._clean_file_path("/foo/bar"), "foo/bar")
        self.assertEqual(self.fm._clean_file_path("foo/bar"), "foo/bar")

    def test_build_remote_key_regular(self) -> None:
        root = Path("/root")
        local = root / "dir" / "file.txt"
        key = self.fm._build_remote_key(local, root, "uploads", static_website=False)
        self.assertEqual(key, "uploads/dir/file.txt")

    def test_build_remote_key_static_website(self) -> None:
        root = Path("/root")
        local = root / "dir" / "file.txt"
        key = self.fm._build_remote_key(local, root, "", static_website=True)
        self.assertEqual(key, "file.txt")

    def test_filter_files_excludes_hidden_and_patterns(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            p = Path(td)
            (p / ".DS_Store").write_text("x")
            (p / "visible.txt").write_text("y")
            (p / "__pycache__").mkdir()
            files = list((p).iterdir())
            kept = self.fm._filter_files(files)
            names = {f.name for f in kept}
            self.assertEqual(names, {"visible.txt"})


if __name__ == "__main__":
    unittest.main()
