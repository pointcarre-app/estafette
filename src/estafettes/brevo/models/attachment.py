"""Attachment model for email sending.

This module provides the Attachment class for representing email attachments.
"""

import base64
import os
from pathlib import Path
from typing import Optional, Union

from pydantic import BaseModel, Field, model_validator
from sib_api_v3_sdk import SendSmtpEmailAttachment


class Attachment(BaseModel):
    """Represents an email attachment.

    This class handles attachments for emails, supporting both URL-based and file-based attachments.

    Attributes:
        name: Name of the attachment file.
        url: Absolute URL of the attachment, if it's a remote resource.
        content: Base64 encoded content of the attachment, if it's a local file.
    """

    name: str = Field(..., description="Name of the attachment file")
    url: Optional[str] = Field(None, description="Absolute URL of the attachment")
    content: Optional[str] = Field(None, description="Base64 encoded content")

    @model_validator(mode="after")
    def validate_exactly_one_soure(self):
        """Validates that either URL or content is present, but not both."""
        # TODO doctest
        # Examples:
        #     >>> # Neither URL nor content
        #     >>> Attachment(name="test.txt")
        #     Traceback (most recent call last):
        #     ...
        #     ValidationError: ...

        #     >>> # Both URL and content
        #     >>> Attachment(name="test.txt", url="http://example.com", content="base64data")
        #     Traceback (most recent call last):
        #     ...
        #         For further information visit https://errors.pydantic.dev/2.11/v/value_error"""

        if (self.url is None and self.content is None) or (
            self.url is not None and self.content is not None
        ):
            raise ValueError("Exactly one of url or content must be provided")
        return self

    @classmethod
    def from_url(cls, name: str, url: str):
        """Creates an attachment from a URL.

        Args:
            name: Name to use for the attachment.
            url: The URL where the attachment can be accessed.

        Returns:
            Attachment: A new Attachment instance with the URL.
        """
        return cls(name=name, url=url, content=None)

    @classmethod
    def from_file(cls, name: str, file_path: str):
        """Creates an attachment from a local file.

        Args:
            name: Name to use for the attachment.
            file_path: Path to the local file.

        Returns:
            Attachment: A new Attachment instance with the file content encoded in base64.
        """
        with open(file_path, "rb") as file:
            content = base64.b64encode(file.read()).decode("utf-8")
        return cls(name=name, content=content, url=None)

    @classmethod
    def from_source(cls, name: str, source: Union[str, Path]) -> "Attachment":
        """Creates an attachment from either a URL or a local file path.

        Args:
            name: Name to use for the attachment.
            source: Either a URL or a local file path.

        Returns:
            Attachment: A new Attachment instance.

        Raises:
            ValueError: If the source is neither a valid URL nor a valid file path.
        """
        source_str = str(source)

        if source_str.startswith(("http://", "https://")):
            return Attachment.from_url(name=name, url=source_str)
        elif os.path.isfile(source_str):
            return Attachment.from_file(name=name, file_path=source_str)
        else:
            raise ValueError(f"Invalid attachment source: {source_str}")

    def to_brevo(self):
        """Converts the attachment to a Brevo-compatible format.

        Returns:
            SendSmtpEmailAttachment: The attachment formatted for the Brevo API.
        """
        return SendSmtpEmailAttachment(name=self.name, url=self.url, content=self.content)
