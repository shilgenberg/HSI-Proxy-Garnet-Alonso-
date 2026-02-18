from __future__ import annotations

from datetime import timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import HsiProxyApi, HsiSystem


class HsiSystemCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    def __init__(self, hass: HomeAssistant, api: HsiProxyApi, system: HsiSystem, scan_interval: int) -> None:
        super().__init__(
            hass,
            logger=__import__("logging").getLogger(__name__),
            name=f"HSI Proxy {system.name}",
            update_interval=timedelta(seconds=scan_interval),
        )
        self.api = api
        self.system = system

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            return await self.api.state_decoded(self.system.id)
        except Exception as err:
            raise UpdateFailed(str(err)) from err
