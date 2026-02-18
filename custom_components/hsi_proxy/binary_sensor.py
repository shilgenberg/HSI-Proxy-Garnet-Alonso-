from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    data = hass.data[DOMAIN][entry.entry_id]
    systems = data["systems"]
    coordinators = data["coordinators"]

    entities = []
    for s in systems:
        entities.append(OnlineBinarySensor(coordinators[s.id], s.id, s.name))
    async_add_entities(entities)


class OnlineBinarySensor(CoordinatorEntity, BinarySensorEntity):
    def __init__(self, coordinator, system_id: int, name: str) -> None:
        super().__init__(coordinator)
        self._attr_name = f"{name} Online"
        self._attr_unique_id = f"hsi_proxy_online_{system_id}"
        self._attr_icon = "mdi:cloud-check-outline"

    @property
    def is_on(self) -> bool:
        data = self.coordinator.data
        if not data:
            return False
        # si llega state_decoded, consideramos online
        return "decoded" in data
