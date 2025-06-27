"""Sensor platform for NeoSmart Blue Blinds."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import (
    PERCENTAGE,
    SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
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
    """Set up the sensor platform."""
    coordinator: NeoSmartBlueCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            NeoSmartBlueBatterySensor(coordinator),
            NeoSmartBlueRSSISensor(coordinator),
            NeoSmartBluePositionSensor(coordinator),
        ]
    )


class NeoSmartBlueBatterySensor(NeoSmartBlueEntity, SensorEntity):
    """Battery level sensor for NeoSmart Blue blind."""

    _attr_device_class = SensorDeviceClass.BATTERY
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = PERCENTAGE

    def __init__(self, coordinator: NeoSmartBlueCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.device.address}_battery"
        self._attr_name = "Battery Level"

    @property
    def native_value(self) -> int | None:
        """Return the battery level."""
        if self.coordinator.data:
            return self.coordinator.data.get("battery_level")
        return None


class NeoSmartBlueRSSISensor(NeoSmartBlueEntity, SensorEntity):
    """RSSI sensor for NeoSmart Blue blind."""

    _attr_device_class = SensorDeviceClass.SIGNAL_STRENGTH
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = SIGNAL_STRENGTH_DECIBELS_MILLIWATT
    _attr_entity_registry_enabled_default = False

    def __init__(self, coordinator: NeoSmartBlueCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.device.address}_rssi"
        self._attr_name = "Signal Strength"

    @property
    def native_value(self) -> int | None:
        """Return the RSSI value."""
        if self.coordinator.data:
            return self.coordinator.data.get("rssi")
        return None


class NeoSmartBluePositionSensor(NeoSmartBlueEntity, SensorEntity):
    """Position sensor for NeoSmart Blue blind."""

    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = PERCENTAGE

    def __init__(self, coordinator: NeoSmartBlueCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.device.address}_position"
        self._attr_name = "Position"

    @property
    def native_value(self) -> int | None:
        """Return the current position."""
        if self.coordinator.data:
            return self.coordinator.data.get("current_position")
        return None
