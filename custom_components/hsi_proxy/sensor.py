from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .api import HsiProxyApi


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    data = hass.data[DOMAIN][entry.entry_id]
    api: HsiProxyApi = data["api"]
    systems = data["systems"]
    coordinators = data["coordinators"]

    entities = []
    for s in systems:
        c = coordinators[s.id]
        entities.append(OpenZonesSensor(c, s.id, s.name))
        entities.append(TroublesSensor(c, s.id, s.name))
    async_add_entities(entities)


class OpenZonesSensor(CoordinatorEntity):
    def __init__(self, coordinator, system_id: int, name: str) -> None:
        super().__init__(coordinator)
        self._attr_name = f"{name} Zonas Abiertas"
        self._attr_unique_id = f"hsi_proxy_open_zones_{system_id}"
        self._attr_icon = "mdi:door-open"

    @property
    def native_value(self):
        decoded = (self.coordinator.data or {}).get("decoded", {})
        zones = decoded.get("zonas_abiertas", [])
        return ",".join(str(z) for z in zones) if zones else ""

    @property
    def extra_state_attributes(self):
        decoded = (self.coordinator.data or {}).get("decoded", {})
        return {
            "zonas_abiertas": decoded.get("zonas_abiertas", []),
            "zonas_alarma": decoded.get("zonas_alarma", []),
            "zonas_inhibidas": decoded.get("zonas_inhibidas", []),
        }


class TroublesSensor(CoordinatorEntity):
    def __init__(self, coordinator, system_id: int, name: str) -> None:
        super().__init__(coordinator)
        self._attr_name = f"{name} Problemas"
        self._attr_unique_id = f"hsi_proxy_troubles_{system_id}"
        self._attr_icon = "mdi:alert-circle-outline"

    @property
    def native_value(self):
        decoded = (self.coordinator.data or {}).get("decoded", {})
        t = decoded.get("troubles1", {}) or {}
        active = [k for k, v in t.items() if v]
        return ", ".join(active) if active else "ok"

    @property
    def extra_state_attributes(self):
        decoded = (self.coordinator.data or {}).get("decoded", {})
        return {"troubles1": decoded.get("troubles1", {})}
