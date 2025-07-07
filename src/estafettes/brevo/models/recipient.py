"""Recipient model for email sending.

This module provides the Recipient class for representing email recipients.
"""

from pydantic import BaseModel, EmailStr, Field
from sib_api_v3_sdk import SendSmtpEmailTo


class Recipient(BaseModel):
    """Represents the recipient of an email.

    Stores information about a recipient's email address and name.

    Attributes:
        email: Email address of the recipient.
        name: Name of the recipient.
    """

    email: EmailStr = Field(..., description="Email address of the recipient")
    name: str = Field(..., description="Name of the recipient")

    def to_brevo(self) -> SendSmtpEmailTo:
        """Convert to Brevo's SendSmtpEmailTo object.

        Returns:
            SendSmtpEmailTo: A Brevo API recipient object.
        """
        return SendSmtpEmailTo(email=self.email, name=self.name)
