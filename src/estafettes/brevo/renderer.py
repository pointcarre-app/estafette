"""HTML template rendering module for the Estafettes email delivery system.

This module provides HTML email template rendering using Jinja2. It handles
template loading, context injection, and HTML generation for email content.
"""

from typing import Dict, Any

from jinja2 import (
    Environment,
    FileSystemLoader,
    StrictUndefined,
)


class HtmlTemplateRenderer:
    """Render HTML email templates using Jinja2."""

    def __init__(self, template_directory: str) -> None:
        """Initialize with template directory.

        Args:
            template_directory (str): Path to the template directory.
        """
        self.env = Environment(
            loader=FileSystemLoader(template_directory),
            autoescape=True,  # Important for security
            undefined=StrictUndefined,
        )

    def render_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """Render a template with given context."""
        template = self.env.get_template(template_name)
        return template.render(**context)
