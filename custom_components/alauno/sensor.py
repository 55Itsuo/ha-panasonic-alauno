"""Usage sensors."""
from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)

from .entity import AlaunoEntity


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = entry.runtime_data
    entities = []
    for aid in coordinator.data:
        entities.append(AlaunoLastUsed(coordinator, aid))
        entities.append(AlaunoTodayCount(coordinator, aid))
    async_add_entities(entities)


class AlaunoLastUsed(AlaunoEntity, SensorEntity):
    _attr_device_class = SensorDeviceClass.TIMESTAMP
    _attr_translation_key = "last_used"

    def __init__(self, coordinator, aid):
        super().__init__(coordinator, aid)
        self._attr_unique_id = f"{self.dev['serial']}_last_used"

    @property
    def native_value(self):
        return self.dev["last_used"]


class AlaunoTodayCount(AlaunoEntity, SensorEntity):
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_translation_key = "today_count"
    _attr_native_unit_of_measurement = "回"

    def __init__(self, coordinator, aid):
        super().__init__(coordinator, aid)
        self._attr_unique_id = f"{self.dev['serial']}_today_count"

    @property
    def native_value(self):
        return self.dev["today_count"]
