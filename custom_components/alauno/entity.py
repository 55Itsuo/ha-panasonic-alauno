"""Base entity."""
from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import AlaunoCoordinator


class AlaunoEntity(CoordinatorEntity[AlaunoCoordinator]):
    _attr_has_entity_name = True

    def __init__(self, coordinator: AlaunoCoordinator, appliance_id: str) -> None:
        super().__init__(coordinator)
        self._aid = appliance_id
        dev = coordinator.data[appliance_id]
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, dev["serial"] or appliance_id)},
            name=f"アラウーノ {dev['name']}",
            manufacturer="Panasonic",
            model=dev["model"],
            serial_number=dev["serial"],
        )

    @property
    def dev(self) -> dict:
        return self.coordinator.data[self._aid]

    @property
    def available(self) -> bool:
        return super().available and self._aid in self.coordinator.data
