# Zentec 031 Home Assistant Custom Integration

Кастомная интеграция `zentec031` для управления приточной установкой через Modbus TCP.

Извлеченная карта регистров: `docs/register_map_extracted.md`.

## Что реализовано

- UI-настройка через `Settings -> Devices & Services -> Add Integration`
- Сущности:
  - `switch` питания
  - `fan` скорости вентилятора
  - `number` уставки температуры
  - `sensor` температуры притока
  - `sensor` наружной температуры
  - `sensor` кода аварии
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

- `power_register`: `40003` (главный пуск)
- `fan_speed_register`: `40000` (уставка скорости)
- `target_temp_register`: `40002` (главная уставка температуры)
- `supply_temp_register`: `50004` (канальный датчик температуры)
- `outdoor_temp_register`: `50005` (температура вытяжного воздуха)
- `alarm_register`: `40004` (аварии 01-16)
- `temperature_divisor`: `1`
- `max_fan_speed`: `7`
- `read_only`: `false`
