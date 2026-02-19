"""Number platform for Zentec 031."""

from __future__ import annotations

from homeassistant.components.number import NumberEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .entity import ZentecEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = entry.runtime_data
    async_add_entities([ZentecTargetTemperature(coordinator, entry)])


class ZentecTargetTemperature(ZentecEntity, NumberEntity):
    """Target temperature setting."""

    _attr_name = "Target Temperature"
    _attr_native_min_value = 10
    _attr_native_max_value = 30
    _attr_native_step = 0.5
    _attr_native_unit_of_measurement = "°C"

    @property
    def unique_id(self) -> str:
        return f"{self._entry.entry_id}_target_temp"

    @property
    def native_value(self) -> float | None:
        return self.coordinator.data.target_temp if self.coordinator.data else None

    async def async_set_native_value(self, value: float) -> None:
        await self.coordinator.async_set_target_temp(value)
