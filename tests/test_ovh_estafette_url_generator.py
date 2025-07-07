from __future__ import annotations

import unittest

from estafettes.ovh.config import OVHConfig
from estafettes.ovh.url_generator import URLGenerator


class URLGeneratorTests(unittest.TestCase):
    def setUp(self) -> None:  # noqa: D401
        self.cfg = OVHConfig()
        self.gen = URLGenerator(self.cfg)
        self.bucket = "mybucket"
        self.region = "EU-WEST-PAR"

    def test_direct_url(self):
        url = self.gen.generate_direct_url(self.bucket, "folder/file.txt", self.region)
        self.assertTrue(url.startswith("https://mybucket."))
        self.assertIn("/folder/file.txt", url)

    def test_website_url(self):
        url = self.gen.generate_website_url(self.bucket, "index.html", self.region)
        self.assertTrue(url.startswith("http://mybucket."))
        self.assertTrue(url.endswith("/index.html"))

    def test_generate_file_urls(self):
        files = ["a.txt", "b.txt"]
        urls = self.gen.generate_file_urls(self.bucket, files, self.region, static_website=True)
        self.assertEqual(len(urls), 2)
        self.assertIn("direct", urls[0])
        self.assertIn("website", urls[0])


if __name__ == "__main__":
    unittest.main()
