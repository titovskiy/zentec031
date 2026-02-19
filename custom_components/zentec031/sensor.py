"""Sensor platform for Zentec 031."""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
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
            ZentecSupplyTemperatureSensor(coordinator, entry),
            ZentecOutdoorTemperatureSensor(coordinator, entry),
            ZentecAlarmCodeSensor(coordinator, entry),
        ]
    )


class ZentecSupplyTemperatureSensor(ZentecEntity, SensorEntity):
    """Supply temperature."""

    _attr_name = "Supply Temperature"
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_device_class = SensorDeviceClass.TEMPERATURE

    @property
    def unique_id(self) -> str:
        return f"{self._entry.entry_id}_supply_temp"

    @property
    def native_value(self) -> float | None:
        return self.coordinator.data.supply_temp if self.coordinator.data else None


class ZentecOutdoorTemperatureSensor(ZentecEntity, SensorEntity):
    """Outdoor temperature."""

    _attr_name = "Outdoor Temperature"
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_device_class = SensorDeviceClass.TEMPERATURE

    @property
    def unique_id(self) -> str:
        return f"{self._entry.entry_id}_outdoor_temp"

    @property
    def native_value(self) -> float | None:
        return self.coordinator.data.outdoor_temp if self.coordinator.data else None


class ZentecAlarmCodeSensor(ZentecEntity, SensorEntity):
    """Current alarm code from controller."""

    _attr_name = "Alarm Code"

    @property
    def unique_id(self) -> str:
        return f"{self._entry.entry_id}_alarm_code"

    @property
    def native_value(self) -> int | None:
        return self.coordinator.data.alarm_code if self.coordinator.data else None
