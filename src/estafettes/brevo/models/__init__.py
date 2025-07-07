"""Models package for Brevo email sending.

This package provides all the model classes for creating and sending emails
through the Brevo API.

Classes:
    Email: Represents an email with recipient, sender, subject, and body.
    Sender: Represents the sender of an email.
    Recipient: Represents the recipient of an email.
    Attachment: Represents an email attachment from a file or URL.
"""

from estafettes.brevo.models.email import Email
from estafettes.brevo.models.sender import Sender
from estafettes.brevo.models.recipient import Recipient
from estafettes.brevo.models.attachment import Attachment

__all__ = ["Email", "Sender", "Recipient", "Attachment"]
