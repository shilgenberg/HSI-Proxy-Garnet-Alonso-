from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any

from homeassistant.helpers.aiohttp_client import async_get_clientsession


@dataclass
class HsiSystem:
    id: int
    name: str


class HsiProxyApi:
    def __init__(self, hass, base_url: str, token: str) -> None:
        self._hass = hass
        self._base_url = base_url.rstrip("/")
        self._token = token
        self._session = async_get_clientsession(hass)

    def _headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self._token}"}

    async def _request(self, method: str, path: str, **kwargs) -> Any:
        url = f"{self._base_url}{path}"
        headers = kwargs.pop("headers", {})
        headers.update(self._headers())

        # aiohttp is async; keep timeouts reasonable
        timeout = kwargs.pop("timeout", 20)

        async with asyncio.timeout(timeout):
            resp = await self._session.request(method, url, headers=headers, **kwargs)

        text = await resp.text()
        if resp.status >= 400:
            raise RuntimeError(f"HTTP {resp.status}: {text}")

        # try json
        try:
            return await resp.json()
        except Exception:
            return {"raw": text}

    async def health(self) -> dict[str, Any]:
        return await self._request("GET", "/health")

    async def list_systems(self) -> list[HsiSystem]:
        data = await self._request("GET", "/api/systems")
        systems = data.get("systems", [])
        out: list[HsiSystem] = []
        for s in systems:
            out.append(HsiSystem(id=int(s["id"]), name=str(s.get("name") or f"System {s['id']}")))
        return out

    async def state_decoded(self, system_id: int) -> dict[str, Any]:
        return await self._request("GET", f"/api/systems/{system_id}/state_decoded")

    async def arm_away(self, system_id: int) -> dict[str, Any]:
        return await self._request("POST", f"/api/systems/{system_id}/arm/away")

    async def arm_home(self, system_id: int) -> dict[str, Any]:
        return await self._request("POST", f"/api/systems/{system_id}/arm/home")

    async def disarm(self, system_id: int) -> dict[str, Any]:
        return await self._request("POST", f"/api/systems/{system_id}/disarm")
