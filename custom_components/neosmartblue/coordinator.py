"""DataUpdateCoordinator for NeoSmart Blue Blinds."""

from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING, Any

from homeassistant.components import bluetooth
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from . import const

if TYPE_CHECKING:
    from collections.abc import AsyncIterator

    from bleak.backends.device import BLEDevice
    from neosmartblue.py import BlueLinkDevice


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
        self._bluelink_device: BlueLinkDevice | None = None
        self._connection_lock = asyncio.Lock()

    @asynccontextmanager
    async def _managed_connection(self) -> AsyncIterator[None]:
        """Provide a managed connection to the device."""
        async with self._connection_lock:
            try:
                await self.bluelink_device.connect()
                yield
            finally:
                await self.bluelink_device.disconnect()

    @property
    def bluelink_device(self) -> BlueLinkDevice:
        """Get the BlueLinkDevice instance."""
        if self._bluelink_device is None:
            from neosmartblue.py import BlueLinkDevice

            self._bluelink_device = BlueLinkDevice(self.device.address)
        return self._bluelink_device

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
            async with self._managed_connection():
                const.LOGGER.debug("Connected to %s", self.device.address)

                # Request status update
                await self.bluelink_device.request_status_update()
                status_data = await self.bluelink_device.receive_data(timeout=5.0)

                if status_data and isinstance(status_data, dict):
                    return status_data

        except (OSError, TimeoutError) as err:
            const.LOGGER.error("Failed to connect to %s: %s", self.device.address, err)

        return None

    async def send_move_command(self, position: int) -> None:
        """Send move command to the device."""
        try:
            async with self._managed_connection():
                await self.bluelink_device.move_to_position(position)
                const.LOGGER.info("Sent move command to position %d", position)
        except (OSError, TimeoutError) as err:
            const.LOGGER.error("Failed to send move command: %s", err)

    async def send_stop_command(self) -> None:
        """Send stop command to the device."""
        try:
            async with self._managed_connection():
                await self.bluelink_device.stop()
                const.LOGGER.info("Sent stop command")
        except (OSError, TimeoutError) as err:
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
