"""Climate platform for Zentec 031."""

from __future__ import annotations

from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import (
    HVACAction,
    HVACMode,
    ClimateEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    CONF_MAX_FAN_SPEED,
    CONF_MODE_HEAT_VALUE,
    CONF_MODE_VENT_VALUE,
    DEFAULT_MAX_FAN_SPEED,
    DEFAULT_MODE_HEAT_VALUE,
    DEFAULT_MODE_VENT_VALUE,
)
from .entity import ZentecEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = entry.runtime_data
    async_add_entities([ZentecClimate(coordinator, entry)])


class ZentecClimate(ZentecEntity, ClimateEntity):
    """Main climate controller entity."""

    _attr_name = "Climate"
    _attr_supported_features = (
        ClimateEntityFeature.TARGET_TEMPERATURE
        | ClimateEntityFeature.FAN_MODE
    )
    _attr_hvac_modes = [HVACMode.OFF, HVACMode.HEAT, HVACMode.FAN_ONLY]
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_min_temp = 10
    _attr_max_temp = 30
    _attr_target_temperature_step = 0.5

    def __init__(self, coordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry)
        self._heat_mode_value = int(
            entry.options.get(CONF_MODE_HEAT_VALUE, entry.data.get(CONF_MODE_HEAT_VALUE, DEFAULT_MODE_HEAT_VALUE))
        )
        self._vent_mode_value = int(
            entry.options.get(CONF_MODE_VENT_VALUE, entry.data.get(CONF_MODE_VENT_VALUE, DEFAULT_MODE_VENT_VALUE))
        )
        self._max_speed = int(entry.options.get(CONF_MAX_FAN_SPEED, entry.data.get(CONF_MAX_FAN_SPEED, DEFAULT_MAX_FAN_SPEED)))
        self._attr_fan_modes = [str(speed) for speed in range(1, self._max_speed + 1)]

    @property
    def unique_id(self) -> str:
        return f"{self._entry.entry_id}_climate"

    @property
    def current_temperature(self) -> float | None:
        return self.coordinator.data.supply_temp if self.coordinator.data else None

    @property
    def target_temperature(self) -> float | None:
        return self.coordinator.data.target_temp if self.coordinator.data else None

    @property
    def fan_mode(self) -> str | None:
        if not self.coordinator.data:
            return None
        speed = self.coordinator.data.fan_speed
        if speed is None or speed < 1 or speed > self._max_speed:
            return None
        return str(speed)

    @property
    def hvac_mode(self) -> HVACMode:
        if not self.coordinator.data:
            return HVACMode.OFF

        if not self.coordinator.data.power:
            return HVACMode.OFF

        mode_raw = self.coordinator.data.mode_raw
        if mode_raw == self._heat_mode_value:
            return HVACMode.HEAT
        if mode_raw == self._vent_mode_value:
            return HVACMode.FAN_ONLY
        if mode_raw == 2:
            return HVACMode.HEAT
        if mode_raw == 1:
            return HVACMode.FAN_ONLY

        return HVACMode.FAN_ONLY

    @property
    def hvac_action(self) -> HVACAction | None:
        mode = self.hvac_mode
        if mode == HVACMode.OFF:
            return HVACAction.OFF
        if mode == HVACMode.FAN_ONLY:
            return HVACAction.FAN
        return HVACAction.HEATING

    async def async_set_temperature(self, **kwargs) -> None:
        temperature = kwargs.get("temperature")
        if temperature is not None:
            await self.coordinator.async_set_target_temp(float(temperature))

    async def async_set_fan_mode(self, fan_mode: str) -> None:
        try:
            speed = int(fan_mode)
        except ValueError:
            return
        speed = max(1, min(speed, self._max_speed))
        await self.coordinator.async_set_power(True)
        await self.coordinator.async_set_fan_speed(speed)

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        if hvac_mode == HVACMode.OFF:
            await self.coordinator.async_set_power(False)
            return

        await self.coordinator.async_set_power(True)
        if hvac_mode == HVACMode.FAN_ONLY:
            await self.coordinator.async_set_mode_value(self._vent_mode_value)
            return

        await self.coordinator.async_set_mode_value(self._heat_mode_value)
