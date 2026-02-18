from __future__ import annotations

from homeassistant.components.alarm_control_panel import (
    AlarmControlPanelEntity,
    AlarmControlPanelEntityFeature,
    AlarmControlPanelState,
)
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
        entities.append(HsiAlarmEntity(api, coordinators[s.id], s.id, s.name))
    async_add_entities(entities)


class HsiAlarmEntity(CoordinatorEntity, AlarmControlPanelEntity):
    _attr_supported_features = (
        AlarmControlPanelEntityFeature.ARM_AWAY
        | AlarmControlPanelEntityFeature.ARM_HOME
        | AlarmControlPanelEntityFeature.ARM_CUSTOM_BYPASS
    )

    def __init__(self, api: HsiProxyApi, coordinator, system_id: int, name: str) -> None:
        super().__init__(coordinator)
        self.api = api
        self.system_id = system_id
        self._attr_name = f"{name} Alarm"
        self._attr_unique_id = f"hsi_proxy_alarm_{system_id}"

    @property
    def state(self) -> AlarmControlPanelState:
        # Nota: si querés estados exactos (armed_away/armed_home) hay que mapear
        # bits del "estado_particiones_hex". Por ahora: si hay troubles/zonas alarma
        # no determina armado. Entonces exponemos "disarmed" como default.
        data = self.coordinator.data or {}
        decoded = data.get("decoded", {})
        # Heurística mínima: si hay zonas en alarma => triggered
        if decoded.get("zonas_alarma"):
            return AlarmControlPanelState.TRIGGERED
        return AlarmControlPanelState.DISARMED

    async def async_alarm_arm_away(self, code: str | None = None) -> None:
        await self.api.arm_away(self.system_id)
        await self.coordinator.async_request_refresh()

    async def async_alarm_arm_home(self, code: str | None = None) -> None:
        await self.api.arm_home(self.system_id)
        await self.coordinator.async_request_refresh()

    async def async_alarm_disarm(self, code: str | None = None) -> None:
        await self.api.disarm(self.system_id)
        await self.coordinator.async_request_refresh()
