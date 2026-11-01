"""Care (maintenance) binary sensors."""
from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)

from .const import CARE_NAMES
from .entity import AlaunoEntity


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = entry.runtime_data
    entities = []
    for aid, dev in coordinator.data.items():
        for care_id in dev["cares"]:
            entities.append(AlaunoCare(coordinator, aid, care_id))
    async_add_entities(entities)


class AlaunoCare(AlaunoEntity, BinarySensorEntity):
    _attr_device_class = BinarySensorDeviceClass.PROBLEM

    def __init__(self, coordinator, aid, care_id):
        super().__init__(coordinator, aid)
        self._care_id = care_id
        self._attr_unique_id = f"{self.dev['serial']}_care_{care_id}"
        if care_id in CARE_NAMES:
            # Name comes from translations/<lang>.json -> entity.binary_sensor.<care_id>
            self._attr_translation_key = care_id
        else:
            # Unknown care item reported by the cloud: fall back to its raw id
            self._attr_name = care_id

    @property
    def _care(self) -> dict:
        return self.dev["cares"].get(self._care_id, {})

    @property
    def is_on(self):
        return bool(self._care.get("need_care"))

    @property
    def extra_state_attributes(self):
        c = self._care
        return {
            "level": c.get("level"),
            "first_notified_date": c.get("first_notified_date"),
            "last_cared_date": c.get("last_cared_date"),
            "howto_url": c.get("desc_url"),
        }
