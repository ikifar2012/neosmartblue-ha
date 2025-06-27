"""DataUpdateCoordinator for NeoSmart Blue Blinds."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from homeassistant.components import bluetooth
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN, LOGGER, NEOSMART_MANUFACTURER_ID, STATUS_PAYLOAD_LENGTH

if TYPE_CHECKING:
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
            LOGGER,
            name=f"{DOMAIN}_{device.address}",
            update_interval=None,  # We'll use passive scanning
        )
        self.device = device
        self._bluelink_device: BlueLinkDevice | None = None
        self._connected = False

    @property
    def connected(self) -> bool:
        """Return if we are connected to the device."""
        return self._connected

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
            await self.bluelink_device.connect()
            self._connected = True
            LOGGER.debug("Connected to %s", self.device.address)

            # Request status update
            await self.bluelink_device.request_status_update()
            status_data = await self.bluelink_device.receive_data(timeout=5.0)

            if status_data and isinstance(status_data, dict):
                return status_data

        except (OSError, TimeoutError) as err:
            LOGGER.error("Failed to connect to %s: %s", self.device.address, err)
            self._connected = False
        finally:
            await self._disconnect()

        return None

    async def send_move_command(self, position: int) -> None:
        """Send move command to the device."""
        try:
            await self.bluelink_device.connect()
            await self.bluelink_device.move_to_position(position)
            LOGGER.info("Sent move command to position %d", position)
        except (OSError, TimeoutError) as err:
            LOGGER.error("Failed to send move command: %s", err)
        finally:
            await self._disconnect()

    async def send_stop_command(self) -> None:
        """Send stop command to the device."""
        try:
            await self.bluelink_device.connect()
            await self.bluelink_device.stop()
            LOGGER.info("Sent stop command")
        except (OSError, TimeoutError) as err:
            LOGGER.error("Failed to send stop command: %s", err)
        finally:
            await self._disconnect()

    async def _disconnect(self) -> None:
        """Disconnect from the BLE device."""
        if self._bluelink_device and self._connected:
            try:
                await self._bluelink_device.disconnect()
                LOGGER.debug("Disconnected from %s", self.device.address)
            except (OSError, TimeoutError) as err:
                LOGGER.error(
                    "Error disconnecting from %s: %s", self.device.address, err
                )
            finally:
                self._connected = False

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
            if NEOSMART_MANUFACTURER_ID in service_info.manufacturer_data:
                from neosmartblue.py import parse_status_data

                manufacturer_data = service_info.manufacturer_data[
                    NEOSMART_MANUFACTURER_ID
                ]
                status_payload = bytearray(manufacturer_data)

                if len(status_payload) >= STATUS_PAYLOAD_LENGTH:
                    # Parse the status data using your library
                    parsed_status = parse_status_data(
                        status_payload[:STATUS_PAYLOAD_LENGTH]
                    )

                    # Add RSSI information
                    parsed_status["rssi"] = service_info.device.rssi or -60

                    return parsed_status

        except (ValueError, KeyError, IndexError) as err:
            LOGGER.debug("Failed to parse advertisement data: %s", err)

        return None

    async def async_shutdown(self) -> None:
        """Shutdown the coordinator."""
        await self._disconnect()
