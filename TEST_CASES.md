# Test Case Specification — «Волновой Дельфин»

Версия: 0.1 (к `SPEC.md` v0.1)

Эталонный аппарат, если не сказано иное: `WaveDolphin("Волновой Дельфин", mass_kg=120, fin_span_m=2, max_speed_kmh=60, energy=100)`.  
Соотношение: 20 модульных / 5 сценарных = 80% / 20%.

Общие правила:
- дробные числа сравниваются через `TestCase.assertAlmostEqual(..., places=6)`;
- после каждого успешного действия проверяются изменённые поля и режимные флаги;
- после исключения сравнивается полный снимок состояния;
- все доменные исключения наследуются от `CrazyVehicleError`;
- каждый тест-метод содержит ID кейса в имени и docstring.

## 1. Модульные тесты (module, AAA)

| ID | Тип | Источник | Предусловие | Вход | Ожидание | Приоритет |
|---|---|---|---|---|---|---|
| TC-01 | module | SPEC 3.2, 3.3 | — | `WaveDolphin("Волновой Дельфин", 120, 2, 60)` | объект создан; `energy=100.0`, `position_km=0.0`, `is_flying=False`, `deep_dive=False`; числовые атрибуты имеют тип `float`; все публичные атрибуты доступны только для чтения | high |
| TC-02 | module | SPEC 3.2 | — | создать объекты с `energy=0` и `energy=100`; все остальные числовые параметры положительные | оба объекта созданы; граничные значения энергии допустимы | high |
| TC-03 | module | SPEC 3.2 | — | `name=""`; `name="   "` | `ValueError`; объект не создаётся | high |
| TC-04 | module | SPEC 3.2 | — | `mass_kg`, `fin_span_m` или `max_speed_kmh` равны `0` либо отрицательны | `ValueError` | high |
| TC-05 | module | SPEC 3.2 | — | `energy=-0.1`; `energy=100.1` | `ValueError` | high |
| TC-06 | module | SPEC 3.0, 3.2 | — | неверные типы каждого аргумента конструктора; `bool` вместо чисел; `name=""` вместе с неверным типом следующего аргумента | `TypeError`; проверка типов всех аргументов предшествует проверке значений | high |
| TC-07 | module | SPEC 3.0, 3.2, 3.4.1, 3.4.3, 3.4.4 | эталон | `NaN`, `+inf`, `-inf` в числовых параметрах конструктора, `move`, `calculate_energy`, `refuel` | `ValueError`; состояние после ошибок методов не меняется | high |
| TC-08 | module | SPEC 3.4.1 | эталон | `move(6, "water")` | время `0.2` ч; `energy=94`; `position_km=6`; `is_flying=False`; `deep_dive=False` | high |
| TC-09 | module | SPEC 3.4.1 | эталон | `move(3, "underwater")` | время `0.15` ч; `energy=94`; `position_km=3`; `deep_dive=True`; `is_flying=False` | high |
| TC-10 | module | SPEC 3.4.1 | эталон | `move(2, "air")` | время `2/60` ч; `energy=96`; `position_km=2`; `is_flying=True`; `deep_dive=False` | high |
| TC-11 | module | SPEC 3.4.1, 6.1, 6.2 | эталон | `move(1, "ground")` | `DolphinCannotWalk`; полный снимок состояния не изменился | high |
| TC-12 | module | SPEC 3.0, 3.4.1 | эталон | `move(0, "water")`; `move(-1, "water")`; `move(1, "unknown")`; `move("1", "water")`; `move(0, 123)` | `ValueError` для неверного значения; `TypeError` для неверного типа; при `move(0, 123)` приоритет у `TypeError`; состояние неизменно | high |
| TC-13 | module | SPEC 3.4.1, 6.1, 6.2 | отдельно: `energy=3` на поверхности; `energy=3` для проверки подводного движения; `energy=1` для полёта | `move(4, "water")`; `move(2, "underwater")`; `move(1, "air")` | `DolphinNoStrength`; `required` равен соответственно `4`, `4`, `2`; `available=3`, `3`, `1`; состояние каждого объекта неизменно; отдельная проверка: при `energy=2` вызов `move(2, "water")` успешен и оставляет `energy=0` | high |
| TC-14 | module | SPEC 3.4.3 | эталон | `calculate_energy(6, "water")`; `(3, "underwater")`; `(2, "air")` | возвращаются `6.0`, `6.0`, `4.0`; `distance=0` → `ValueError`, неверный тип аргумента → `TypeError`, `ground` → `DolphinCannotWalk`; состояние объекта не меняется; расчёт не зависит от текущего запаса энергии | high |
| TC-15 | module | SPEC 3.4.2 | объекты в режимах water, air, underwater; отдельный объект с `fin_span_m=1.5` | `can_overcome("wave" / "reef" / "cliff")` | поверхность: `True / False / False`; air при размахе 2.0: `True / False / True`; underwater: `False / True / False`; air при размахе 1.5: `True / False / False`; состояние не меняется | high |
| TC-16 | module | SPEC 3.4.2 | эталон | `can_overcome(123)`; `can_overcome("mountain")` | `TypeError`; `ValueError`; состояние неизменно | medium |
| TC-17 | module | SPEC 3.4.4 | поверхность, отдельно `energy=20` и `energy=80` | `refuel(30)`; `refuel(50)` | энергия становится `50` и `100` соответственно; метод возвращает `None` | high |
| TC-18 | module | SPEC 3.0, 3.4.4, 6.1, 6.2 | эталон и отдельные объекты в air/underwater | `refuel(0)`; `refuel(-1)`; `refuel(True)`; `refuel("10")`; `refuel(10)` в air и underwater | `ValueError`; `TypeError`; `DolphinInvalidState`; при ошибках энергия и флаги не меняются | high |
| TC-19 | module | SPEC 3.4.5 | эталон после `move(2, "water")` | дважды вызвать `get_status()`, изменить первый словарь | ключи ровно `name`, `mass_kg`, `fin_span_m`, `max_speed_kmh`, `energy`, `position_km`, `is_flying`, `deep_dive`; изменение словаря не меняет объект и второй снимок | medium |
| TC-20 | module | SPEC 6.1, 6.2 | — | `issubclass(...)`; создать `DolphinNoStrength(required=6, available=2)` | `DolphinError` наследуется от `CrazyVehicleError`; три доменных исключения наследуются от `DolphinError`; у `DolphinNoStrength` доступны `required=6.0`, `available=2.0` | medium |

## 2. Сценарные тесты (scenario, GWT)

Все сценарии выполняются через тестовую обёртку `Pilot`, которая делегирует команды публичным методам `WaveDolphin`.

| ID | Тип | Источник | Вход | Ожидание | Приоритет |
|---|---|---|---|---|---|
| TC-21 | scenario | SPEC 4.2, сценарий 5 | полёт 10 км, затем движение по воде 5 км; начальная энергия 80 | после первого шага: `position=10`, `energy=60`, `is_flying=True`; после второго: `position=15`, `energy=55`, `is_flying=False`, `deep_dive=False` | high |
| TC-22 | scenario | SPEC 4.2, сценарий 6 | вода 2 км → под водой 3 км → вода 1 км; начальная энергия 80 | итог: `position=6`, `energy=71`, `is_flying=False`, `deep_dive=False`; риф преодолим во время подводного участка | high |
| TC-23 | scenario | SPEC 4.2, сценарий 7 | при энергии 8: под водой 2 км; неудачная попытка пройти ещё 3 км; вода 1 км; пополнение на 10 | вторая попытка вызывает `DolphinNoStrength` и не меняет состояние; итог: `position=3`, `energy=13`, оба флага выключены | high |
| TC-24 | scenario | SPEC 4.2, сценарий 8 | размах плавников 1.5 м: под водой 2 км → воздух 1 км → вода 2 км | под водой риф преодолим; скала не преодолима из-за малого размаха; итог: `position=5`, `energy=42`, оба флага выключены | medium |
| TC-25 | scenario | SPEC 4.2, сценарий 9 | начальная энергия 50: вода 5 км → воздух 5 км → под водой 5 км; неудачная заправка; вода 1 км; заправка на 50 | заправка под водой вызывает `DolphinInvalidState` без изменения состояния; итог: `position=16`, `energy=74`, оба флага выключены | medium |

## 3. Покрытие

| Область | Тесты |
|---|---|
| конструктор и типы | TC-01–TC-07 |
| движение в трёх средах и запрет суши | TC-08–TC-13, TC-21–TC-25 |
| расчёт энергии | TC-14 |
| препятствия | TC-15–TC-16, TC-21, TC-22, TC-24 |
| пополнение энергии | TC-17–TC-18, TC-23, TC-25 |
| статус и исключения | TC-19–TC-20 |
