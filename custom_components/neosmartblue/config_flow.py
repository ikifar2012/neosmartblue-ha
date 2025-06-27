"""Config flow for Neosmart Blinds Blue."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant.components.bluetooth import (
    BluetoothServiceInfoBleak,
    async_discovered_service_info,
)
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_ADDRESS

from .const import DOMAIN, NEOSMART_MANUFACTURER_ID


class NeoSmartBlueConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Neosmart Blinds Blue."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._discovery_info: BluetoothServiceInfoBleak | None = None
        self._discovered_devices: dict[str, str] = {}
        self._title_placeholders: dict[str, str] = {}

    async def async_step_bluetooth(
        self, discovery_info: BluetoothServiceInfoBleak
    ) -> ConfigFlowResult:
        """Handle the bluetooth discovery step."""
        await self.async_set_unique_id(discovery_info.address)
        self._abort_if_unique_id_configured()
        self._discovery_info = discovery_info
        name = discovery_info.name or "Neosmart Blind Blue"
        self._title_placeholders = {"name": name}
        return await self.async_step_bluetooth_confirm()

    async def async_step_bluetooth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Confirm discovery."""
        if user_input is not None and self._discovery_info is not None:
            return self.async_create_entry(
                title=self._title_placeholders["name"],
                data={CONF_ADDRESS: self._discovery_info.address},
            )

        self._set_confirm_only()
        return self.async_show_form(
            step_id="bluetooth_confirm",
            description_placeholders=self._title_placeholders,
        )

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the user step to pick discovered device."""
        if user_input is not None:
            address = user_input[CONF_ADDRESS]
            await self.async_set_unique_id(address, raise_on_progress=False)
            self._abort_if_unique_id_configured()
            name = self._discovered_devices[address]
            return self.async_create_entry(title=name, data={CONF_ADDRESS: address})

        current_addresses = self._async_current_ids()
        for discovery_info in async_discovered_service_info(
            self.hass, connectable=True
        ):
            address = discovery_info.address
            if address in current_addresses or address in self._discovered_devices:
                continue

            if self._is_neosmart_device(discovery_info):
                name = discovery_info.name or "Neosmart Blind Blue"
                self._discovered_devices[address] = f"{name} ({address})"

        if not self._discovered_devices:
            return self.async_abort(reason="no_devices_found")

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {vol.Required(CONF_ADDRESS): vol.In(self._discovered_devices)}
            ),
        )

    def _is_neosmart_device(self, discovery_info: BluetoothServiceInfoBleak) -> bool:
        """Check if discovery_info is a NeoSmart Blue device."""
        # Check device name for NeoSmart Blue patterns
        name = discovery_info.name or ""
        if name.startswith(("NEO-", "NMB-")):
            return True

        # Also check manufacturer data for NeoSmart manufacturer ID
        return NEOSMART_MANUFACTURER_ID in discovery_info.manufacturer_data
