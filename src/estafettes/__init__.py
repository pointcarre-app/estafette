"""Estafettes: A streamlined email delivery system supporting multiple providers.

Estafettes provides a high-level interface for composing and sending emails
through various email service providers. Currently supports Brevo (SendInBlue).

The package offers intuitive models for creating emails with attachments,
managing senders and recipients, and handling the underlying API communication.

Features:
- Simple email composition with rich text support
- File and URL attachment handling
- Environment-based configuration using dotenv
- Seamless integration with multiple email APIs
- Type-safe models using Pydantic

Example:
    ```python
    from estafettes.brevo.models import Email, Sender, Recipient
    from estafettes.brevo import BrevoEstafette

    email = Email(
        to=Recipient(email="user@example.com", name="User Name"),
        sender=Sender(email="sender@example.com", name="Sender Name"),
        subject="Hello from Estafettes",
        body="This is a test email sent using Estafettes.",
        attachment_sources={"report.pdf": "/path/to/report.pdf"}
    )

    # Send the email using the Brevo client
    client = BrevoEstafette()
    client.send(email)
    ```
"""

# Import from the brevo subpackage
from estafettes.brevo import BrevoEstafette

# Import from the ovh subpackage
from estafettes.ovh import OVHEstafette

# Expose the main classes at the package level
__all__ = ["BrevoEstafette", "OVHEstafette"]
