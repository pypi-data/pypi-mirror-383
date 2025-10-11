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
    CONF_URL,
    CONF_USERNAME,
)


class Provider(StrEnum):
    """Dynamic DNS providers."""

    ANYDNS = "anydns"
    DUCKDNS = "duckdns"
    FREEDNS = "freedns"
    FREEDNS_IPV6 = "freedns_ipv6"
    MYTHICBEASTS = "mythicbeasts"
    NAMECHEAP = "namecheap"
    NO_IP = "no_ip"
    CUSTOM = "custom"


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
        url = URL(data.get(CONF_URL) or self.base_url)
        url = url.with_path(url.path.format(**data))
        if url.user:
            url = url.with_user(url.user.format(**data))
        if url.password:
            url = url.with_password(url.password.format(**data))
        return url % {k: data[v] for k, v in self.params.items() if v in data}


PROVIDERS: dict[Provider, ProviderConf] = {
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
    Provider.MYTHICBEASTS: ProviderConf(
        name="Mythic Beasts",
        base_url="https://ipv4.api.mythic-beasts.com/dns/v2/dynamic/{domain}",
        method="POST",
        params={"username": CONF_USERNAME, "password": CONF_PASSWORD},
        schema=vol.Schema(
            {
                vol.Required(CONF_DOMAIN): str,
                vol.Required(CONF_USERNAME): str,
                vol.Required(CONF_PASSWORD): str,
            }
        ),
    ),
    Provider.ANYDNS: ProviderConf(
        name="AnyDNS.info",
        base_url="https://anydns.info/update.php",
        params={
            "host": CONF_DOMAIN,
            "user": CONF_USERNAME,
            "password": CONF_PASSWORD,
            "ip": CONF_IP_ADDRESS,
            "ip6": CONF_IPV6_ADDRESS,
        },
        schema=vol.Schema(
            {
                vol.Required(CONF_DOMAIN): str,
                vol.Required(CONF_USERNAME): str,
                vol.Required(CONF_PASSWORD): str,
            },
        ),
    ),
    Provider.FREEDNS: ProviderConf(
        name="FreeDNS",
        base_url="https://sync.afraid.org/u/{token}/",
        params={"address": CONF_IP_ADDRESS},
        schema=vol.Schema({vol.Required(CONF_TOKEN): str}),
        success_fn=lambda x: x.startswith(("Updated", "No IP change")),
    ),
    Provider.FREEDNS_IPV6: ProviderConf(
        name="FreeDNS IPv6",
        base_url="https://v6.sync.afraid.org/u/{token}",
        params={"address": CONF_IPV6_ADDRESS},
        schema=vol.Schema({vol.Required(CONF_TOKEN): str}),
        success_fn=lambda x: x.startswith(("Updated", "No IP change")),
    ),
    Provider.NAMECHEAP: ProviderConf(
        name="Namecheap",
        base_url=(
            "https://dynamicdns.park-your-domain.com/update?host={host}&domain={domain}"
            "&password={password}&ip={ip_address}"
        ),
        params={
            "host": CONF_HOST,
            "domain": CONF_DOMAIN,
            "password": CONF_PASSWORD,
            "ip": CONF_IP_ADDRESS,
        },
        schema=vol.Schema(
            {
                vol.Required(CONF_HOST, default="@"): str,
                vol.Required(CONF_DOMAIN): str,
                vol.Required(CONF_PASSWORD): str,
            }
        ),
        success_fn=lambda x: "<ErrCount>0</ErrCount>" in x,
    ),
    Provider.NO_IP: ProviderConf(
        name="NO-IP.com",
        base_url="https://{username}:{password}@dynupdate.no-ip.com/nic/update",
        params={
            "hostname": CONF_DOMAIN,
            "myip": CONF_IP_ADDRESS,
        },
        schema=vol.Schema(
            {
                vol.Required(CONF_DOMAIN, default="all.ddnskey.com"): str,
                vol.Required(CONF_USERNAME): str,
                vol.Required(CONF_PASSWORD): str,
            }
        ),
        success_fn=lambda x: x.startswith(("good", "nochg")),
    ),
    Provider.CUSTOM: ProviderConf(
        name="Custom dynamic DNS",
        base_url="{url}",
        params={
            "ip": CONF_IP_ADDRESS,
            "ipv6": CONF_IPV6_ADDRESS,
        },
        schema=vol.Schema({vol.Required(CONF_URL): str}),
    ),
}
