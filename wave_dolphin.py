"""Волновой Дельфин по SPEC.md версии 0.1."""

import math


class CrazyVehicleError(Exception):
    pass


class DolphinError(CrazyVehicleError):
    pass


class DolphinCannotWalk(DolphinError):
    pass


class DolphinNoStrength(DolphinError):
    def __init__(self, required, available):
        self.required = float(required)
        self.available = float(available)
        super().__init__(
            f"Недостаточно энергии: нужно {self.required}, есть {self.available}"
        )


class DolphinInvalidState(DolphinError):
    pass


def _check_number_type(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError("Ожидается int или float, кроме bool")


def _number(value, allow_zero=False):
    try:
        value = float(value)
    except OverflowError:
        raise ValueError("Число слишком большое для float") from None
    if not math.isfinite(value):
        raise ValueError("Число должно быть конечным")
    if value < 0 or (value == 0 and not allow_zero):
        raise ValueError("Число вне допустимого диапазона")
    return value


class WaveDolphin:
    def __init__(self, name, mass_kg, fin_span_m, max_speed_kmh, energy=100.0):
        # Сначала типы всех аргументов, затем их значения.
        if not isinstance(name, str):
            raise TypeError("Название должно быть строкой")
        for value in (mass_kg, fin_span_m, max_speed_kmh, energy):
            _check_number_type(value)

        if not name.strip():
            raise ValueError("Название не должно быть пустым")
        mass_kg = _number(mass_kg)
        fin_span_m = _number(fin_span_m)
        max_speed_kmh = _number(max_speed_kmh)
        energy = _number(energy, allow_zero=True)
        if energy > 100:
            raise ValueError("Энергия должна быть от 0 до 100")

        self._name = name
        self._mass_kg = mass_kg
        self._fin_span_m = fin_span_m
        self._max_speed_kmh = max_speed_kmh
        self._energy = energy
        self._position_km = 0.0
        self._is_flying = False
        self._deep_dive = False

    @property
    def name(self):
        return self._name

    @property
    def mass_kg(self):
        return self._mass_kg

    @property
    def fin_span_m(self):
        return self._fin_span_m

    @property
    def max_speed_kmh(self):
        return self._max_speed_kmh

    @property
    def energy(self):
        return self._energy

    @property
    def position_km(self):
        return self._position_km

    @property
    def is_flying(self):
        return self._is_flying

    @property
    def deep_dive(self):
        return self._deep_dive

    def calculate_energy(self, distance_km, terrain):
        _check_number_type(distance_km)
        if not isinstance(terrain, str):
            raise TypeError("Режим должен быть строкой")

        distance = _number(distance_km)
        if terrain not in ("water", "underwater", "air", "ground"):
            raise ValueError("Неизвестный режим")
        if terrain == "ground":
            raise DolphinCannotWalk("Дельфин не передвигается по суше")
        if terrain == "water":
            return distance * 1.0
        return distance * 2.0

    def move(self, distance_km, terrain):
        required = self.calculate_energy(distance_km, terrain)
        if required > self._energy:
            raise DolphinNoStrength(required, self._energy)

        if terrain == "water":
            speed = self._max_speed_kmh * 0.5
        elif terrain == "underwater":
            speed = self._max_speed_kmh / 3
        else:
            speed = self._max_speed_kmh

        hours = float(distance_km) / speed
        self._position_km += float(distance_km)
        self._energy -= required
        self._is_flying = terrain == "air"
        self._deep_dive = terrain == "underwater"
        return hours

    def can_overcome(self, obstacle):
        if not isinstance(obstacle, str):
            raise TypeError("Препятствие должно быть строкой")
        if obstacle == "wave":
            return not self._deep_dive
        if obstacle == "reef":
            return self._deep_dive
        if obstacle == "cliff":
            return self._is_flying and self._fin_span_m >= 2.0
        raise ValueError("Неизвестное препятствие")

    def refuel(self, amount):
        _check_number_type(amount)
        amount = _number(amount)
        if self._is_flying or self._deep_dive:
            raise DolphinInvalidState("Заправка разрешена только на поверхности")
        self._energy = min(100.0, self._energy + amount)

    def get_status(self):
        return {
            "name": self._name,
            "mass_kg": self._mass_kg,
            "fin_span_m": self._fin_span_m,
            "max_speed_kmh": self._max_speed_kmh,
            "energy": self._energy,
            "position_km": self._position_km,
            "is_flying": self._is_flying,
            "deep_dive": self._deep_dive,
        }
