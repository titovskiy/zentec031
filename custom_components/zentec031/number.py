"""Number platform for Zentec 031."""

from __future__ import annotations

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .entity import ZentecEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = entry.runtime_data
    async_add_entities(
        [
            ZentecMinHeatTemperatureSetting(coordinator, entry),
            ZentecMaxHeatTemperatureSetting(coordinator, entry),
        ]
    )


class ZentecMinHeatTemperatureSetting(ZentecEntity, NumberEntity):
    """Minimum heating temperature setting (B0)."""

    _attr_name = "Min Heating Temperature"
    _attr_entity_category = EntityCategory.CONFIG
    _attr_mode = NumberMode.BOX
    _attr_native_min_value = 5
    _attr_native_max_value = 60
    _attr_native_step = 1
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS

    @property
    def unique_id(self) -> str:
        return f"{self._entry.entry_id}_min_heat_temp"

    @property
    def native_value(self) -> float | None:
        return self.coordinator.data.min_heat_temp if self.coordinator.data else None

    async def async_set_native_value(self, value: float) -> None:
        await self.coordinator.async_set_min_heat_temp(value)


class ZentecMaxHeatTemperatureSetting(ZentecEntity, NumberEntity):
    """Maximum heating temperature setting (B1)."""

    _attr_name = "Max Heating Temperature"
    _attr_entity_category = EntityCategory.CONFIG
    _attr_mode = NumberMode.BOX
    _attr_native_min_value = 5
    _attr_native_max_value = 60
    _attr_native_step = 1
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS

    @property
    def unique_id(self) -> str:
        return f"{self._entry.entry_id}_max_heat_temp"

    @property
    def native_value(self) -> float | None:
        return self.coordinator.data.max_heat_temp if self.coordinator.data else None

    async def async_set_native_value(self, value: float) -> None:
        await self.coordinator.async_set_max_heat_temp(value)
