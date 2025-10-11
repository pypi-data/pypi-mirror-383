"""Dynamic DNS updater."""

from __future__ import annotations

import logging

from aiohttp import ClientSession

from .providers import Provider, PROVIDERS

_LOGGER = logging.getLogger(__package__)


class Updater:
    """Dynamic DNS updater class."""

    def __init__(
        self,
        provider: Provider,
        data: dict[str, str],
        session: ClientSession,
    ) -> None:
        """Initialize."""

        self.session = session
        self.provider = provider
        self.method = PROVIDERS[provider].method
        self.url = PROVIDERS[provider].render_url(data)
        self.success = PROVIDERS[provider].success_fn

    async def update(self) -> bool:
        """Update the dynamic DNS record."""

        async with self.session.request(self.method, self.url) as res:
            _LOGGER.debug("[%s]: %s", self.provider.name, await res.text())
            return (
                self.success(await res.text()) if self.success is not None else res.ok
            )
