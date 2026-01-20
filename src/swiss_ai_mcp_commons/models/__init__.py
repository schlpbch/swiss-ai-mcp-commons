"""Shared data models for Swiss AI MCPs."""

from .location import Location, Coordinates, Region
from .weather import Weather, Temperature, SnowConditions, AirQuality
from .pricing import Price, FareOption, PricingInfo
from .time import TimeRange, DateRange

__all__ = [
    # Location models
    "Location",
    "Coordinates",
    "Region",
    # Weather models
    "Weather",
    "Temperature",
    "SnowConditions",
    "AirQuality",
    # Pricing models
    "Price",
    "FareOption",
    "PricingInfo",
    # Time models
    "TimeRange",
    "DateRange",
]
