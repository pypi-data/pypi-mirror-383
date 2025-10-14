"""
Sarmat.
Ядро пакета.
Описание бизнес логики.
Модели.
Подвижной состав.
"""
from dataclasses import dataclass
from datetime import date
from typing import List

from sarmat.core.constants import CrewType, PermitType, VehicleType

from .sarmat_models import PersonModel, BaseIdModel, BaseUidModel, BaseModel, CustomAttributesModel


@dataclass
class SeatsRow(BaseIdModel):
    """Ряд сидений в транспортном средстве."""

    a: int = 0
    b: int = 0
    c: int = 0
    d: int = 0
    e: int = 0


@dataclass
class BaseVehicleModel(BaseModel):
    """Подвижной состав (основные атрибуты)."""

    vehicle_type: VehicleType   # тип транспортного средства
    vehicle_name: str           # марка транспортного средства
    state_number: str           # регистрационный номер
    seats: int                  # количество мест для посадки
    stand: int = 0              # количество мест стоя
    capacity: int = 0           # вместимость багажного отделения


@dataclass
class VehicleModel(BaseIdModel, CustomAttributesModel, BaseVehicleModel):
    """Подвижной состав."""

    vehicle_model: str | None = None        # модель транспортного средства
    seats_map: list[SeatsRow] | None = None     # схема расположения мест


@dataclass
class BaseCrewModel(BaseModel):
    """Экипаж (основные атрибуты)."""

    crew_type: CrewType     # тип члена экипажа
    is_main: bool = True    # признак главного члена экипажа


@dataclass
class CrewModel(BaseIdModel, CustomAttributesModel, BaseCrewModel, PersonModel):
    """Экипаж."""


@dataclass
class BasePermitModel(BaseModel):
    """Путевой лист (основные атрибуты)"""

    number: str                     # номер путевого листа
    permit_type: PermitType         # тип путевого листа
    depart_date: date               # дата выезда
    crew: List[CrewModel]           # экипаж
    vehicle: List[VehicleModel]     # подвижной состав


@dataclass
class PermitModel(BaseUidModel, CustomAttributesModel, BasePermitModel):
    """Путевой лист"""
