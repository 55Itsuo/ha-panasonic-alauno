"""Data update coordinator."""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import JST, AlaunoApiError, AlaunoAuthError, AlaunoClient
from .const import CONF_DEVICES, DOMAIN, SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)


class AlaunoCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Fetch devices, care status and today's usage."""

    def __init__(
        self, hass: HomeAssistant, entry: ConfigEntry, client: AlaunoClient
    ) -> None:
        super().__init__(
            hass, _LOGGER, name=DOMAIN, config_entry=entry, update_interval=SCAN_INTERVAL
        )
        self.client = client
        self.selected: list[str] = entry.data[CONF_DEVICES]

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            devices = await self.client.devices()
            now = datetime.now(JST)
            usages = await self.client.usages(now)
            result: dict[str, Any] = {}
            for dev in devices:
                aid = dev["appliance_id"]
                if aid not in self.selected:
                    continue
                info = dev.get("appliance_info", {})
                cares = {c["id"]: c for c in await self.client.care(aid)}
                times = sorted(usages.get(aid, []))
                result[aid] = {
                    "name": info.get("nickname") or aid[:6],
                    "serial": info.get("serial_number"),
                    "model": info.get("product_code"),
                    "cares": cares,
                    "today_count": len(times),
                    "last_used": times[-1] if times else None,
                }
            return result
        except AlaunoAuthError as err:
            raise ConfigEntryAuthFailed(str(err)) from err
        except AlaunoApiError as err:
            raise UpdateFailed(str(err)) from err
