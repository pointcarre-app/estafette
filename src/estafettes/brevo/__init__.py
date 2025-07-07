"""Brevo-specific implementation of the Estafettes email delivery system.

This module contains the BrevoEstafette class and related functionality for
interacting with the Brevo (SendInBlue) API.
"""

from sib_api_v3_sdk import (
    TransactionalEmailsApi,
    ApiClient,
    AccountApi,
)

import dotenv
from rich.console import Console

from estafettes.brevo.models import Email
from estafettes.brevo.config import get_sib_configuration

############### GLOBALS


# TODO: selim : do we need that ?
dotenv.load_dotenv()


class BrevoEstafette:
    """Main service class for interacting with the Brevo (SendInBlue) API.

    This class provides methods to access account information and send transactional emails
    through the Brevo API.

    Attributes:
        configuration (Configuration): The Brevo API configuration.
        client (ApiClient): The Brevo API client instance.
    """

    console = Console()

    def __init__(self, api_key: str) -> None:
        """Initialize the BrevoEstafette client.

        Args:
            api_key (str): The Brevo API key.
        """
        self.configuration = get_sib_configuration(api_key)
        self.client = ApiClient(self.configuration)

    @property
    def account(self) -> dict:
        """Get account information from Brevo.

        Returns:
            dict: Account information from the Brevo API.
        """
        api_instance = AccountApi(self.client)
        return api_instance.get_account()

    def send(self, email: Email) -> None:
        """Send a transactional email through Brevo.

        Args:
            email (Email): The email object containing all necessary information
                to send an email.

        Returns:
            None: This method doesn't return anything but logs the request and response.
        """
        api_instance = TransactionalEmailsApi(
            api_client=self.client,
        )

        send_smtp_email = email.to_brevo()
        self.console.log(send_smtp_email)
        api_response = api_instance.send_transac_email(send_smtp_email)
        self.console.log(api_response)
