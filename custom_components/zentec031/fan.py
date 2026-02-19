"""Fan platform for Zentec 031."""

from __future__ import annotations

from typing import Any

from homeassistant.components.fan import FanEntity, FanEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CONF_MAX_FAN_SPEED, DEFAULT_MAX_FAN_SPEED
from .entity import ZentecEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = entry.runtime_data
    async_add_entities([ZentecFan(coordinator, entry)])


class ZentecFan(ZentecEntity, FanEntity):
    """Fan speed entity."""

    _attr_name = "Fan"
    _attr_supported_features = (
        FanEntityFeature.SET_SPEED
        | FanEntityFeature.PRESET_MODE
        | FanEntityFeature.TURN_ON
        | FanEntityFeature.TURN_OFF
    )

    def __init__(self, coordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry)
        self._max_speed = int(entry.options.get(CONF_MAX_FAN_SPEED, entry.data.get(CONF_MAX_FAN_SPEED, DEFAULT_MAX_FAN_SPEED)))
        self._attr_preset_modes = [str(speed) for speed in range(1, self._max_speed + 1)]

    @property
    def unique_id(self) -> str:
        return f"{self._entry.entry_id}_fan"

    @property
    def is_on(self) -> bool | None:
        return self.coordinator.data.power if self.coordinator.data else None

    @property
    def speed_count(self) -> int:
        return self._max_speed

    @property
    def percentage(self) -> int | None:
        speed = self.coordinator.data.fan_speed if self.coordinator.data else None
        if speed is None:
            return None
        return round((speed / self._max_speed) * 100)

    @property
    def preset_mode(self) -> str | None:
        if not self.coordinator.data:
            return None
        speed = self.coordinator.data.fan_speed
        if speed is None or speed < 1 or speed > self._max_speed:
            return None
        return str(speed)

    async def async_set_percentage(self, percentage: int) -> None:
        if percentage <= 0:
            await self.coordinator.async_set_power(True)
            await self.coordinator.async_set_fan_speed(1)
            return
        await self.coordinator.async_set_power(True)
        speed = max(1, round((percentage / 100) * self._max_speed))
        await self.coordinator.async_set_fan_speed(speed)

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        try:
            speed = int(preset_mode)
        except ValueError as err:
            raise HomeAssistantError(f"Unsupported preset mode: {preset_mode}") from err
        speed = max(1, min(speed, self._max_speed))
        await self.coordinator.async_set_power(True)
        await self.coordinator.async_set_fan_speed(speed)

    async def async_turn_on(
        self, percentage: int | None = None, preset_mode: str | None = None, **kwargs: Any
    ) -> None:
        await self.coordinator.async_set_power(True)
        if percentage is not None:
            await self.async_set_percentage(percentage)

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.coordinator.async_set_power(True)
        await self.coordinator.async_set_fan_speed(1)
