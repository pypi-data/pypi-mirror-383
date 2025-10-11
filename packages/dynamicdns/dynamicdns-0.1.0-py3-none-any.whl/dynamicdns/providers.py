"""List of dynamic DNS providers."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Callable

import voluptuous as vol
from yarl import URL

from .const import (
    CONF_DOMAIN,
    CONF_HOST,
    CONF_IP_ADDRESS,
    CONF_IPV6_ADDRESS,
    CONF_PASSWORD,
    CONF_TOKEN,
    CONF_USERNAME,
)


class Provider(StrEnum):
    """Dynamic DNS providers."""

    DUCKDNS = "duckdns"
    MYTHICBEASTS_IPV4 = "mythicbeasts_ipv4"
    ANYDNS = "anydns"
    FREEDNS = "freedns"
    FREEDNS_IPV6 = "freedns_ipv6"


@dataclass(frozen=True, kw_only=True)
class ProviderConf:
    """Dynamic DNS provider config."""

    name: str
    base_url: str
    method: str = "GET"
    params: dict[str, str] = field(default_factory=dict)
    schema: vol.Schema
    success_fn: Callable[[str], bool] | None = None

    def render_url(self, data: dict[str, str]) -> URL:
        """Render the provider URL with given data and remove unused query parameters."""

        url = URL(self.base_url)
        url = url.with_path(url.path.format(**data))
        return url % {k: data[v] for k, v in self.params.items() if v in data}


providers: dict[Provider, ProviderConf] = {
    Provider.DUCKDNS: ProviderConf(
        name="Duck DNS",
        base_url="https://www.duckdns.org/update?verbose=true",
        params={
            "domains": CONF_HOST,
            "token": CONF_TOKEN,
            "ip": CONF_IP_ADDRESS,
            "ipv6": CONF_IPV6_ADDRESS,
        },
        schema=vol.Schema(
            {
                vol.Required(CONF_HOST): str,
                vol.Required(CONF_TOKEN): vol.All(str, vol.Length(min=36, max=36)),
            }
        ),
        success_fn=lambda x: x.startswith("OK"),
    ),
    Provider.MYTHICBEASTS_IPV4: ProviderConf(
        name="Mythic Beasts IPv4",
        base_url="https://ipv4.api.mythic-beasts.com/dns/v2/dynamic/{domain}",
        method="POST",
        params={"username": CONF_USERNAME, "password": CONF_PASSWORD},
        schema=vol.Schema(
            {
                vol.Required(CONF_DOMAIN): str,
                vol.Required(CONF_USERNAME): str,
                vol.Required(CONF_PASSWORD): str,
            },
        ),
    ),
    Provider.ANYDNS: ProviderConf(
        name="AnyDNS.info",
        base_url="https://anydns.info/update.php",
        params={"host": CONF_HOST, "user": CONF_USERNAME, "password": CONF_PASSWORD},
        schema=vol.Schema(
            {
                vol.Required(CONF_HOST): str,
                vol.Required(CONF_USERNAME): str,
                vol.Required(CONF_PASSWORD): str,
            },
        ),
    ),
    Provider.FREEDNS: ProviderConf(
        name="FreeDNS IPv4",
        base_url="https://sync.afraid.org/u/{token}/",
        schema=vol.Schema({vol.Required(CONF_TOKEN): str}),
        success_fn=lambda x: x.startswith(("Updated", "No IP change")),
    ),
    Provider.FREEDNS_IPV6: ProviderConf(
        name="FreeDNS IPv6",
        base_url="https://v6.sync.afraid.org/u/{token}",
        schema=vol.Schema({vol.Required(CONF_TOKEN): str}),
        success_fn=lambda x: x.startswith(("Updated", "No IP change")),
    ),
}
