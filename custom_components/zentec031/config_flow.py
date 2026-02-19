"""Config flow for Zentec 031 integration."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from pymodbus.client import ModbusTcpClient

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_PORT
from homeassistant.core import callback
from homeassistant.helpers import selector

from .const import (
    CONF_ALARM_REGISTER,
    CONF_FAN_SPEED_REGISTER,
    CONF_MAX_HEAT_TEMP_REGISTER,
    CONF_MAX_FAN_SPEED,
    CONF_MIN_HEAT_TEMP_REGISTER,
    CONF_MODE_HEAT_VALUE,
    CONF_MODE_REGISTER,
    CONF_MODE_VENT_VALUE,
    CONF_OUTDOOR_TEMP_REGISTER,
    CONF_POWER_REGISTER,
    CONF_READ_ONLY,
    CONF_SCAN_INTERVAL,
    CONF_SLAVE_ID,
    CONF_SUPPLY_TEMP_DIVISOR,
    CONF_SUPPLY_TEMP_REGISTER,
    CONF_TARGET_TEMP_REGISTER,
    CONF_TEMPERATURE_DIVISOR,
    DEFAULT_ALARM_REGISTER,
    DEFAULT_FAN_SPEED_REGISTER,
    DEFAULT_MAX_HEAT_TEMP_REGISTER,
    DEFAULT_MAX_FAN_SPEED,
    DEFAULT_MIN_HEAT_TEMP_REGISTER,
    DEFAULT_MODE_HEAT_VALUE,
    DEFAULT_MODE_REGISTER,
    DEFAULT_MODE_VENT_VALUE,
    DEFAULT_OUTDOOR_TEMP_REGISTER,
    DEFAULT_PORT,
    DEFAULT_POWER_REGISTER,
    DEFAULT_READ_ONLY,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_SLAVE_ID,
    DEFAULT_SUPPLY_TEMP_DIVISOR,
    DEFAULT_SUPPLY_TEMP_REGISTER,
    DEFAULT_TARGET_TEMP_REGISTER,
    DEFAULT_TEMPERATURE_DIVISOR,
    DOMAIN,
)

CONF_ADVANCED_OPTIONS = "advanced_options"


class ZentecConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Zentec 031."""

    VERSION = 1

    def __init__(self) -> None:
        self._user_input: dict[str, Any] = {}

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        errors: dict[str, str] = {}

        if user_input is not None:
            is_ok = await self.hass.async_add_executor_job(
                _can_connect,
                user_input[CONF_HOST],
                int(user_input[CONF_PORT]),
            )
            if not is_ok:
                errors["base"] = "cannot_connect"
            else:
                self._user_input = {
                    CONF_NAME: user_input[CONF_NAME],
                    CONF_HOST: user_input[CONF_HOST],
                    CONF_PORT: int(user_input[CONF_PORT]),
                }
                if bool(user_input.get(CONF_ADVANCED_OPTIONS)):
                    return await self.async_step_advanced()
                return await self._async_create_final_entry({})

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_NAME, default="Zentec 031"): str,
                    vol.Required(CONF_HOST): str,
                    vol.Required(CONF_PORT, default=DEFAULT_PORT): vol.All(vol.Coerce(int), vol.Range(min=1, max=65535)),
                    vol.Optional(CONF_ADVANCED_OPTIONS, default=False): bool,
                }
            ),
            errors=errors,
        )

    async def async_step_advanced(self, user_input: dict[str, Any] | None = None):
        if user_input is not None:
            return await self._async_create_final_entry(user_input)

        return self.async_show_form(
            step_id="advanced",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_SLAVE_ID, default=DEFAULT_SLAVE_ID): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=0,
                            max=247,
                            step=1,
                            mode=selector.NumberSelectorMode.BOX,
                        )
                    ),
                    vol.Required(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): vol.All(vol.Coerce(int), vol.Range(min=5, max=3600)),
                    vol.Required(CONF_POWER_REGISTER, default=DEFAULT_POWER_REGISTER): vol.All(
                        vol.Coerce(int), vol.Range(min=0, max=65535)
                    ),
                    vol.Required(CONF_MODE_REGISTER, default=DEFAULT_MODE_REGISTER): vol.All(
                        vol.Coerce(int), vol.Range(min=0, max=65535)
                    ),
                    vol.Required(CONF_MODE_HEAT_VALUE, default=DEFAULT_MODE_HEAT_VALUE): vol.All(
                        vol.Coerce(int), vol.Range(min=0, max=65535)
                    ),
                    vol.Required(CONF_MODE_VENT_VALUE, default=DEFAULT_MODE_VENT_VALUE): vol.All(
                        vol.Coerce(int), vol.Range(min=0, max=65535)
                    ),
                    vol.Required(CONF_FAN_SPEED_REGISTER, default=DEFAULT_FAN_SPEED_REGISTER): vol.All(
                        vol.Coerce(int), vol.Range(min=0, max=65535)
                    ),
                    vol.Required(CONF_TARGET_TEMP_REGISTER, default=DEFAULT_TARGET_TEMP_REGISTER): vol.All(
                        vol.Coerce(int), vol.Range(min=0, max=65535)
                    ),
                    vol.Required(CONF_MIN_HEAT_TEMP_REGISTER, default=DEFAULT_MIN_HEAT_TEMP_REGISTER): vol.All(
                        vol.Coerce(int), vol.Range(min=0, max=65535)
                    ),
                    vol.Required(CONF_MAX_HEAT_TEMP_REGISTER, default=DEFAULT_MAX_HEAT_TEMP_REGISTER): vol.All(
                        vol.Coerce(int), vol.Range(min=0, max=65535)
                    ),
                    vol.Required(CONF_SUPPLY_TEMP_REGISTER, default=DEFAULT_SUPPLY_TEMP_REGISTER): vol.All(
                        vol.Coerce(int), vol.Range(min=0, max=65535)
                    ),
                    vol.Required(CONF_SUPPLY_TEMP_DIVISOR, default=DEFAULT_SUPPLY_TEMP_DIVISOR): vol.All(
                        vol.Coerce(int), vol.Range(min=1, max=1000)
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
                    vol.Required(CONF_MAX_FAN_SPEED, default=DEFAULT_MAX_FAN_SPEED): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=1,
                            max=20,
                            step=1,
                            mode=selector.NumberSelectorMode.BOX,
                        )
                    ),
                    vol.Required(CONF_READ_ONLY, default=DEFAULT_READ_ONLY): bool,
                }
            ),
        )

    async def _async_create_final_entry(self, advanced: dict[str, Any]) -> config_entries.ConfigFlowResult:
        data = {
            CONF_NAME: self._user_input[CONF_NAME],
            CONF_HOST: self._user_input[CONF_HOST],
            CONF_PORT: int(self._user_input[CONF_PORT]),
            CONF_SLAVE_ID: int(advanced.get(CONF_SLAVE_ID, DEFAULT_SLAVE_ID)),
            CONF_SCAN_INTERVAL: int(advanced.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)),
            CONF_POWER_REGISTER: int(advanced.get(CONF_POWER_REGISTER, DEFAULT_POWER_REGISTER)),
            CONF_MODE_REGISTER: int(advanced.get(CONF_MODE_REGISTER, DEFAULT_MODE_REGISTER)),
            CONF_MODE_HEAT_VALUE: int(advanced.get(CONF_MODE_HEAT_VALUE, DEFAULT_MODE_HEAT_VALUE)),
            CONF_MODE_VENT_VALUE: int(advanced.get(CONF_MODE_VENT_VALUE, DEFAULT_MODE_VENT_VALUE)),
            CONF_FAN_SPEED_REGISTER: int(advanced.get(CONF_FAN_SPEED_REGISTER, DEFAULT_FAN_SPEED_REGISTER)),
            CONF_TARGET_TEMP_REGISTER: int(advanced.get(CONF_TARGET_TEMP_REGISTER, DEFAULT_TARGET_TEMP_REGISTER)),
            CONF_MIN_HEAT_TEMP_REGISTER: int(advanced.get(CONF_MIN_HEAT_TEMP_REGISTER, DEFAULT_MIN_HEAT_TEMP_REGISTER)),
            CONF_MAX_HEAT_TEMP_REGISTER: int(advanced.get(CONF_MAX_HEAT_TEMP_REGISTER, DEFAULT_MAX_HEAT_TEMP_REGISTER)),
            CONF_SUPPLY_TEMP_REGISTER: int(advanced.get(CONF_SUPPLY_TEMP_REGISTER, DEFAULT_SUPPLY_TEMP_REGISTER)),
            CONF_SUPPLY_TEMP_DIVISOR: int(advanced.get(CONF_SUPPLY_TEMP_DIVISOR, DEFAULT_SUPPLY_TEMP_DIVISOR)),
            CONF_OUTDOOR_TEMP_REGISTER: int(advanced.get(CONF_OUTDOOR_TEMP_REGISTER, DEFAULT_OUTDOOR_TEMP_REGISTER)),
            CONF_ALARM_REGISTER: int(advanced.get(CONF_ALARM_REGISTER, DEFAULT_ALARM_REGISTER)),
            CONF_TEMPERATURE_DIVISOR: int(advanced.get(CONF_TEMPERATURE_DIVISOR, DEFAULT_TEMPERATURE_DIVISOR)),
            CONF_MAX_FAN_SPEED: int(advanced.get(CONF_MAX_FAN_SPEED, DEFAULT_MAX_FAN_SPEED)),
            CONF_READ_ONLY: bool(advanced.get(CONF_READ_ONLY, DEFAULT_READ_ONLY)),
        }

        await self.async_set_unique_id(f"{data[CONF_HOST]}:{data[CONF_PORT]}:{data[CONF_SLAVE_ID]}")
        self._abort_if_unique_id_configured()
        return self.async_create_entry(title=data[CONF_NAME], data=data)

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
                        CONF_MODE_REGISTER,
                        default=int(options.get(CONF_MODE_REGISTER, data.get(CONF_MODE_REGISTER, DEFAULT_MODE_REGISTER))),
                    ): vol.All(vol.Coerce(int), vol.Range(min=0, max=65535)),
                    vol.Required(
                        CONF_MODE_HEAT_VALUE,
                        default=int(options.get(CONF_MODE_HEAT_VALUE, data.get(CONF_MODE_HEAT_VALUE, DEFAULT_MODE_HEAT_VALUE))),
                    ): vol.All(vol.Coerce(int), vol.Range(min=0, max=65535)),
                    vol.Required(
                        CONF_MODE_VENT_VALUE,
                        default=int(options.get(CONF_MODE_VENT_VALUE, data.get(CONF_MODE_VENT_VALUE, DEFAULT_MODE_VENT_VALUE))),
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
                        CONF_MIN_HEAT_TEMP_REGISTER,
                        default=int(
                            options.get(
                                CONF_MIN_HEAT_TEMP_REGISTER,
                                data.get(CONF_MIN_HEAT_TEMP_REGISTER, DEFAULT_MIN_HEAT_TEMP_REGISTER),
                            )
                        ),
                    ): vol.All(vol.Coerce(int), vol.Range(min=0, max=65535)),
                    vol.Required(
                        CONF_MAX_HEAT_TEMP_REGISTER,
                        default=int(
                            options.get(
                                CONF_MAX_HEAT_TEMP_REGISTER,
                                data.get(CONF_MAX_HEAT_TEMP_REGISTER, DEFAULT_MAX_HEAT_TEMP_REGISTER),
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
                        CONF_SUPPLY_TEMP_DIVISOR,
                        default=int(
                            options.get(
                                CONF_SUPPLY_TEMP_DIVISOR,
                                data.get(CONF_SUPPLY_TEMP_DIVISOR, DEFAULT_SUPPLY_TEMP_DIVISOR),
                            )
                        ),
                    ): vol.All(vol.Coerce(int), vol.Range(min=1, max=1000)),
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
                    ): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=1,
                            max=20,
                            step=1,
                            mode=selector.NumberSelectorMode.BOX,
                        )
                    ),
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
