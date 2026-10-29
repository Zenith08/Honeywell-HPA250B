import re

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_ADDRESS

from .const import DOMAIN


class HoneywellHPA250BConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Honeywell HPA250B."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            address = user_input[CONF_ADDRESS].strip().upper().replace("-", ":")
            if not re.fullmatch(r"(?:[0-9A-F]{2}:){5}[0-9A-F]{2}", address):
                errors["base"] = "invalid_address"
            else:
                await self.async_set_unique_id(address)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=f"Honeywell HPA250B ({address})",
                    data={CONF_ADDRESS: address},
                )

        schema = vol.Schema({
            vol.Required(CONF_ADDRESS): str,
        })
        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
            description_placeholders={
                "hint": "Enter the purifier's Bluetooth address, for example F8:36:9B:80:8A:26."
            },
        )
