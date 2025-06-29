"""Binary sensor platform for Neo Smart Blinds Blue."""

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
            NeoSmartBlueTouchControlSensor(coordinator),
            NeoSmartBlueUpLimitSensor(coordinator),
            NeoSmartBlueDownLimitSensor(coordinator),
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


class NeoSmartBlueTouchControlSensor(NeoSmartBlueEntity, BinarySensorEntity):
    """Touch control binary sensor for NeoSmart Blue blind."""

    def __init__(self, coordinator: NeoSmartBlueCoordinator) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.device.address}_touch_control"
        self._attr_name = "Touch Control Active"
        self._attr_entity_registry_enabled_default = False

    @property
    def is_on(self) -> bool | None:
        """Return true if touch control is active."""
        if self.coordinator.data:
            return self.coordinator.data.get("touch_control", False)
        return None


class NeoSmartBlueUpLimitSensor(NeoSmartBlueEntity, BinarySensorEntity):
    """Up limit set binary sensor for NeoSmart Blue blind."""

    def __init__(self, coordinator: NeoSmartBlueCoordinator) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.device.address}_up_limit_set"
        self._attr_name = "Up Limit Set"
        self._attr_entity_registry_enabled_default = False

    @property
    def is_on(self) -> bool | None:
        """Return true if up limit is set."""
        if self.coordinator.data:
            return self.coordinator.data.get("up_limit_set", False)
        return None


class NeoSmartBlueDownLimitSensor(NeoSmartBlueEntity, BinarySensorEntity):
    """Down limit set binary sensor for NeoSmart Blue blind."""

    def __init__(self, coordinator: NeoSmartBlueCoordinator) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.device.address}_down_limit_set"
        self._attr_name = "Down Limit Set"
        self._attr_entity_registry_enabled_default = False

    @property
    def is_on(self) -> bool | None:
        """Return true if down limit is set."""
        if self.coordinator.data:
            return self.coordinator.data.get("down_limit_set", False)
        return None
