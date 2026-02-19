"""Data coordinator for Zentec 031 integration."""

from __future__ import annotations

from dataclasses import fields
from datetime import timedelta
import logging
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import ZentecModbusApi, ZentecState
from .const import CONF_READ_ONLY

_LOGGER = logging.getLogger(__name__)


class ZentecCoordinator(DataUpdateCoordinator[ZentecState]):
    """Coordinate data updates and writes for Zentec controller."""

    def __init__(
        self,
        hass: HomeAssistant,
        api: ZentecModbusApi,
        update_interval: timedelta,
        name: str,
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=name,
            update_interval=update_interval,
        )
        self.api = api

    async def _async_update_data(self) -> ZentecState:
        try:
            new_state = await self.hass.async_add_executor_job(self.api.read_state)
            if self.data is None:
                return new_state
            return ZentecState(
                **{
                    field.name: getattr(new_state, field.name)
                    if getattr(new_state, field.name) is not None
                    else getattr(self.data, field.name)
                    for field in fields(ZentecState)
                }
            )
        except Exception as err:  # noqa: BLE001
            raise UpdateFailed(f"Failed to update Zentec data: {err}") from err

    async def async_set_power(self, enabled: bool) -> None:
        await self._async_write(self.api.set_power, enabled)

    async def async_set_fan_speed(self, fan_speed: int) -> None:
        await self._async_write(self.api.set_fan_speed, fan_speed)

    async def async_set_mode_value(self, mode_value: int) -> None:
        await self._async_write(self.api.set_mode, mode_value)

    async def async_set_target_temp(self, target_temp: float) -> None:
        await self._async_write(self.api.set_target_temp, target_temp)

    async def async_set_min_heat_temp(self, value: float) -> None:
        await self._async_write(self.api.set_min_heat_temp, value)

    async def async_set_max_heat_temp(self, value: float) -> None:
        await self._async_write(self.api.set_max_heat_temp, value)

    async def _async_write(self, method: Any, *args: Any) -> None:
        if bool(self.api.config.get(CONF_READ_ONLY, False)):
            raise HomeAssistantError("Zentec integration is in read-only mode")
        try:
            await self.hass.async_add_executor_job(method, *args)
        except Exception as err:  # noqa: BLE001
            raise HomeAssistantError(f"Failed to write Zentec setting: {err}") from err
        await self.async_request_refresh()
