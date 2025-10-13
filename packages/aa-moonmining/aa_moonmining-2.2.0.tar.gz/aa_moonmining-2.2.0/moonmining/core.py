"""Core logic."""

import datetime as dt
from dataclasses import dataclass
from enum import IntEnum, auto
from typing import List, Optional

from . import helpers


# pylint: disable = too-many-instance-attributes
@dataclass
class CalculatedExtraction:
    """An extraction calculated from moon mining notifications."""

    class Status(IntEnum):
        """Extraction status."""

        STARTED = auto()
        CANCELED = auto()
        READY = auto()
        COMPLETED = auto()
        UNDEFINED = auto()

    refinery_id: int
    status: Status
    auto_fracture_at: Optional[dt.datetime] = None
    canceled_at: Optional[dt.datetime] = None
    canceled_by: Optional[int] = None
    chunk_arrival_at: Optional[dt.datetime] = None
    fractured_at: Optional[dt.datetime] = None
    fractured_by: Optional[int] = None
    products: Optional[List["CalculatedExtractionProduct"]] = None
    started_at: Optional[dt.datetime] = None
    started_by: Optional[int] = None

    def __post_init__(self):
        self.refinery_id = int(self.refinery_id)
        self.status = self.Status(self.status)
        if self.started_at:
            self.started_at = helpers.round_seconds(self.started_at)
        if self.chunk_arrival_at:
            self.chunk_arrival_at = helpers.round_seconds(self.chunk_arrival_at)
        if self.auto_fracture_at:
            self.auto_fracture_at = helpers.round_seconds(self.auto_fracture_at)

    @property
    def duration(self) -> dt.timedelta:
        """Return duration of this extraction."""
        if self.chunk_arrival_at and self.started_at:
            return self.chunk_arrival_at - self.started_at
        raise ValueError("chunk_arrival_at and/or started_at not defined")

    def total_volume(self) -> float:
        """Return total volume in this extraction."""
        if not self.products:
            return 0

        total = sum(product.volume for product in self.products)
        return total

    def moon_products_estimated(
        self, volume_per_day: float
    ) -> List["CalculatedMoonProduct"]:
        """Return products with estimated amounts."""
        duration_in_days = self.duration.total_seconds() / (60 * 60 * 24)
        if duration_in_days <= 0:
            raise ValueError("Can not estimate products without duration.")

        max_volume = duration_in_days * volume_per_day
        correction_factor = max(1, self.total_volume() / max_volume)
        if not self.products:
            return []

        products = [
            CalculatedMoonProduct(
                ore_type_id=product.ore_type_id,
                amount=product.calculated_share(duration_in_days, volume_per_day)
                / correction_factor,
            )
            for product in self.products
        ]
        return products


@dataclass
class CalculatedExtractionProduct:
    """Product of an extraction calculated from moon mining notifications."""

    ore_type_id: int
    volume: float

    def __post_init__(self):
        self.ore_type_id = int(self.ore_type_id)

    def calculated_share(self, duration_in_days: float, volume_per_day: float) -> float:
        """Return calculated share of this moon product."""
        return self.volume / (duration_in_days * volume_per_day)

    @classmethod
    def create_list_from_dict(cls, ores: dict) -> List["CalculatedExtractionProduct"]:
        """Return list of newly created objs from a dict."""
        return [cls(ore_type_id, volume) for ore_type_id, volume in ores.items()]


@dataclass
class CalculatedMoonProduct:
    """Product of an extraction calculated from moon mining notifications."""

    ore_type_id: int
    amount: float

    def __post_init__(self):
        self.ore_type_id = int(self.ore_type_id)
