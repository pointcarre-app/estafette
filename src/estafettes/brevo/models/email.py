"""Email model for email sending.

This module provides the Email class for representing email messages.
"""

from pathlib import Path
from typing import Any, Optional, List, Union, Dict

from pydantic import BaseModel, Field, model_validator
from sib_api_v3_sdk import SendSmtpEmail

from estafettes.brevo.renderer import HtmlTemplateRenderer
from estafettes.brevo.models.sender import Sender
from estafettes.brevo.models.recipient import Recipient
from estafettes.brevo.models.attachment import Attachment


class Email(BaseModel):
    """Represents an email message with sender, recipient, subject, and body.

    This class provides a high-level interface for creating email messages
    that can be sent through the Brevo API. It supports adding attachments
    from files or URLs, and HTML template rendering.

    Attributes:
        to: The recipient(s) of the email.
        sender: The sender of the email.
        subject: The subject line of the email.
        body: The text content of the email.
        template_name: Name of the HTML template file (optional).
        template_dir: Directory containing template files (required when using templates).
        context: Variables to pass to the template (optional).
        attachment_sources: Dictionary mapping filenames to file paths or URLs.
        attachments: List of Attachment objects generated from attachment_sources.

    Note:
        When using templates (template_name and context), template_dir must be explicitly
        provided. The library no longer falls back to environment variables for template
        directory resolution.

    Examples:
        >>> from estafettes.brevo.models import Email, Sender, Recipient
        >>> sender = Sender(email="jane@example.com", name="Jane")
        >>> recipient = Recipient(email="john@example.com", name="John")
        >>> email = Email(
        ...     to=recipient,
        ...     sender=sender,
        ...     subject="Hello",
        ...     body="World"
        ... )
        >>> email.subject
        'Hello'
        >>> email.sender.email
        'jane@example.com'
        >>> email.to[0].email
        'john@example.com'
        >>> email.attachments is None
        True
    """

    to: Union[Recipient, List[Recipient]] = Field(..., description="Recipient(s) of the email")
    sender: Sender = Field(..., description="Sender of the email")
    subject: str = Field(..., description="Field of the email")
    body: str = Field(..., description="Body of the email")
    template_name: Optional[str] = Field(None, description="Template name")
    template_dir: Optional[str] = Field(None, description="Template directory")
    context: Optional[Dict[str, Any]] = Field(None, description="Template context")
    attachment_sources: Optional[Dict[str, Union[str, Path]]] = Field(
        default=None,
        exclude=True,
        description="Dictionnay formatted as {'file.ext': 'path/to/file.ext'}",
    )

    attachments: Optional[List[Attachment]] = Field(None)
    html_content: Optional[str] = Field(None)

    @model_validator(mode="after")
    def validate_and_convert_to(self) -> "Email":
        """Ensures 'to' field is always a list of Recipients.

        If a single Recipient is provided, it will be wrapped in a list.

        Returns:
            Email: The validated Email model
        """
        if not isinstance(self.to, list):
            self.to = [self.to]
        return self

    def model_post_init(self, __context) -> None:
        """Post-initialization processing for the Email model.

        Converts attachment sources to Attachment objects if provided.

        Args:
            __context: Context information provided by Pydantic.

        Returns:
            None
        """
        if self.attachment_sources:
            self.attachments = []

            for name, source in self.attachment_sources.items():
                attachment = Attachment.from_source(name, source)
                self.attachments.append(attachment)

        if self.template_name and self.context:
            # template_dir is required when using templates
            if self.template_dir is None:
                raise ValueError(
                    "template_dir must be provided when using template_name and context"
                )
            renderer = HtmlTemplateRenderer(self.template_dir)
            self.html_content = renderer.render_template(self.template_name, self.context)

    def to_brevo(self) -> SendSmtpEmail:
        """Convert to Brevo's SendSmtpEmail object.

        Translates the Email model into a SendSmtpEmail object compatible with
        the Brevo API for sending emails.

        Returns:
            SendSmtpEmail: A Brevo API email object ready to be sent.
        """
        # At this point, self.to is guaranteed to be a list due to validate_and_convert_to
        recipients = self.to if isinstance(self.to, list) else [self.to]
        return SendSmtpEmail(
            to=[recipient.to_brevo() for recipient in recipients],
            sender=self.sender.to_brevo(),
            text_content=self.body,
            html_content=self.html_content,
            subject=self.subject,
            attachment=[attachment.to_brevo() for attachment in self.attachments]
            if self.attachments
            else None,
        )
