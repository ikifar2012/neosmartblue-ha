"""NeoSmart Blue entity base class."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER
from .coordinator import NeoSmartBlueCoordinator


class NeoSmartBlueEntity(CoordinatorEntity[NeoSmartBlueCoordinator]):
    """Base class for NeoSmart Blue entities."""

    def __init__(self, coordinator: NeoSmartBlueCoordinator) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.device.address)},
            name=coordinator.device.name or "NeoSmart Blue Device",
            manufacturer=MANUFACTURER,
            model="NeoSmart Blue Blind",
            connections={("bluetooth", coordinator.device.address)},
        )

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self.coordinator.last_update_success
