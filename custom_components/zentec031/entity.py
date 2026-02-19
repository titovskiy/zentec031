"""Shared entity class for Zentec 031."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import ZentecCoordinator


class ZentecEntity(CoordinatorEntity[ZentecCoordinator]):
    """Base entity for Zentec devices."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: ZentecCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._entry = entry
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="Zentec 031",
            manufacturer="Zentec",
            model="031",
            configuration_url=f"http://{entry.data[CONF_HOST]}",
        )
