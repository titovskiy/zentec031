"""Sensor platform for Zentec 031."""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
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
            ZentecSupplyTemperatureSensor(coordinator, entry),
            ZentecOutdoorTemperatureSensor(coordinator, entry),
            ZentecAlarmCodeSensor(coordinator, entry),
            ZentecAlarmCode2DiagnosticSensor(coordinator, entry),
            ZentecAlarmCode3DiagnosticSensor(coordinator, entry),
            ZentecPowerRawDiagnosticSensor(coordinator, entry),
            ZentecModeRawDiagnosticSensor(coordinator, entry),
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


class ZentecAlarmCode2DiagnosticSensor(ZentecEntity, SensorEntity):
    """Alarm register 2 (17-32) diagnostic sensor."""

    _attr_name = "Alarm Code 17-32"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def unique_id(self) -> str:
        return f"{self._entry.entry_id}_alarm_code_2"

    @property
    def native_value(self) -> int | None:
        return self.coordinator.data.alarm_code_2 if self.coordinator.data else None


class ZentecAlarmCode3DiagnosticSensor(ZentecEntity, SensorEntity):
    """Alarm register 3 (33-48) diagnostic sensor."""

    _attr_name = "Alarm Code 33-48"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def unique_id(self) -> str:
        return f"{self._entry.entry_id}_alarm_code_3"

    @property
    def native_value(self) -> int | None:
        return self.coordinator.data.alarm_code_3 if self.coordinator.data else None


class ZentecPowerRawDiagnosticSensor(ZentecEntity, SensorEntity):
    """Power register raw value diagnostic sensor."""

    _attr_name = "Power Raw"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def unique_id(self) -> str:
        return f"{self._entry.entry_id}_power_raw"

    @property
    def native_value(self) -> int | None:
        return self.coordinator.data.power_raw if self.coordinator.data else None


class ZentecModeRawDiagnosticSensor(ZentecEntity, SensorEntity):
    """Mode register raw value diagnostic sensor."""

    _attr_name = "Mode Raw"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def unique_id(self) -> str:
        return f"{self._entry.entry_id}_mode_raw"

    @property
    def native_value(self) -> int | None:
        return self.coordinator.data.mode_raw if self.coordinator.data else None
