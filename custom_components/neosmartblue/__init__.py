"""
Custom integration to integrate NeoSmart Blue Blinds with Home Assistant.

This integration provides Bluetooth Low Energy (BLE) support for NeoSmart Blue blinds.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components import bluetooth
from homeassistant.const import Platform

from .const import DOMAIN, LOGGER
from .coordinator import NeoSmartBlueCoordinator

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant

PLATFORMS: list[Platform] = [
    Platform.COVER,
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> bool:
    """Set up NeoSmart Blue blinds from a config entry."""
    address: str = entry.data["address"]

    # Get the Bluetooth device
    ble_device = bluetooth.async_ble_device_from_address(
        hass, address, connectable=False
    )
    if not ble_device:
        LOGGER.error("Could not find Bluetooth device with address %s", address)
        return False

    # Create coordinator
    coordinator = NeoSmartBlueCoordinator(hass, ble_device)

    # Store coordinator in hass data
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Set up Bluetooth listener for passive updates
    entry.async_on_unload(
        bluetooth.async_register_callback(
            hass,
            coordinator.handle_bluetooth_event,
            {"address": address},
            bluetooth.BluetoothScanningMode.PASSIVE,
        )
    )

    # Forward entry setup to platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Add update listener
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> bool:
    """Handle removal of an entry."""
    coordinator: NeoSmartBlueCoordinator = hass.data[DOMAIN][entry.entry_id]
    await coordinator.async_shutdown()

    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def async_reload_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> None:
    """Reload config entry."""
    await hass.config_entries.async_reload(entry.entry_id)
