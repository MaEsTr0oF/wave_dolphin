"""Автотесты для водного транспорта «Волновой Дельфин» (SPEC v0.1).

Запуск из корня проекта:
    python -m unittest discover -s tests -v

Модульные тесты используют AAA, сценарные — Given/When/Then через Pilot.
Каждый метод содержит ID соответствующего тест-кейса.
"""

import unittest

from wave_dolphin import (
    CrazyVehicleError,
    DolphinCannotWalk,
    DolphinError,
    DolphinInvalidState,
    DolphinNoStrength,
    WaveDolphin,
)

PLACES = 6


def make_dolphin(**overrides):
    """Создать эталонный аппарат из SPEC 3.2."""
    params = {
        "name": "Волновой Дельфин",
        "mass_kg": 120,
        "fin_span_m": 2,
        "max_speed_kmh": 60,
    }
    params.update(overrides)
    return WaveDolphin(**params)


def snapshot(dolphin):
    """Вернуть полный снимок изменяемого публичного состояния."""
    return (
        dolphin.energy,
        dolphin.position_km,
        dolphin.is_flying,
        dolphin.deep_dive,
    )


class Pilot:
    """Тестовая обёртка пилота, делегирующая команды транспорту."""

    def __init__(self, dolphin):
        self._dolphin = dolphin

    def swim(self, distance_km):
        return self._dolphin.move(distance_km, "water")

    def dive(self, distance_km):
        return self._dolphin.move(distance_km, "underwater")

    def fly(self, distance_km):
        return self._dolphin.move(distance_km, "air")

    def can_overcome(self, obstacle):
        return self._dolphin.can_overcome(obstacle)

    def refuel(self, amount):
        return self._dolphin.refuel(amount)


class TestConstructor(unittest.TestCase):
    """SPEC 3.2, 3.3."""

    def test_tc01_init_valid_defaults(self):
        """TC-01. Создание с энергией по умолчанию и начальное состояние."""
        dolphin = make_dolphin()

        self.assertEqual(dolphin.name, "Волновой Дельфин")
        self.assertAlmostEqual(dolphin.mass_kg, 120.0, places=PLACES)
        self.assertAlmostEqual(dolphin.fin_span_m, 2.0, places=PLACES)
        self.assertAlmostEqual(dolphin.max_speed_kmh, 60.0, places=PLACES)
        self.assertAlmostEqual(dolphin.energy, 100.0, places=PLACES)
        self.assertAlmostEqual(dolphin.position_km, 0.0, places=PLACES)
        self.assertIs(dolphin.is_flying, False)
        self.assertIs(dolphin.deep_dive, False)
        for attr in ("mass_kg", "fin_span_m", "max_speed_kmh", "energy",
                     "position_km"):
            with self.subTest(attr=attr):
                self.assertIsInstance(getattr(dolphin, attr), float)
        readonly_fields = (
            "name", "mass_kg", "fin_span_m", "max_speed_kmh", "energy",
            "position_km", "is_flying", "deep_dive",
        )
        for attr in readonly_fields:
            with self.subTest(readonly=attr):
                with self.assertRaises(AttributeError):
                    setattr(dolphin, attr, None)

    def test_tc02_init_energy_boundaries(self):
        """TC-02. Граничные значения энергии 0 и 100 допустимы."""
        for energy in (0, 100):
            with self.subTest(energy=energy):
                dolphin = make_dolphin(energy=energy)
                self.assertAlmostEqual(dolphin.energy, float(energy),
                                       places=PLACES)

    def test_tc03_init_empty_name_raises(self):
        """TC-03. Пустое имя и имя из пробелов → ValueError."""
        for name in ("", "   "):
            with self.subTest(name=name):
                with self.assertRaises(ValueError):
                    make_dolphin(name=name)

    def test_tc04_init_non_positive_dimensions_raise(self):
        """TC-04. Неположительная масса, размах или скорость → ValueError."""
        for param in ("mass_kg", "fin_span_m", "max_speed_kmh"):
            for value in (0, -1):
                with self.subTest(param=param, value=value):
                    with self.assertRaises(ValueError):
                        make_dolphin(**{param: value})

    def test_tc05_init_energy_range(self):
        """TC-05. Энергия вне диапазона 0…100 → ValueError."""
        for energy in (-0.1, 100.1):
            with self.subTest(energy=energy):
                with self.assertRaises(ValueError):
                    make_dolphin(energy=energy)

    def test_tc06_init_wrong_types_raise(self):
        """TC-06. Неверные типы и приоритет проверки типов → TypeError."""
        cases = [
            {"name": 123},
            {"name": None},
            {"mass_kg": "120"},
            {"mass_kg": True},
            {"fin_span_m": None},
            {"max_speed_kmh": "60"},
            {"energy": "50"},
            {"name": "", "mass_kg": "120"},
        ]
        for overrides in cases:
            with self.subTest(overrides=overrides):
                with self.assertRaises(TypeError):
                    make_dolphin(**overrides)

    def test_tc07_non_finite_numbers_raise(self):
        """TC-07. NaN и ±∞ отвергаются в конструкторе и числовых методах."""
        special = (float("nan"), float("inf"), float("-inf"))
        for param in ("mass_kg", "fin_span_m", "max_speed_kmh", "energy"):
            for value in special:
                with self.subTest(param=param, value=value):
                    with self.assertRaises(ValueError):
                        make_dolphin(**{param: value})

        dolphin = make_dolphin()
        before = snapshot(dolphin)
        for value in special:
            with self.subTest(method="move", value=value):
                with self.assertRaises(ValueError):
                    dolphin.move(value, "water")
            with self.subTest(method="calculate_energy", value=value):
                with self.assertRaises(ValueError):
                    dolphin.calculate_energy(value, "air")
            with self.subTest(method="refuel", value=value):
                with self.assertRaises(ValueError):
                    dolphin.refuel(value)
        self.assertEqual(snapshot(dolphin), before)


class TestMove(unittest.TestCase):
    """SPEC 3.4.1."""

    def test_tc08_move_on_water(self):
        """TC-08. Поверхностное движение: половина max_speed и 1 ед./км."""
        dolphin = make_dolphin()

        hours = dolphin.move(6, "water")

        self.assertAlmostEqual(hours, 0.2, places=PLACES)
        self.assertAlmostEqual(dolphin.energy, 94.0, places=PLACES)
        self.assertAlmostEqual(dolphin.position_km, 6.0, places=PLACES)
        self.assertIs(dolphin.is_flying, False)
        self.assertIs(dolphin.deep_dive, False)

    def test_tc09_move_underwater(self):
        """TC-09. Подводное движение: треть max_speed и 2 ед./км."""
        dolphin = make_dolphin()

        hours = dolphin.move(3, "underwater")

        self.assertAlmostEqual(hours, 0.15, places=PLACES)
        self.assertAlmostEqual(dolphin.energy, 94.0, places=PLACES)
        self.assertAlmostEqual(dolphin.position_km, 3.0, places=PLACES)
        self.assertIs(dolphin.is_flying, False)
        self.assertIs(dolphin.deep_dive, True)

    def test_tc10_move_in_air(self):
        """TC-10. Полёт над водой: max_speed и 2 ед./км."""
        dolphin = make_dolphin()

        hours = dolphin.move(2, "air")

        self.assertAlmostEqual(hours, 2 / 60, places=PLACES)
        self.assertAlmostEqual(dolphin.energy, 96.0, places=PLACES)
        self.assertAlmostEqual(dolphin.position_km, 2.0, places=PLACES)
        self.assertIs(dolphin.is_flying, True)
        self.assertIs(dolphin.deep_dive, False)

    def test_tc11_ground_movement_forbidden(self):
        """TC-11. Движение по суше → DolphinCannotWalk без изменения состояния."""
        dolphin = make_dolphin()
        before = snapshot(dolphin)

        with self.assertRaises(DolphinCannotWalk):
            dolphin.move(1, "ground")

        self.assertEqual(snapshot(dolphin), before)

    def test_tc12_move_invalid_arguments_raise(self):
        """TC-12. Неверные значения и типы move → ValueError/TypeError."""
        dolphin = make_dolphin()
        before = snapshot(dolphin)

        for args in ((0, "water"), (-1, "water"), (1, "unknown")):
            with self.subTest(args=args):
                with self.assertRaises(ValueError):
                    dolphin.move(*args)
        for args in (("1", "water"), (True, "water"), (0, 123)):
            with self.subTest(args=args):
                with self.assertRaises(TypeError):
                    dolphin.move(*args)
        self.assertEqual(snapshot(dolphin), before)

    def test_tc13_move_insufficient_energy_is_atomic(self):
        """TC-13. Нехватка энергии вызывает DolphinNoStrength без изменений."""
        cases = [
            (make_dolphin(energy=3), 4, "water", 4.0, 3.0),
            (make_dolphin(energy=3), 2, "underwater", 4.0, 3.0),
            (make_dolphin(energy=1), 1, "air", 2.0, 1.0),
        ]
        for dolphin, distance, terrain, required, available in cases:
            with self.subTest(terrain=terrain):
                before = snapshot(dolphin)
                with self.assertRaises(DolphinNoStrength) as ctx:
                    dolphin.move(distance, terrain)
                self.assertAlmostEqual(ctx.exception.required, required,
                                       places=PLACES)
                self.assertAlmostEqual(ctx.exception.available, available,
                                       places=PLACES)
                self.assertEqual(snapshot(dolphin), before)

        exact = make_dolphin(energy=2)
        hours = exact.move(2, "water")
        self.assertAlmostEqual(hours, 2 / 30, places=PLACES)
        self.assertAlmostEqual(exact.energy, 0.0, places=PLACES)
        self.assertAlmostEqual(exact.position_km, 2.0, places=PLACES)


class TestEnergyAndObstacles(unittest.TestCase):
    """SPEC 3.4.2, 3.4.3."""

    def test_tc14_calculate_energy_without_mutation(self):
        """TC-14. Расчёт энергии для трёх сред не меняет состояние."""
        dolphin = make_dolphin()
        before = snapshot(dolphin)

        self.assertAlmostEqual(dolphin.calculate_energy(6, "water"), 6.0,
                               places=PLACES)
        self.assertAlmostEqual(dolphin.calculate_energy(3, "underwater"), 6.0,
                               places=PLACES)
        self.assertAlmostEqual(dolphin.calculate_energy(2, "air"), 4.0,
                               places=PLACES)
        with self.assertRaises(ValueError):
            dolphin.calculate_energy(0, "water")
        with self.assertRaises(TypeError):
            dolphin.calculate_energy(0, 123)
        with self.assertRaises(DolphinCannotWalk):
            dolphin.calculate_energy(1, "ground")
        self.assertEqual(snapshot(dolphin), before)

    def test_tc15_can_overcome_matrix(self):
        """TC-15. Возможность преодоления волн, рифа и скалы зависит от режима."""
        surface = make_dolphin()
        airborne = make_dolphin()
        airborne.move(1, "air")
        underwater = make_dolphin()
        underwater.move(1, "underwater")
        narrow_fins = make_dolphin(fin_span_m=1.5)
        narrow_fins.move(1, "air")

        self.assertEqual(
            [surface.can_overcome(x) for x in ("wave", "reef", "cliff")],
            [True, False, False],
        )
        self.assertEqual(
            [airborne.can_overcome(x) for x in ("wave", "reef", "cliff")],
            [True, False, True],
        )
        self.assertEqual(
            [underwater.can_overcome(x) for x in ("wave", "reef", "cliff")],
            [False, True, False],
        )
        self.assertEqual(
            [narrow_fins.can_overcome(x) for x in ("wave", "reef", "cliff")],
            [True, False, False],
        )

    def test_tc16_can_overcome_invalid_obstacle(self):
        """TC-16. Неверный тип препятствия → TypeError, неизвестное → ValueError."""
        dolphin = make_dolphin()
        before = snapshot(dolphin)
        with self.assertRaises(TypeError):
            dolphin.can_overcome(123)
        with self.assertRaises(ValueError):
            dolphin.can_overcome("mountain")
        self.assertEqual(snapshot(dolphin), before)


class TestRefuelAndStatus(unittest.TestCase):
    """SPEC 3.4.4, 3.4.5."""

    def test_tc17_refuel_caps_at_capacity(self):
        """TC-17. Пополнение энергии и ограничение максимума 100."""
        partially_charged = make_dolphin(energy=20)
        full_after_charge = make_dolphin(energy=80)

        self.assertIsNone(partially_charged.refuel(30))
        self.assertAlmostEqual(partially_charged.energy, 50.0,
                               places=PLACES)
        full_after_charge.refuel(50)
        self.assertAlmostEqual(full_after_charge.energy, 100.0,
                               places=PLACES)

    def test_tc18_refuel_invalid_arguments_and_state(self):
        """TC-18. Ошибочная заправка и заправка не на поверхности."""
        dolphin = make_dolphin(energy=50)
        before = snapshot(dolphin)
        for amount in (0, -1):
            with self.subTest(amount=amount):
                with self.assertRaises(ValueError):
                    dolphin.refuel(amount)
        for amount in (True, "10"):
            with self.subTest(amount=amount):
                with self.assertRaises(TypeError):
                    dolphin.refuel(amount)
        self.assertEqual(snapshot(dolphin), before)

        for terrain in ("air", "underwater"):
            vehicle = make_dolphin(energy=50)
            vehicle.move(1, terrain)
            before = snapshot(vehicle)
            with self.subTest(terrain=terrain):
                with self.assertRaises(DolphinInvalidState):
                    vehicle.refuel(10)
                self.assertEqual(snapshot(vehicle), before)

    def test_tc19_get_status_returns_independent_snapshot(self):
        """TC-19. get_status возвращает словарь с точными ключами и копию."""
        dolphin = make_dolphin()
        dolphin.move(2, "water")

        first = dolphin.get_status()
        second = dolphin.get_status()
        expected_keys = {
            "name", "mass_kg", "fin_span_m", "max_speed_kmh", "energy",
            "position_km", "is_flying", "deep_dive",
        }
        self.assertEqual(set(first), expected_keys)
        self.assertEqual(first["name"], "Волновой Дельфин")
        self.assertAlmostEqual(first["energy"], 98.0, places=PLACES)
        self.assertAlmostEqual(first["position_km"], 2.0, places=PLACES)

        first["energy"] = 0
        first["position_km"] = 999
        self.assertAlmostEqual(dolphin.energy, 98.0, places=PLACES)
        self.assertAlmostEqual(dolphin.position_km, 2.0, places=PLACES)
        self.assertAlmostEqual(second["energy"], 98.0, places=PLACES)
        self.assertAlmostEqual(second["position_km"], 2.0, places=PLACES)

    def test_tc20_domain_exception_hierarchy(self):
        """TC-20. Иерархия доменных исключений и атрибуты ошибки энергии."""
        for exception in (DolphinCannotWalk, DolphinNoStrength,
                          DolphinInvalidState):
            with self.subTest(exception=exception.__name__):
                self.assertTrue(issubclass(exception, DolphinError))
                self.assertTrue(issubclass(exception, CrazyVehicleError))
        self.assertTrue(issubclass(DolphinError, CrazyVehicleError))
        self.assertTrue(issubclass(CrazyVehicleError, Exception))

        error = DolphinNoStrength(required=6, available=2)
        self.assertAlmostEqual(error.required, 6.0, places=PLACES)
        self.assertAlmostEqual(error.available, 2.0, places=PLACES)


class TestScenarios(unittest.TestCase):
    """SPEC 4.2; сценарные тесты выполняются через Pilot."""

    def test_tc21_race_over_waves(self):
        """TC-21. Гонка над волнами: полёт, затем движение по поверхности."""
        dolphin = make_dolphin(energy=80)
        pilot = Pilot(dolphin)

        hours = pilot.fly(10)
        self.assertAlmostEqual(hours, 10 / 60, places=PLACES)
        self.assertAlmostEqual(dolphin.energy, 60.0, places=PLACES)
        self.assertAlmostEqual(dolphin.position_km, 10.0, places=PLACES)
        self.assertIs(dolphin.is_flying, True)
        self.assertIs(pilot.can_overcome("cliff"), True)

        hours = pilot.swim(5)
        self.assertAlmostEqual(hours, 5 / 30, places=PLACES)
        self.assertAlmostEqual(dolphin.energy, 55.0, places=PLACES)
        self.assertAlmostEqual(dolphin.position_km, 15.0, places=PLACES)
        self.assertIs(dolphin.is_flying, False)
        self.assertIs(dolphin.deep_dive, False)

    def test_tc22_coral_reef_exploration(self):
        """TC-22. Исследование рифа с возвращением на поверхность."""
        dolphin = make_dolphin(energy=80)
        pilot = Pilot(dolphin)

        pilot.swim(2)
        self.assertAlmostEqual(dolphin.energy, 78.0, places=PLACES)
        self.assertAlmostEqual(dolphin.position_km, 2.0, places=PLACES)

        hours = pilot.dive(3)
        self.assertAlmostEqual(hours, 3 / 20, places=PLACES)
        self.assertAlmostEqual(dolphin.energy, 72.0, places=PLACES)
        self.assertAlmostEqual(dolphin.position_km, 5.0, places=PLACES)
        self.assertIs(dolphin.deep_dive, True)
        self.assertIs(pilot.can_overcome("reef"), True)

        pilot.swim(1)
        self.assertAlmostEqual(dolphin.energy, 71.0, places=PLACES)
        self.assertAlmostEqual(dolphin.position_km, 6.0, places=PLACES)
        self.assertIs(dolphin.deep_dive, False)
        self.assertIs(dolphin.is_flying, False)

    def test_tc23_escape_from_flooded_grotto(self):
        """TC-23. Нехватка энергии не меняет состояние; возврат и пополнение."""
        dolphin = make_dolphin(energy=8)
        pilot = Pilot(dolphin)

        pilot.dive(2)
        self.assertAlmostEqual(dolphin.energy, 4.0, places=PLACES)
        self.assertAlmostEqual(dolphin.position_km, 2.0, places=PLACES)
        self.assertIs(dolphin.deep_dive, True)
        before = snapshot(dolphin)

        with self.assertRaises(DolphinNoStrength):
            pilot.dive(3)
        self.assertEqual(snapshot(dolphin), before)

        pilot.swim(1)
        pilot.refuel(10)
        self.assertAlmostEqual(dolphin.energy, 13.0, places=PLACES)
        self.assertAlmostEqual(dolphin.position_km, 3.0, places=PLACES)
        self.assertIs(dolphin.is_flying, False)
        self.assertIs(dolphin.deep_dive, False)

    def test_tc24_coastal_cliff_with_short_fins(self):
        """TC-24. Короткие плавники не позволяют преодолеть скалу в полёте."""
        dolphin = make_dolphin(fin_span_m=1.5, energy=50)
        pilot = Pilot(dolphin)

        pilot.dive(2)
        self.assertIs(pilot.can_overcome("reef"), True)
        self.assertIs(pilot.can_overcome("cliff"), False)
        pilot.fly(1)
        self.assertIs(dolphin.is_flying, True)
        self.assertAlmostEqual(dolphin.energy, 44.0, places=PLACES)
        self.assertIs(pilot.can_overcome("cliff"), False)

        pilot.swim(2)
        self.assertAlmostEqual(dolphin.energy, 42.0, places=PLACES)
        self.assertAlmostEqual(dolphin.position_km, 5.0, places=PLACES)
        self.assertIs(dolphin.is_flying, False)
        self.assertIs(dolphin.deep_dive, False)

    def test_tc25_mixed_route_and_refuel(self):
        """TC-25. Смешанный маршрут, запрет заправки под водой и пополнение."""
        dolphin = make_dolphin(energy=50)
        pilot = Pilot(dolphin)

        pilot.swim(5)
        pilot.fly(5)
        pilot.dive(5)
        before = snapshot(dolphin)
        with self.assertRaises(DolphinInvalidState):
            pilot.refuel(50)
        self.assertEqual(snapshot(dolphin), before)

        pilot.swim(1)
        pilot.refuel(50)
        self.assertAlmostEqual(dolphin.position_km, 16.0, places=PLACES)
        self.assertAlmostEqual(dolphin.energy, 74.0, places=PLACES)
        self.assertIs(dolphin.is_flying, False)
        self.assertIs(dolphin.deep_dive, False)


if __name__ == "__main__":
    unittest.main()
