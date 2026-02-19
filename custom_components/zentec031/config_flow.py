"""Config flow for Zentec 031 integration."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from pymodbus.client import ModbusTcpClient

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import callback

from .const import (
    CONF_ALARM_REGISTER,
    CONF_FAN_SPEED_REGISTER,
    CONF_MAX_FAN_SPEED,
    CONF_OUTDOOR_TEMP_REGISTER,
    CONF_POWER_REGISTER,
    CONF_READ_ONLY,
    CONF_SCAN_INTERVAL,
    CONF_SLAVE_ID,
    CONF_SUPPLY_TEMP_REGISTER,
    CONF_TARGET_TEMP_REGISTER,
    CONF_TEMPERATURE_DIVISOR,
    DEFAULT_ALARM_REGISTER,
    DEFAULT_FAN_SPEED_REGISTER,
    DEFAULT_MAX_FAN_SPEED,
    DEFAULT_OUTDOOR_TEMP_REGISTER,
    DEFAULT_PORT,
    DEFAULT_POWER_REGISTER,
    DEFAULT_READ_ONLY,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_SLAVE_ID,
    DEFAULT_SUPPLY_TEMP_REGISTER,
    DEFAULT_TARGET_TEMP_REGISTER,
    DEFAULT_TEMPERATURE_DIVISOR,
    DOMAIN,
)


class ZentecConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Zentec 031."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        errors: dict[str, str] = {}

        if user_input is not None:
            await self.async_set_unique_id(f"{user_input[CONF_HOST]}:{user_input[CONF_PORT]}:{user_input[CONF_SLAVE_ID]}")
            self._abort_if_unique_id_configured()

            is_ok = await self.hass.async_add_executor_job(
                _can_connect,
                user_input[CONF_HOST],
                int(user_input[CONF_PORT]),
            )
            if is_ok:
                return self.async_create_entry(title=f"Zentec {user_input[CONF_HOST]}", data=user_input)
            errors["base"] = "cannot_connect"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST): str,
                    vol.Required(CONF_PORT, default=DEFAULT_PORT): vol.All(vol.Coerce(int), vol.Range(min=1, max=65535)),
                    vol.Required(CONF_SLAVE_ID, default=DEFAULT_SLAVE_ID): vol.All(vol.Coerce(int), vol.Range(min=1, max=247)),
                    vol.Required(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): vol.All(vol.Coerce(int), vol.Range(min=5, max=3600)),
                    vol.Required(CONF_POWER_REGISTER, default=DEFAULT_POWER_REGISTER): vol.All(
                        vol.Coerce(int), vol.Range(min=0, max=65535)
                    ),
                    vol.Required(CONF_FAN_SPEED_REGISTER, default=DEFAULT_FAN_SPEED_REGISTER): vol.All(
                        vol.Coerce(int), vol.Range(min=0, max=65535)
                    ),
                    vol.Required(CONF_TARGET_TEMP_REGISTER, default=DEFAULT_TARGET_TEMP_REGISTER): vol.All(
                        vol.Coerce(int), vol.Range(min=0, max=65535)
                    ),
                    vol.Required(CONF_SUPPLY_TEMP_REGISTER, default=DEFAULT_SUPPLY_TEMP_REGISTER): vol.All(
                        vol.Coerce(int), vol.Range(min=0, max=65535)
                    ),
                    vol.Required(CONF_OUTDOOR_TEMP_REGISTER, default=DEFAULT_OUTDOOR_TEMP_REGISTER): vol.All(
                        vol.Coerce(int), vol.Range(min=0, max=65535)
                    ),
                    vol.Required(CONF_ALARM_REGISTER, default=DEFAULT_ALARM_REGISTER): vol.All(
                        vol.Coerce(int), vol.Range(min=0, max=65535)
                    ),
                    vol.Required(CONF_TEMPERATURE_DIVISOR, default=DEFAULT_TEMPERATURE_DIVISOR): vol.All(
                        vol.Coerce(int), vol.Range(min=1, max=1000)
                    ),
                    vol.Required(CONF_MAX_FAN_SPEED, default=DEFAULT_MAX_FAN_SPEED): vol.All(
                        vol.Coerce(int), vol.Range(min=1, max=20)
                    ),
                    vol.Required(CONF_READ_ONLY, default=DEFAULT_READ_ONLY): bool,
                }
            ),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return ZentecOptionsFlow(config_entry)


class ZentecOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for Zentec 031."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self._entry = config_entry

    async def async_step_init(self, user_input: dict[str, Any] | None = None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        options = self._entry.options
        data = self._entry.data

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_SCAN_INTERVAL,
                        default=int(options.get(CONF_SCAN_INTERVAL, data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL))),
                    ): vol.All(vol.Coerce(int), vol.Range(min=5, max=3600)),
                    vol.Required(
                        CONF_POWER_REGISTER,
                        default=int(options.get(CONF_POWER_REGISTER, data.get(CONF_POWER_REGISTER, DEFAULT_POWER_REGISTER))),
                    ): vol.All(vol.Coerce(int), vol.Range(min=0, max=65535)),
                    vol.Required(
                        CONF_FAN_SPEED_REGISTER,
                        default=int(
                            options.get(CONF_FAN_SPEED_REGISTER, data.get(CONF_FAN_SPEED_REGISTER, DEFAULT_FAN_SPEED_REGISTER))
                        ),
                    ): vol.All(vol.Coerce(int), vol.Range(min=0, max=65535)),
                    vol.Required(
                        CONF_TARGET_TEMP_REGISTER,
                        default=int(
                            options.get(
                                CONF_TARGET_TEMP_REGISTER, data.get(CONF_TARGET_TEMP_REGISTER, DEFAULT_TARGET_TEMP_REGISTER)
                            )
                        ),
                    ): vol.All(vol.Coerce(int), vol.Range(min=0, max=65535)),
                    vol.Required(
                        CONF_SUPPLY_TEMP_REGISTER,
                        default=int(
                            options.get(
                                CONF_SUPPLY_TEMP_REGISTER, data.get(CONF_SUPPLY_TEMP_REGISTER, DEFAULT_SUPPLY_TEMP_REGISTER)
                            )
                        ),
                    ): vol.All(vol.Coerce(int), vol.Range(min=0, max=65535)),
                    vol.Required(
                        CONF_OUTDOOR_TEMP_REGISTER,
                        default=int(
                            options.get(
                                CONF_OUTDOOR_TEMP_REGISTER,
                                data.get(CONF_OUTDOOR_TEMP_REGISTER, DEFAULT_OUTDOOR_TEMP_REGISTER),
                            )
                        ),
                    ): vol.All(vol.Coerce(int), vol.Range(min=0, max=65535)),
                    vol.Required(
                        CONF_ALARM_REGISTER,
                        default=int(options.get(CONF_ALARM_REGISTER, data.get(CONF_ALARM_REGISTER, DEFAULT_ALARM_REGISTER))),
                    ): vol.All(vol.Coerce(int), vol.Range(min=0, max=65535)),
                    vol.Required(
                        CONF_TEMPERATURE_DIVISOR,
                        default=int(
                            options.get(CONF_TEMPERATURE_DIVISOR, data.get(CONF_TEMPERATURE_DIVISOR, DEFAULT_TEMPERATURE_DIVISOR))
                        ),
                    ): vol.All(vol.Coerce(int), vol.Range(min=1, max=1000)),
                    vol.Required(
                        CONF_MAX_FAN_SPEED,
                        default=int(options.get(CONF_MAX_FAN_SPEED, data.get(CONF_MAX_FAN_SPEED, DEFAULT_MAX_FAN_SPEED))),
                    ): vol.All(vol.Coerce(int), vol.Range(min=1, max=20)),
                    vol.Required(
                        CONF_READ_ONLY,
                        default=bool(options.get(CONF_READ_ONLY, data.get(CONF_READ_ONLY, DEFAULT_READ_ONLY))),
                    ): bool,
                }
            ),
        )


def _can_connect(host: str, port: int) -> bool:
    client = ModbusTcpClient(host=host, port=port)
    try:
        return bool(client.connect())
    finally:
        client.close()
