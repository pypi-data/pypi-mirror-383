"""Dynamic DNS updater."""

from __future__ import annotations

import logging

from aiohttp import ClientSession

from .providers import Provider, providers

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
        self.method = providers[provider].method
        self.url = providers[provider].render_url(data)
        self.success = providers[provider].success_fn

    async def update(self) -> bool:
        """Update the dynamic DNS record."""

        async with self.session.request(self.method, self.url) as res:
            _LOGGER.debug(await res.text())
            return (
                self.success(await res.text()) if self.success is not None else res.ok
            )
