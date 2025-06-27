"""Base entity for the NeoSmart Blue integration."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER
from .coordinator import NeoSmartBlueCoordinator


class NeoSmartBlueEntity(CoordinatorEntity[NeoSmartBlueCoordinator]):
    """Base class for NeoSmart Blue entities."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: NeoSmartBlueCoordinator) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.device.address)},
            name=coordinator.device.name or "NeoSmart Blue Blind",
            manufacturer=MANUFACTURER,
            model="NeoSmart Blue Blind",
        )
