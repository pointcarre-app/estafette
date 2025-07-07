"""Sender model for email sending.

This module provides the Sender class for representing email senders.
"""

from pydantic import BaseModel, EmailStr, Field
from sib_api_v3_sdk import SendSmtpEmailSender


class Sender(BaseModel):
    """Represents the sender of an email.

    Stores information about a sender's email address and name.

    Attributes:
        email: Email address of the sender.
        name: Name of the sender.
    """

    email: EmailStr = Field(..., description="Email address of the sender")
    name: str = Field(..., description="Name of the sender")

    def to_brevo(self) -> SendSmtpEmailSender:
        """Convert to Brevo's SendSmtpEmailSender object.

        Returns:
            SendSmtpEmailSender: A Brevo API sender object.
        """
        return SendSmtpEmailSender(email=self.email, name=self.name)
