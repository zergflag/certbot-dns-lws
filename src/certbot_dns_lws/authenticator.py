from __future__ import annotations

import logging

from certbot import errors
from certbot.plugins import dns_common

from certbot_dns_lws.client import LwsDnsClient

LOGGER = logging.getLogger(__name__)


class Authenticator(dns_common.DNSAuthenticator):
    """Certbot DNS authenticator for LWS."""

    description = "Obtain certificates using an LWS DNS TXT record."

    ttl = 900

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.credentials = None

    @classmethod
    def add_parser_arguments(cls, add, default_propagation_seconds=300):
        super().add_parser_arguments(
            add,
            default_propagation_seconds=default_propagation_seconds,
        )

        add(
            "credentials",
            help="LWS credentials INI file.",
        )

    def more_info(self):
        return (
            "This plugin completes dns-01 challenges by creating TXT "
            "records through the LWS Client API."
        )

    def _setup_credentials(self):
        self.credentials = self._configure_credentials(
            "credentials",
            "LWS credentials INI file",
            {
                "login": "LWS account identifier",
                "api_key": "LWS API key",
            },
        )

    def _perform(self, domain: str, validation_name: str, validation: str):
        client = self._get_client()

        try:
            client.add_txt_record(
                fqdn=validation_name,
                value=validation,
                ttl=self.ttl,
            )
        except Exception as exc:
            raise errors.PluginError(
                f"Unable to create LWS TXT record {validation_name}: {exc}"
            ) from exc

    def _cleanup(self, domain: str, validation_name: str, validation: str):
        client = self._get_client()

        try:
            client.delete_txt_record(
                fqdn=validation_name,
                value=validation,
            )
        except Exception as exc:
            LOGGER.warning(
                "Unable to delete LWS TXT record %s: %s",
                validation_name,
                exc,
            )

    def _get_client(self) -> LwsDnsClient:
        if self.credentials is None:
            raise errors.PluginError("LWS credentials are not configured.")

        return LwsDnsClient(
            login=self.credentials.conf("login"),
            api_key=self.credentials.conf("api_key"),
        )
