"""Реализация водного транспорта «Волновой Дельфин» (SPEC v0.2)."""

from __future__ import annotations

import math
from typing import Any


class CrazyVehicleError(Exception):
    """Базовое исключение учебных транспортных моделей."""


class DolphinError(CrazyVehicleError):
    """Базовое доменное исключение «Волнового Дельфина»."""


class DolphinCannotWalk(DolphinError):
    """Возникает при попытке движения по суше."""


class DolphinNoStrength(DolphinError):
    """Недостаточно энергии для выбранного перемещения."""

    def __init__(self, required: float, available: float) -> None:
        self.required = float(required)
        self.available = float(available)
        super().__init__(
            f"Недостаточно энергии: требуется {self.required:g}, "
            f"доступно {self.available:g}."
        )


class DolphinInvalidState(DolphinError):
    """Операция запрещена в текущем режиме транспорта."""


class WaveDolphin:
    """Гибридный транспорт для поверхности воды, погружения и полёта."""

    _NUMERIC_FIELDS = ("mass_kg", "fin_span_m", "max_speed_kmh", "energy")
    _TERRAINS = {"water", "underwater", "air", "ground"}
    _ENERGY_RATE = {"water": 1.0, "underwater": 2.0, "air": 2.0}

    def __init__(
        self,
        name: str,
        mass_kg: float,
        fin_span_m: float,
        max_speed_kmh: float,
        energy: float = 100.0,
    ) -> None:
        """Проверить параметры и создать аппарат в поверхностном режиме."""
        values = {
            "name": name,
            "mass_kg": mass_kg,
            "fin_span_m": fin_span_m,
            "max_speed_kmh": max_speed_kmh,
            "energy": energy,
        }
        # Сначала проверяются типы всех аргументов.
        if not isinstance(name, str):
            raise TypeError("name должен иметь тип str.")
        for field in self._NUMERIC_FIELDS:
            value = values[field]
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise TypeError(f"{field} должен быть числом int или float, кроме bool.")
        # Затем проверяются значения всех аргументов.
        if not name.strip():
            raise ValueError("name не может быть пустым или состоять из пробелов.")
        for field in ("mass_kg", "fin_span_m", "max_speed_kmh"):
            value = float(values[field])
            if not math.isfinite(value) or value <= 0:
                raise ValueError(f"{field} должен быть конечным числом больше нуля.")
        energy_value = float(energy)
        if not math.isfinite(energy_value) or not 0.0 <= energy_value <= 100.0:
            raise ValueError("energy должен находиться в диапазоне от 0 до 100.")

        object.__setattr__(self, "_name", name)
        object.__setattr__(self, "_mass_kg", float(mass_kg))
        object.__setattr__(self, "_fin_span_m", float(fin_span_m))
        object.__setattr__(self, "_max_speed_kmh", float(max_speed_kmh))
        object.__setattr__(self, "_energy", energy_value)
        object.__setattr__(self, "_position_km", 0.0)
        object.__setattr__(self, "_is_flying", False)
        object.__setattr__(self, "_deep_dive", False)

    def __setattr__(self, name: str, value: Any) -> None:
        """Запретить внешнее изменение публичных и внутренних атрибутов."""
        if name in {
            "name", "mass_kg", "fin_span_m", "max_speed_kmh", "energy",
            "position_km", "is_flying", "deep_dive",
        } or name.startswith("_"):
            raise AttributeError("Атрибуты WaveDolphin доступны только для чтения.")
        object.__setattr__(self, name, value)

    @property
    def name(self) -> str:
        return self._name

    @property
    def mass_kg(self) -> float:
        return self._mass_kg

    @property
    def fin_span_m(self) -> float:
        return self._fin_span_m

    @property
    def max_speed_kmh(self) -> float:
        return self._max_speed_kmh

    @property
    def energy(self) -> float:
        return self._energy

    @property
    def position_km(self) -> float:
        return self._position_km

    @property
    def is_flying(self) -> bool:
        return self._is_flying

    @property
    def deep_dive(self) -> bool:
        return self._deep_dive

    @staticmethod
    def _validate_numeric_and_terrain(distance_km: float, terrain: str) -> None:
        """Проверить типы всех аргументов, затем значения и режим."""
        if isinstance(distance_km, bool) or not isinstance(distance_km, (int, float)):
            raise TypeError("distance_km должен быть числом int или float, кроме bool.")
        if not isinstance(terrain, str):
            raise TypeError("terrain должен иметь тип str.")
        distance = float(distance_km)
        if not math.isfinite(distance) or distance <= 0:
            raise ValueError("distance_km должен быть конечным числом больше нуля.")
        if terrain not in WaveDolphin._TERRAINS:
            raise ValueError("Неизвестный режим перемещения.")

    def _get_energy_cost(self, distance_km: float, terrain: str) -> float:
        """Вернуть стоимость перемещения после валидации параметров."""
        if terrain == "ground":
            raise DolphinCannotWalk("Транспорт не предназначен для движения по суше.")
        return float(distance_km) * self._ENERGY_RATE[terrain]

    def move(self, distance_km: float, terrain: str) -> float:
        """Переместить транспорт и атомарно обновить энергию и режим."""
        self._validate_numeric_and_terrain(distance_km, terrain)
        if terrain == "ground":
            raise DolphinCannotWalk("Транспорт не предназначен для движения по суше.")

        distance = float(distance_km)
        rates = {"water": self.max_speed_kmh * 0.5,
                 "underwater": self.max_speed_kmh / 3.0,
                 "air": self.max_speed_kmh}
        required = self._get_energy_cost(distance, terrain)
        if required > self.energy:
            raise DolphinNoStrength(required, self.energy)

        hours = distance / rates[terrain]
        object.__setattr__(self, "_position_km", self.position_km + distance)
        object.__setattr__(self, "_energy", self.energy - required)
        object.__setattr__(self, "_is_flying", terrain == "air")
        object.__setattr__(self, "_deep_dive", terrain == "underwater")
        return float(hours)

    def can_overcome(self, obstacle: str) -> bool:
        """Проверить препятствие без изменения состояния и расхода энергии."""
        if not isinstance(obstacle, str):
            raise TypeError("obstacle должен иметь тип str.")
        if obstacle not in {"wave", "reef", "cliff"}:
            raise ValueError("Неизвестный тип препятствия.")
        if obstacle == "wave":
            return not self.deep_dive
        if obstacle == "reef":
            return self.deep_dive
        return self.is_flying and self.fin_span_m >= 2.0

    def calculate_energy(self, distance_km: float, terrain: str) -> float:
        """Рассчитать расход без проверки запаса и изменения состояния."""
        self._validate_numeric_and_terrain(distance_km, terrain)
        return self._get_energy_cost(float(distance_km), terrain)

    def refuel(self, amount: float) -> None:
        """Пополнить энергию на поверхности, ограничив запас значением 100."""
        if isinstance(amount, bool) or not isinstance(amount, (int, float)):
            raise TypeError("amount должен быть числом int или float, кроме bool.")
        amount_value = float(amount)
        if not math.isfinite(amount_value) or amount_value <= 0:
            raise ValueError("amount должен быть конечным числом больше нуля.")
        if self.is_flying or self.deep_dive:
            raise DolphinInvalidState(
                "Заправка разрешена только на поверхности воды."
            )
        object.__setattr__(self, "_energy", min(100.0, self.energy + amount_value))
        return None

    def get_status(self) -> dict[str, Any]:
        """Вернуть независимый словарь со снимком всех публичных атрибутов."""
        return {
            "name": self.name,
            "mass_kg": self.mass_kg,
            "fin_span_m": self.fin_span_m,
            "max_speed_kmh": self.max_speed_kmh,
            "energy": self.energy,
            "position_km": self.position_km,
            "is_flying": self.is_flying,
            "deep_dive": self.deep_dive,
        }
