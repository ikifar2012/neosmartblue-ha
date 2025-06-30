"""Cover platform for Neo Smart Blinds Blue."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from homeassistant.components.cover import (
    ATTR_POSITION,
    CoverDeviceClass,
    CoverEntity,
    CoverEntityFeature,
)

from .const import DOMAIN
from .entity import NeoSmartBlueEntity

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import NeoSmartBlueCoordinator

# Position constants
FULLY_OPEN = 100
FULLY_CLOSED = 0


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the cover platform."""
    coordinator: NeoSmartBlueCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([NeoSmartBlueCover(coordinator)])


class NeoSmartBlueCover(NeoSmartBlueEntity, CoverEntity):
    """NeoSmart Blue blind cover entity."""

    _attr_device_class = CoverDeviceClass.SHADE
    _attr_supported_features = (
        CoverEntityFeature.OPEN
        | CoverEntityFeature.CLOSE
        | CoverEntityFeature.STOP
        | CoverEntityFeature.SET_POSITION
    )

    def __init__(self, coordinator: NeoSmartBlueCoordinator) -> None:
        """Initialize the cover."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.device.address}_cover"
        self._attr_name = "Blind"

    @property
    def current_cover_position(self) -> int | None:
        """Return current position of cover."""
        if self.coordinator.data:
            # Invert position so 100 is open
            pos = self.coordinator.data.get("current_position")
            if pos is not None:
                return 100 - pos
        return None

    @property
    def is_closed(self) -> bool | None:
        """Return if the cover is closed or not."""
        position = self.current_cover_position
        return position == FULLY_CLOSED if position is not None else None

    @property
    def is_opening(self) -> bool:
        """Return if the cover is opening or not."""
        if self.coordinator.data:
            return self.coordinator.data.get(
                "motor_running", False
            ) and self.coordinator.data.get("motor_direction_down", False)
        return False

    @property
    def is_closing(self) -> bool:
        """Return if the cover is closing or not."""
        if self.coordinator.data:
            return self.coordinator.data.get(
                "motor_running", False
            ) and not self.coordinator.data.get("motor_direction_down", False)
        return False

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        # Device is available if we can see advertisements or it's connectable
        return (
            self.coordinator.is_device_advertising()
            or self.coordinator.is_device_connectable()
        )

    async def async_open_cover(self, **_kwargs: Any) -> None:
        """Open the cover."""
        await self.coordinator.send_move_command(0)

    async def async_close_cover(self, **_kwargs: Any) -> None:
        """Close the cover."""
        await self.coordinator.send_move_command(100)

    async def async_stop_cover(self, **_kwargs: Any) -> None:
        """Stop the cover."""
        await self.coordinator.send_stop_command()

    async def async_set_cover_position(self, **kwargs: Any) -> None:
        """Move the cover to a specific position."""
        position = kwargs[ATTR_POSITION]
        device_position = 100 - position
        await self.coordinator.send_move_command(device_position)
