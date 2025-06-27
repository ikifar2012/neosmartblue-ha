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
        # First try to get a connectable device
        ble_device = bluetooth.async_ble_device_from_address(
            self.hass, self.device.address, connectable=True
        )

        # If no connectable device found, try getting any device and use it anyway
        if not ble_device:
            ble_device = bluetooth.async_ble_device_from_address(
                self.hass, self.device.address, connectable=False
            )

        # If still no device, check if we have a recent advertisement
        if not ble_device:
            service_info = bluetooth.async_last_service_info(
                self.hass, self.device.address, connectable=False
            )
            if service_info:
                ble_device = service_info.device

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
        # Try to get the latest advertisement data first
        latest_data = self.get_latest_advertisement_data()
        if latest_data:
            const.LOGGER.debug(
                "Using latest advertisement data for %s: %s",
                self.device.address,
                latest_data,
            )
            return latest_data

        # Fall back to existing data or default values
        return self.data or {
            "battery_level": 0,
            "current_position": 50,
            "target_position": 50,
            "limit_range_size": 0,
            "rssi": self.device.rssi or -60,
            "motor_running": False,
            "motor_direction_down": False,
            "up_limit_set": False,
            "down_limit_set": False,
            "touch_control": False,
            "charging": False,
            "channel_setting_mode": False,
            "reverse_rotation": False,
        }

    def _create_bluelink_device(self, client: BleakClient) -> Any:
        """Create a BlueLinkDevice with injected client."""
        from neosmartblue.py import BlueLinkDevice

        bluelink_device = BlueLinkDevice(self.device.address)
        # Inject our managed client into the device
        object.__setattr__(bluelink_device, "client", client)
        return bluelink_device

    async def connect_and_get_status(self) -> dict[str, Any] | None:
        """Connect to device and get current status."""
        try:
            async with self._managed_connection() as client:
                const.LOGGER.debug("Connected to %s", self.device.address)

                # Use the neosmartblue library to get status
                bluelink_device = self._create_bluelink_device(client)

                # Request status update
                await bluelink_device.request_status_update()
                status_data = await bluelink_device.receive_data(timeout=5.0)

                if status_data and isinstance(status_data, dict):
                    return status_data

        except (OSError, TimeoutError, HomeAssistantError) as err:
            const.LOGGER.error("Failed to connect to %s: %s", self.device.address, err)

        return None

    async def send_move_command(self, position: int) -> None:
        """Send move command to the device."""
        const.LOGGER.debug(
            "Attempting to send move command to position %d for %s",
            position,
            self.device.address,
        )

        # Check if device is present before attempting connection
        if not bluetooth.async_address_present(
            self.hass, self.device.address, connectable=False
        ):
            const.LOGGER.warning(
                "Device %s is not present, cannot send move command",
                self.device.address,
            )
            return

        try:
            async with self._managed_connection() as client:
                const.LOGGER.debug(
                    "Successfully connected to %s for move command",
                    self.device.address,
                )

                # Use the neosmartblue library to send move command
                bluelink_device = self._create_bluelink_device(client)

                await bluelink_device.move_to_position(position)
                const.LOGGER.info("Sent move command to position %d", position)
        except (OSError, TimeoutError, HomeAssistantError) as err:
            const.LOGGER.error(
                "Failed to send move command to %s: %s",
                self.device.address,
                err,
            )

    async def send_stop_command(self) -> None:
        """Send stop command to the device."""
        const.LOGGER.debug("Attempting to send stop command to %s", self.device.address)

        # Check if device is present before attempting connection
        if not bluetooth.async_address_present(
            self.hass, self.device.address, connectable=False
        ):
            const.LOGGER.warning(
                "Device %s is not present, cannot send stop command",
                self.device.address,
            )
            return

        try:
            async with self._managed_connection() as client:
                const.LOGGER.debug(
                    "Successfully connected to %s for stop command",
                    self.device.address,
                )

                # Use the neosmartblue library to send stop command
                bluelink_device = self._create_bluelink_device(client)

                await bluelink_device.stop()
                const.LOGGER.info("Sent stop command")
        except (OSError, TimeoutError, HomeAssistantError) as err:
            const.LOGGER.error(
                "Failed to send stop command to %s: %s",
                self.device.address,
                err,
            )

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
                const.LOGGER.debug(
                    "Received advertisement data from %s: %s",
                    self.device.address,
                    status_data,
                )
                self.async_set_updated_data(status_data)
            else:
                const.LOGGER.debug(
                    "Advertisement from %s without valid status data",
                    self.device.address,
                )

    def _parse_advertisement_data(
        self, service_info: bluetooth.BluetoothServiceInfoBleak
    ) -> dict[str, Any] | None:
        """Parse advertisement data for status information."""
        if not service_info.manufacturer_data:
            const.LOGGER.debug(
                "No manufacturer data in advertisement from %s",
                service_info.device.address,
            )
            return None

        try:
            # NeoSmart Blue devices use manufacturer ID 2407
            if const.NEOSMART_MANUFACTURER_ID in service_info.manufacturer_data:
                from neosmartblue.py import parse_status_data

                manufacturer_data = service_info.manufacturer_data[
                    const.NEOSMART_MANUFACTURER_ID
                ]
                status_payload = bytearray(manufacturer_data)

                const.LOGGER.debug(
                    "Raw manufacturer data from %s: %s",
                    service_info.device.address,
                    status_payload.hex().upper(),
                )

                if len(status_payload) >= const.STATUS_PAYLOAD_LENGTH:
                    # Parse the status data using the library
                    parsed_status = parse_status_data(
                        status_payload[: const.STATUS_PAYLOAD_LENGTH]
                    )

                    # Add RSSI information
                    parsed_status["rssi"] = service_info.device.rssi or -60

                    const.LOGGER.debug(
                        "Parsed status data from %s: %s",
                        service_info.device.address,
                        parsed_status,
                    )
                    return parsed_status

                const.LOGGER.debug(
                    "Status payload too short from %s: %d bytes (expected %d)",
                    service_info.device.address,
                    len(status_payload),
                    const.STATUS_PAYLOAD_LENGTH,
                )

            const.LOGGER.debug(
                "No NeoSmart manufacturer data from %s (found IDs: %s)",
                service_info.device.address,
                list(service_info.manufacturer_data.keys()),
            )

        except (ValueError, KeyError, IndexError) as err:
            const.LOGGER.warning(
                "Failed to parse advertisement data from %s: %s",
                service_info.device.address,
                err,
            )

        return None

    async def async_shutdown(self) -> None:
        """Shutdown the coordinator."""
        # Connections are now managed per-operation, so nothing to do on shutdown.

    def is_device_advertising(self) -> bool:
        """Check if the device is currently advertising."""
        return bluetooth.async_address_present(
            self.hass, self.device.address, connectable=False
        )

    def get_latest_advertisement_data(self) -> dict[str, Any] | None:
        """Get the latest advertisement data without connection."""
        service_info = bluetooth.async_last_service_info(
            self.hass, self.device.address, connectable=False
        )
        if service_info:
            return self._parse_advertisement_data(service_info)
        return None

    async def refresh_advertisement_data(self) -> None:
        """Manually refresh data from the latest advertisement."""
        latest_data = self.get_latest_advertisement_data()
        if latest_data:
            const.LOGGER.debug(
                "Refreshed advertisement data for %s: %s",
                self.device.address,
                latest_data,
            )
            self.async_set_updated_data(latest_data)
        else:
            const.LOGGER.debug(
                "No advertisement data available for %s",
                self.device.address,
            )
