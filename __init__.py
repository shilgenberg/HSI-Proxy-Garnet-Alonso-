from __future__ import annotations

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

from .const import DOMAIN, PLATFORMS, CONF_BASE_URL, CONF_TOKEN, CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
from .api import HsiProxyApi
from .coordinator import HsiSystemCoordinator


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    base_url = entry.data[CONF_BASE_URL]
    token = entry.data[CONF_TOKEN]
    scan_interval = entry.options.get(CONF_SCAN_INTERVAL, entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL))

    api = HsiProxyApi(hass, base_url, token)
    systems = await api.list_systems()

    coordinators = []
    for s in systems:
        c = HsiSystemCoordinator(hass, api, s, scan_interval)
        await c.async_config_entry_first_refresh()
        coordinators.append(c)

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "api": api,
        "systems": systems,
        "coordinators": {c.system.id: c for c in coordinators},
        "scan_interval": scan_interval,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok
