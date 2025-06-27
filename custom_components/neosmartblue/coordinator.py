"""DataUpdateCoordinator for NeoSmart Blue Blinds."""

from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING, Any

from bleak import BleakClient
from homeassistant.components import bluetooth
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from . import const

if TYPE_CHECKING:
    from collections.abc import AsyncIterator

    from bleak.backends.device import BLEDevice


class NeoSmartBlueCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Class to manage fetching data from NeoSmart Blue blinds via BLE."""

    def __init__(
        self,
        hass: HomeAssistant,
        device: BLEDevice,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            const.LOGGER,
            name=f"{const.DOMAIN}_{device.address}",
            update_interval=None,  # We'll use passive scanning
        )
        self.device = device
        self._connection_lock = asyncio.Lock()

    @asynccontextmanager
    async def _managed_connection(self) -> AsyncIterator[BleakClient]:
        """Provide a managed connection to the device."""
        ble_device = bluetooth.async_ble_device_from_address(
            self.hass, self.device.address, connectable=True
        )
        if not ble_device:
            msg = f"Device not available: {self.device.address}"
            raise HomeAssistantError(msg)

        async with self._connection_lock:
            client = BleakClient(ble_device)
            try:
                await client.connect()
                yield client
            finally:
                await client.disconnect()

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from the device."""
        # For NeoSmart Blue, we primarily get data from advertisements
        # But we can also connect and request status if needed
        return self.data or {
            "battery_level": 0,
            "current_position": 50,
            "target_position": 50,
            "rssi": self.device.rssi or -60,
            "motor_running": False,
            "motor_direction_down": False,
            "charging": False,
        }

    async def connect_and_get_status(self) -> dict[str, Any] | None:
        """Connect to device and get current status."""
        try:
            async with self._managed_connection() as client:
                const.LOGGER.debug("Connected to %s", self.device.address)

                # TODO: Implement status reading using the BleakClient
                # For now, return None to indicate no status available
                # You'll need to implement the actual GATT characteristic reading here
                return None

        except (OSError, TimeoutError, HomeAssistantError) as err:
            const.LOGGER.error("Failed to connect to %s: %s", self.device.address, err)

        return None

    async def send_move_command(self, position: int) -> None:
        """Send move command to the device."""
        try:
            async with self._managed_connection() as client:
                # TODO: Implement move command using the BleakClient
                # You'll need to write to the appropriate GATT characteristic here
                const.LOGGER.info("Sent move command to position %d", position)
        except (OSError, TimeoutError, HomeAssistantError) as err:
            const.LOGGER.error("Failed to send move command: %s", err)

    async def send_stop_command(self) -> None:
        """Send stop command to the device."""
        try:
            async with self._managed_connection() as client:
                # TODO: Implement stop command using the BleakClient
                # You'll need to write to the appropriate GATT characteristic here
                const.LOGGER.info("Sent stop command")
        except (OSError, TimeoutError, HomeAssistantError) as err:
            const.LOGGER.error("Failed to send stop command: %s", err)

    @callback
    def handle_bluetooth_event(
        self,
        service_info: bluetooth.BluetoothServiceInfoBleak,
        change: bluetooth.BluetoothChange,
    ) -> None:
        """Handle bluetooth events."""
        if change == bluetooth.BluetoothChange.ADVERTISEMENT:
            # Update device data from advertisement
            self.device = service_info.device

            # Parse manufacturer data for status information
            status_data = self._parse_advertisement_data(service_info)
            if status_data:
                self.async_set_updated_data(status_data)

    def _parse_advertisement_data(
        self, service_info: bluetooth.BluetoothServiceInfoBleak
    ) -> dict[str, Any] | None:
        """Parse advertisement data for status information."""
        if not service_info.manufacturer_data:
            return None

        try:
            # NeoSmart Blue devices use manufacturer ID 2407
            if const.NEOSMART_MANUFACTURER_ID in service_info.manufacturer_data:
                from neosmartblue.py import parse_status_data

                manufacturer_data = service_info.manufacturer_data[
                    const.NEOSMART_MANUFACTURER_ID
                ]
                status_payload = bytearray(manufacturer_data)

                if len(status_payload) >= const.STATUS_PAYLOAD_LENGTH:
                    # Parse the status data using your library
                    parsed_status = parse_status_data(
                        status_payload[: const.STATUS_PAYLOAD_LENGTH]
                    )

                    # Add RSSI information
                    parsed_status["rssi"] = service_info.device.rssi or -60

                    return parsed_status

        except (ValueError, KeyError, IndexError) as err:
            const.LOGGER.debug("Failed to parse advertisement data: %s", err)

        return None

    async def async_shutdown(self) -> None:
        """Shutdown the coordinator."""
        # Connections are now managed per-operation, so nothing to do on shutdown.
