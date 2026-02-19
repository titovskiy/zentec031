"""The Zentec 031 integration."""

from __future__ import annotations

from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant

from .api import ZentecModbusApi
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
    PLATFORMS,
)
from .coordinator import ZentecCoordinator

_LOGGER = logging.getLogger(__name__)


def _build_runtime_config(entry: ConfigEntry) -> dict[str, int | bool]:
    data = entry.data
    options = entry.options
    return {
        CONF_SLAVE_ID: int(data.get(CONF_SLAVE_ID, DEFAULT_SLAVE_ID)),
        CONF_SCAN_INTERVAL: int(options.get(CONF_SCAN_INTERVAL, data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL))),
        CONF_POWER_REGISTER: int(
            options.get(CONF_POWER_REGISTER, data.get(CONF_POWER_REGISTER, data.get("power_coil", DEFAULT_POWER_REGISTER)))
        ),
        CONF_MODE_REGISTER: int(options.get(CONF_MODE_REGISTER, data.get(CONF_MODE_REGISTER, DEFAULT_MODE_REGISTER))),
        CONF_MODE_HEAT_VALUE: int(options.get(CONF_MODE_HEAT_VALUE, data.get(CONF_MODE_HEAT_VALUE, DEFAULT_MODE_HEAT_VALUE))),
        CONF_MODE_VENT_VALUE: int(options.get(CONF_MODE_VENT_VALUE, data.get(CONF_MODE_VENT_VALUE, DEFAULT_MODE_VENT_VALUE))),
        CONF_FAN_SPEED_REGISTER: int(
            options.get(CONF_FAN_SPEED_REGISTER, data.get(CONF_FAN_SPEED_REGISTER, DEFAULT_FAN_SPEED_REGISTER))
        ),
        CONF_TARGET_TEMP_REGISTER: int(
            options.get(CONF_TARGET_TEMP_REGISTER, data.get(CONF_TARGET_TEMP_REGISTER, DEFAULT_TARGET_TEMP_REGISTER))
        ),
        CONF_MIN_HEAT_TEMP_REGISTER: int(
            options.get(CONF_MIN_HEAT_TEMP_REGISTER, data.get(CONF_MIN_HEAT_TEMP_REGISTER, DEFAULT_MIN_HEAT_TEMP_REGISTER))
        ),
        CONF_MAX_HEAT_TEMP_REGISTER: int(
            options.get(CONF_MAX_HEAT_TEMP_REGISTER, data.get(CONF_MAX_HEAT_TEMP_REGISTER, DEFAULT_MAX_HEAT_TEMP_REGISTER))
        ),
        CONF_SUPPLY_TEMP_REGISTER: int(
            options.get(CONF_SUPPLY_TEMP_REGISTER, data.get(CONF_SUPPLY_TEMP_REGISTER, DEFAULT_SUPPLY_TEMP_REGISTER))
        ),
        CONF_SUPPLY_TEMP_DIVISOR: int(
            options.get(CONF_SUPPLY_TEMP_DIVISOR, data.get(CONF_SUPPLY_TEMP_DIVISOR, DEFAULT_SUPPLY_TEMP_DIVISOR))
        ),
        CONF_OUTDOOR_TEMP_REGISTER: int(
            options.get(CONF_OUTDOOR_TEMP_REGISTER, data.get(CONF_OUTDOOR_TEMP_REGISTER, DEFAULT_OUTDOOR_TEMP_REGISTER))
        ),
        CONF_ALARM_REGISTER: int(options.get(CONF_ALARM_REGISTER, data.get(CONF_ALARM_REGISTER, DEFAULT_ALARM_REGISTER))),
        CONF_TEMPERATURE_DIVISOR: int(
            options.get(CONF_TEMPERATURE_DIVISOR, data.get(CONF_TEMPERATURE_DIVISOR, DEFAULT_TEMPERATURE_DIVISOR))
        ),
        CONF_MAX_FAN_SPEED: int(options.get(CONF_MAX_FAN_SPEED, data.get(CONF_MAX_FAN_SPEED, DEFAULT_MAX_FAN_SPEED))),
        CONF_READ_ONLY: bool(options.get(CONF_READ_ONLY, data.get(CONF_READ_ONLY, DEFAULT_READ_ONLY))),
    }


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Zentec 031 from a config entry."""
    config = _build_runtime_config(entry)

    api = ZentecModbusApi(
        host=entry.data[CONF_HOST],
        port=int(entry.data.get(CONF_PORT, DEFAULT_PORT)),
        config=config,
    )

    coordinator = ZentecCoordinator(
        hass=hass,
        api=api,
        update_interval=timedelta(seconds=config[CONF_SCAN_INTERVAL]),
        name=f"{DOMAIN}_{entry.entry_id}",
    )

    await coordinator.async_refresh()
    if not coordinator.last_update_success:
        _LOGGER.warning(
            "Initial Zentec poll failed; setup will continue and entities remain unavailable until connection recovers"
        )

    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload Zentec entry."""
    coordinator: ZentecCoordinator = entry.runtime_data
    coordinator.api.close()
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload entry on options update."""
    await hass.config_entries.async_reload(entry.entry_id)
