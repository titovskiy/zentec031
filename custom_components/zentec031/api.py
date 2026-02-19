"""Modbus API wrapper for Zentec 031."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from pymodbus.client import ModbusTcpClient

from .const import (
    CONF_ALARM_REGISTER,
    CONF_FAN_SPEED_REGISTER,
    CONF_MAX_HEAT_TEMP_REGISTER,
    CONF_MAX_FAN_SPEED,
    CONF_MIN_HEAT_TEMP_REGISTER,
    CONF_MODE_REGISTER,
    CONF_OUTDOOR_TEMP_REGISTER,
    CONF_POWER_REGISTER,
    CONF_SLAVE_ID,
    CONF_SUPPLY_TEMP_DIVISOR,
    CONF_SUPPLY_TEMP_REGISTER,
    CONF_TARGET_TEMP_REGISTER,
    CONF_TEMPERATURE_DIVISOR,
)


@dataclass(slots=True)
class ZentecState:
    """Current controller state."""

    power: bool | None = None
    power_raw: int | None = None
    mode_raw: int | None = None
    fan_speed: int | None = None
    target_temp: float | None = None
    min_heat_temp: float | None = None
    max_heat_temp: float | None = None
    supply_temp: float | None = None
    outdoor_temp: float | None = None
    alarm_code: int | None = None
    alarm_code_2: int | None = None
    alarm_code_3: int | None = None


class ZentecModbusApi:
    """Thin async-friendly wrapper over blocking pymodbus client."""

    def __init__(self, host: str, port: int, config: dict[str, Any]) -> None:
        self._client = ModbusTcpClient(host=host, port=port, timeout=10, retries=3)
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
        supply_divisor = max(int(self._config[CONF_SUPPLY_TEMP_DIVISOR]), 1)
        reg_map = {
            "power": int(self._config[CONF_POWER_REGISTER]),
            "mode": int(self._config[CONF_MODE_REGISTER]),
            "fan_speed": int(self._config[CONF_FAN_SPEED_REGISTER]),
            "target_temp": int(self._config[CONF_TARGET_TEMP_REGISTER]),
            "min_heat_temp": int(self._config[CONF_MIN_HEAT_TEMP_REGISTER]),
            "max_heat_temp": int(self._config[CONF_MAX_HEAT_TEMP_REGISTER]),
            "supply_temp": int(self._config[CONF_SUPPLY_TEMP_REGISTER]),
            "outdoor_temp": int(self._config[CONF_OUTDOOR_TEMP_REGISTER]),
            "alarm_code": int(self._config[CONF_ALARM_REGISTER]),
            "alarm_code_2": int(self._config[CONF_ALARM_REGISTER]) + 1,
            "alarm_code_3": int(self._config[CONF_ALARM_REGISTER]) + 2,
        }
        values = {key: self._read_register(address, unit) for key, address in reg_map.items()}
        power_raw = values["power"]
        mode_raw = values["mode"]
        fan_speed = values["fan_speed"]
        target_temp_raw = values["target_temp"]
        min_heat_temp_raw = values["min_heat_temp"]
        max_heat_temp_raw = values["max_heat_temp"]
        supply_temp_raw = values["supply_temp"]
        outdoor_temp_raw = values["outdoor_temp"]
        alarm_code = values["alarm_code"]
        alarm_code_2 = values["alarm_code_2"]
        alarm_code_3 = values["alarm_code_3"]

        return ZentecState(
            power=bool(power_raw) if power_raw is not None else None,
            power_raw=power_raw,
            mode_raw=mode_raw,
            fan_speed=fan_speed,
            target_temp=self._to_temp(target_temp_raw, divisor),
            min_heat_temp=self._to_temp(min_heat_temp_raw, divisor),
            max_heat_temp=self._to_temp(max_heat_temp_raw, divisor),
            supply_temp=self._to_temp(supply_temp_raw, supply_divisor),
            outdoor_temp=self._to_temp(outdoor_temp_raw, divisor),
            alarm_code=alarm_code,
            alarm_code_2=alarm_code_2,
            alarm_code_3=alarm_code_3,
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

    def set_mode(self, mode_value: int) -> None:
        """Write operation mode to holding register."""
        unit = self._config[CONF_SLAVE_ID]
        self._ensure_client_connected()
        self._client.write_register(
            address=self._config[CONF_MODE_REGISTER],
            value=mode_value,
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

    def set_min_heat_temp(self, value: float) -> None:
        """Write minimum heating setpoint."""
        divisor = max(int(self._config[CONF_TEMPERATURE_DIVISOR]), 1)
        raw = int(round(value * divisor))
        unit = self._config[CONF_SLAVE_ID]
        self._ensure_client_connected()
        self._client.write_register(
            address=self._config[CONF_MIN_HEAT_TEMP_REGISTER],
            value=raw,
            device_id=unit,
        )

    def set_max_heat_temp(self, value: float) -> None:
        """Write maximum heating setpoint."""
        divisor = max(int(self._config[CONF_TEMPERATURE_DIVISOR]), 1)
        raw = int(round(value * divisor))
        unit = self._config[CONF_SLAVE_ID]
        self._ensure_client_connected()
        self._client.write_register(
            address=self._config[CONF_MAX_HEAT_TEMP_REGISTER],
            value=raw,
            device_id=unit,
        )

    def _read_register(self, address: int, unit: int) -> int | None:
        try:
            self._ensure_client_connected()
            if 30000 <= address < 40000:
                result = self._client.read_input_registers(address=address, count=1, device_id=unit)
            else:
                result = self._client.read_holding_registers(address=address, count=1, device_id=unit)
        except Exception:  # noqa: BLE001
            return None
        if result.isError() or not getattr(result, "registers", None):
            return None
        return int(result.registers[0])

    def _ensure_client_connected(self) -> None:
        if not self._client.connected:
            self._client.connect()

    @staticmethod
    def _to_temp(value: int | None, divisor: int) -> float | None:
        if value is None:
            return None
        return round(value / divisor, 1)
