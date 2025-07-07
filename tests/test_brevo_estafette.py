from __future__ import annotations

import os
import unittest
from pathlib import Path
from typing import List, Dict

from dotenv import load_dotenv

from estafettes.brevo.models import Email

TESTS_DIR = Path(__file__).parent


def _make_receivers() -> List[Dict[str, str]]:
    """Build list of receiver dicts from environment or fallback values."""
    # Support either modern CSV env vars or legacy single-receiver vars
    receiver_emails_env = os.getenv("RECEIVER_EMAILS") or os.getenv("RECEIVER_EMAIL")
    receiver_names_env = os.getenv("RECEIVER_NAMES") or os.getenv("RECEIVER_NAME")

    if not receiver_emails_env:
        raise RuntimeError(
            "RECEIVER_EMAILS or RECEIVER_EMAIL must be set in the environment/.env for tests."
        )

    receiver_emails = receiver_emails_env.split(",")
    receiver_names = receiver_names_env.split(",") if receiver_names_env else []
    receivers: List[Dict[str, str]] = []
    for idx, email in enumerate(receiver_emails):
        name = receiver_names[idx] if idx < len(receiver_names) else email.split("@")[0]
        receivers.append({"email": email.strip(), "name": name.strip()})
    return receivers


class TestBrevoEstafetteEmailModels(unittest.TestCase):
    """Unit-tests for BrevoEstafette Email model validation."""

    @classmethod
    def setUpClass(cls) -> None:  # noqa: D401  (simple name acceptable in tests)
        # Load .env once for all tests if present.
        env_path = Path(__file__).resolve().parent.parent / ".env"
        if env_path.exists():
            load_dotenv(env_path)

    # ------------------------------------------------------------------
    # Simple email tests
    # ------------------------------------------------------------------

    def test_simple_email_model(self) -> None:
        sender_email = os.getenv("SENDER_EMAIL", "sender@example.com")
        sender_name = os.getenv("SENDER_NAME", "Sender")

        data = {
            "sender": {"email": sender_email, "name": sender_name},
            "to": _make_receivers(),
            "subject": "Estafettes no-html",
            "body": "hello world",
            "attachment_sources": {"hello.txt": str(TESTS_DIR / "hello_world.txt")},
        }

        email = Email.model_validate(data)
        self.assertEqual(email.sender.email, sender_email)
        self.assertEqual(email.body, "hello world")
        self.assertGreaterEqual(len(email.to), 1)

    # ------------------------------------------------------------------
    # Template email tests
    # ------------------------------------------------------------------

    def test_template_email_model(self) -> None:
        sender_email = os.getenv("SENDER_EMAIL", "sender@example.com")
        sender_name = os.getenv("SENDER_NAME", "Sender")

        data = {
            "sender": {"email": sender_email, "name": sender_name},
            "to": _make_receivers(),
            "subject": "Estafettes template",
            "body": "fallback body",
            "template_dir": str(TESTS_DIR),
            "template_name": "template.html",
            "context": {
                "user_name": "Titi",
                "link": "https://example.com",
                "company_name": "Some Co",
            },
            "attachment_sources": {"hello.txt": str(TESTS_DIR / "hello_world.txt")},
        }

        email = Email.model_validate(data)
        self.assertEqual(email.template_dir, str(TESTS_DIR))
        self.assertEqual(email.template_name, "template.html")
        self.assertGreaterEqual(len(email.to), 1)

        # ----------------------------------------------------------------------------
        # Optional live send: uncomment the next two lines ONLY if you have set
        # SIB_API_KEY in your environment and really want to dispatch an email.
        # from estafettes.brevo import BrevoEstafette
        # BrevoEstafette(api_key=os.environ["SIB_API_KEY"]).send(email)
        # ----------------------------------------------------------------------------


if __name__ == "__main__":
    unittest.main()
