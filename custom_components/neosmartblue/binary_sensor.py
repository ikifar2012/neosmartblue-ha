"""Binary sensor platform for NeoSmart Blue Blinds."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)

from .const import DOMAIN
from .entity import NeoSmartBlueEntity

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import NeoSmartBlueCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the binary sensor platform."""
    coordinator: NeoSmartBlueCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            NeoSmartBlueMotorSensor(coordinator),
            NeoSmartBlueChargingSensor(coordinator),
        ]
    )


class NeoSmartBlueMotorSensor(NeoSmartBlueEntity, BinarySensorEntity):
    """Motor running binary sensor for NeoSmart Blue blind."""

    _attr_device_class = BinarySensorDeviceClass.RUNNING

    def __init__(self, coordinator: NeoSmartBlueCoordinator) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.device.address}_motor_running"
        self._attr_name = "Motor Running"

    @property
    def is_on(self) -> bool | None:
        """Return true if the motor is running."""
        if self.coordinator.data:
            return self.coordinator.data.get("motor_running", False)
        return None


class NeoSmartBlueChargingSensor(NeoSmartBlueEntity, BinarySensorEntity):
    """Charging binary sensor for NeoSmart Blue blind."""

    _attr_device_class = BinarySensorDeviceClass.BATTERY_CHARGING

    def __init__(self, coordinator: NeoSmartBlueCoordinator) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.device.address}_charging"
        self._attr_name = "Charging"

    @property
    def is_on(self) -> bool | None:
        """Return true if the device is charging."""
        if self.coordinator.data:
            return self.coordinator.data.get("charging", False)
        return None
