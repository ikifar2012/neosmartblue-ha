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
    """
    Class to manage fetching data from NeoSmart Blue blinds via BLE.

    This coordinator operates in a purely passive mode:
    - No active polling or data fetching
    - Updates only come from BLE advertisements via handle_bluetooth_event
    - Connections are only made for sending commands, never for status
    """

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
            # Get a scanner to ensure we have the best connection strategy
            scanner = bluetooth.async_get_scanner(self.hass)
            if not scanner:
                msg = "No Bluetooth scanner available"
                raise HomeAssistantError(msg)

            client = BleakClient(ble_device)
            try:
                # Use a longer timeout for connection attempts as recommended
                # for devices that might need service resolution
                await client.connect(timeout=15.0)
                const.LOGGER.debug(
                    "Successfully connected to %s via BleakClient",
                    self.device.address,
                )
                yield client
            except Exception as err:
                const.LOGGER.error(
                    "Failed to connect to %s: %s",
                    self.device.address,
                    err,
                )
                raise
            finally:
                try:
                    if client.is_connected:
                        await client.disconnect()
                        const.LOGGER.debug(
                            "Disconnected from %s",
                            self.device.address,
                        )
                except (OSError, TimeoutError, HomeAssistantError, Exception) as err:
                    const.LOGGER.warning(
                        "Error during disconnect from %s: %s",
                        self.device.address,
                        err,
                    )

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from the device."""
        # For NeoSmart Blue, we rely entirely on advertisements for status data
        # Return existing data or default values - no active polling
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

    async def send_move_command(self, position: int) -> None:
        """Send move command to the device."""
        const.LOGGER.debug(
            "Attempting to send move command to position %d for %s",
            position,
            self.device.address,
        )

        # Check if device is present and connectable before attempting connection
        if not bluetooth.async_address_present(
            self.hass, self.device.address, connectable=True
        ):
            const.LOGGER.warning(
                "Device %s is not present or not connectable, cannot send move command",
                self.device.address,
            )
            return

        # Check if we have a connectable device available
        ble_device = bluetooth.async_ble_device_from_address(
            self.hass, self.device.address, connectable=True
        )
        if not ble_device:
            const.LOGGER.warning(
                "No connectable device found for %s, cannot send move command",
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
        except (OSError, TimeoutError, HomeAssistantError, Exception) as err:
            const.LOGGER.exception(
                "Failed to send move command to %s: %s",
                self.device.address,
                err,
            )

    async def send_stop_command(self) -> None:
        """Send stop command to the device."""
        const.LOGGER.debug("Attempting to send stop command to %s", self.device.address)

        # Check if device is present and connectable before attempting connection
        if not bluetooth.async_address_present(
            self.hass, self.device.address, connectable=True
        ):
            const.LOGGER.warning(
                "Device %s is not present or not connectable, cannot send stop command",
                self.device.address,
            )
            return

        # Check if we have a connectable device available
        ble_device = bluetooth.async_ble_device_from_address(
            self.hass, self.device.address, connectable=True
        )
        if not ble_device:
            const.LOGGER.warning(
                "No connectable device found for %s, cannot send stop command",
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
        except (OSError, TimeoutError, HomeAssistantError, Exception) as err:
            const.LOGGER.exception(
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
        # This method is kept for manual refresh if needed, but normal operation
        # relies entirely on the handle_bluetooth_event callback for updates
        latest_data = self.get_latest_advertisement_data()
        if latest_data:
            const.LOGGER.debug(
                "Manually refreshed advertisement data for %s: %s",
                self.device.address,
                latest_data,
            )
            self.async_set_updated_data(latest_data)
        else:
            const.LOGGER.debug(
                "No advertisement data available for manual refresh for %s",
                self.device.address,
            )

    def is_device_connectable(self) -> bool:
        """Check if the device is currently connectable."""
        return bool(
            bluetooth.async_ble_device_from_address(
                self.hass, self.device.address, connectable=True
            )
        )
