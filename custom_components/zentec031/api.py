"""Modbus API wrapper for Zentec 031."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from pymodbus.client import ModbusTcpClient

from .const import (
    CONF_ALARM_REGISTER,
    CONF_FAN_SPEED_REGISTER,
    CONF_MAX_FAN_SPEED,
    CONF_OUTDOOR_TEMP_REGISTER,
    CONF_POWER_REGISTER,
    CONF_SLAVE_ID,
    CONF_SUPPLY_TEMP_REGISTER,
    CONF_TARGET_TEMP_REGISTER,
    CONF_TEMPERATURE_DIVISOR,
)


@dataclass(slots=True)
class ZentecState:
    """Current controller state."""

    power: bool | None = None
    fan_speed: int | None = None
    target_temp: float | None = None
    supply_temp: float | None = None
    outdoor_temp: float | None = None
    alarm_code: int | None = None


class ZentecModbusApi:
    """Thin async-friendly wrapper over blocking pymodbus client."""

    def __init__(self, host: str, port: int, config: dict[str, Any]) -> None:
        self._client = ModbusTcpClient(host=host, port=port, timeout=2, retries=1)
        self._config = config

    @property
    def config(self) -> dict[str, Any]:
        """Return runtime config."""
        return self._config

    def close(self) -> None:
        """Close client socket."""
        self._client.close()

    def read_state(self) -> ZentecState:
        """Read all key values from controller."""
        unit = self._config[CONF_SLAVE_ID]
        divisor = max(int(self._config[CONF_TEMPERATURE_DIVISOR]), 1)
        reg_map = {
            "power": int(self._config[CONF_POWER_REGISTER]),
            "fan_speed": int(self._config[CONF_FAN_SPEED_REGISTER]),
            "target_temp": int(self._config[CONF_TARGET_TEMP_REGISTER]),
            "supply_temp": int(self._config[CONF_SUPPLY_TEMP_REGISTER]),
            "outdoor_temp": int(self._config[CONF_OUTDOOR_TEMP_REGISTER]),
            "alarm_code": int(self._config[CONF_ALARM_REGISTER]),
        }
        min_reg = min(reg_map.values())
        max_reg = max(reg_map.values())

        registers = self._read_register_block(min_reg, max_reg - min_reg + 1, unit)
        power_raw = self._block_value(registers, min_reg, reg_map["power"])

        fan_speed = self._block_value(registers, min_reg, reg_map["fan_speed"])
        target_temp_raw = self._block_value(registers, min_reg, reg_map["target_temp"])
        supply_temp_raw = self._block_value(registers, min_reg, reg_map["supply_temp"])
        outdoor_temp_raw = self._block_value(registers, min_reg, reg_map["outdoor_temp"])
        alarm_code = self._block_value(registers, min_reg, reg_map["alarm_code"])

        return ZentecState(
            power=bool(power_raw) if power_raw is not None else None,
            fan_speed=fan_speed,
            target_temp=self._to_temp(target_temp_raw, divisor),
            supply_temp=self._to_temp(supply_temp_raw, divisor),
            outdoor_temp=self._to_temp(outdoor_temp_raw, divisor),
            alarm_code=alarm_code,
        )

    def set_power(self, enabled: bool) -> None:
        """Write power state to holding register."""
        unit = self._config[CONF_SLAVE_ID]
        self._ensure_client_connected()
        self._client.write_register(
            address=self._config[CONF_POWER_REGISTER],
            value=1 if enabled else 0,
            device_id=unit,
        )

    def set_fan_speed(self, fan_speed: int) -> None:
        """Write fan speed to holding register."""
        max_speed = max(int(self._config[CONF_MAX_FAN_SPEED]), 1)
        fan_speed = max(1, min(fan_speed, max_speed))
        unit = self._config[CONF_SLAVE_ID]

        self._ensure_client_connected()
        self._client.write_register(
            address=self._config[CONF_FAN_SPEED_REGISTER],
            value=fan_speed,
            device_id=unit,
        )

    def set_target_temp(self, target_temp: float) -> None:
        """Write target air temperature to holding register."""
        divisor = max(int(self._config[CONF_TEMPERATURE_DIVISOR]), 1)
        value = int(round(target_temp * divisor))
        unit = self._config[CONF_SLAVE_ID]

        self._ensure_client_connected()
        self._client.write_register(
            address=self._config[CONF_TARGET_TEMP_REGISTER],
            value=value,
            device_id=unit,
        )

    def _read_register_block(self, address: int, count: int, unit: int) -> list[int] | None:
        self._ensure_client_connected()
        result = self._client.read_holding_registers(address=address, count=count, device_id=unit)
        if result.isError() or not getattr(result, "registers", None):
            return None
        return [int(value) for value in result.registers]

    def _ensure_client_connected(self) -> None:
        if not self._client.connected:
            self._client.connect()

    @staticmethod
    def _to_temp(value: int | None, divisor: int) -> float | None:
        if value is None:
            return None
        return round(value / divisor, 1)

    @staticmethod
    def _block_value(block: list[int] | None, base_address: int, address: int) -> int | None:
        if block is None:
            return None
        index = address - base_address
        if index < 0 or index >= len(block):
            return None
        return int(block[index])
