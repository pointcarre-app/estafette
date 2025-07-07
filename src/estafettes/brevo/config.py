"""Configuration module for the Estafettes Brevo integration.

This module provides configuration setup for the Brevo (formerly SendInBlue) API.
It handles API key configuration and client setup.
"""

from sib_api_v3_sdk import Configuration


def get_sib_configuration(api_key: str) -> Configuration:
    """Get the Brevo (formerly SendInBlue) API configuration.

    Sets up the configuration with the provided API key.

    Args:
        api_key (str): The Brevo API key.

    Returns:
        Configuration: Configured Brevo API configuration object.
    """
    # NOTE mad: see https://github.com/sendinblue/APIv3-python-library#installation--usage
    configuration = Configuration()
    configuration.api_key["api-key"] = api_key
    return configuration
