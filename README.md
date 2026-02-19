# Zentec 031 Home Assistant Custom Integration

Кастомная интеграция `zentec031` для управления приточной установкой через Modbus TCP.

Извлеченная карта регистров: `docs/register_map_extracted.md`.

## Что реализовано

- UI-настройка через `Settings -> Devices & Services -> Add Integration`
- Сущности:
  - `climate` (вкл/выкл, режим `heat`/`fan_only`, уставка температуры, пресеты скоростей `1..N`)
  - `number` в блоке настроек устройства:
    - `Min Heating Temperature` (B0, ввод числом, 5..60°C)
    - `Max Heating Temperature` (B1, ввод числом, 5..60°C)
  - `sensor` температуры притока
  - `sensor` наружной температуры
  - `sensor` кода аварии
  - отдельные `diagnostic` сенсоры:
    - `Power Raw`
    - `Mode Raw`
    - `Alarm Code 17-32`
    - `Alarm Code 33-48`
- Расширенные настройки через Options:
  - адреса register
  - делитель температуры
  - максимальная скорость вентилятора
  - интервал опроса
  - `read_only` (запрет любых записей в устройство)

## Установка

1. Скопируйте папку `custom_components/zentec031` в ваш Home Assistant:
   - `<config>/custom_components/zentec031`
2. Перезапустите Home Assistant.
3. Добавьте интеграцию `Zentec 031` в UI.

## Важно

Заводская карта Modbus-регистров у разных контроллеров может отличаться.
Если значения/управление работают некорректно, откройте Options интеграции и выставьте правильные адреса register по вашему мануалу.

Текущие значения по умолчанию:

- `slave_id`: `0`
- `power_register`: `40003` (главный пуск)
- `mode_register`: `40001` (главный режим работы)
- `mode_heat_value`: `2`
- `mode_vent_value`: `1`
- `fan_speed_register`: `40000` (уставка скорости)
- `target_temp_register`: `40002` (главная уставка температуры)
- `min_heat_temp_register`: `50008` (B0, минимальная температура подогрева)
- `max_heat_temp_register`: `50009` (B1, максимальная температура подогрева)
- `supply_temp_register`: `40009` (текущая температура для climate)
- `supply_temp_divisor`: `10`
- `outdoor_temp_register`: `50005` (температура вытяжного воздуха)
- `alarm_register`: `40004` (аварии 01-16)
- `temperature_divisor`: `1`
- `max_fan_speed`: `7`
- `read_only`: `false`

Примечание: для адресов `30000..39999` интеграция автоматически использует чтение Input Registers.
