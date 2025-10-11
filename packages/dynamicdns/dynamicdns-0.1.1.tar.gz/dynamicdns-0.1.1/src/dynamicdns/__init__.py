# SPDX-FileCopyrightText: 2025-present tr4nt0r <4445816+tr4nt0r@users.noreply.github.com>
#
# SPDX-License-Identifier: MIT

from .providers import Provider, ProviderConf, PROVIDERS
from .updater import Updater

__version__ = "0.1.1"
__all__ = [
    "PROVIDERS",
    "Provider",
    "ProviderConf",
    "Updater",
]
