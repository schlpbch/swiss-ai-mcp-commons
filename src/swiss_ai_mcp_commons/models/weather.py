"""Weather-related data models for Swiss MCPs."""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class Temperature(BaseModel):
    """Temperature readings with Celsius unit."""

    value: float = Field(..., description="Temperature value in Celsius")
    min: Optional[float] = Field(default=None, description="Minimum temperature in Celsius")
    max: Optional[float] = Field(default=None, description="Maximum temperature in Celsius")
    apparent: Optional[float] = Field(default=None, description="Apparent/feels-like temperature")
    dew_point: Optional[float] = Field(default=None, description="Dew point in Celsius")

    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "value": 15.2,
                "min": 8.5,
                "max": 19.3,
                "apparent": 14.1,
                "dew_point": 10.2
            }
        }


class SnowConditions(BaseModel):
    """Snow depth and conditions for mountain regions."""

    depth_cm: float = Field(..., ge=0, description="Snow depth in centimeters")
    fresh_cm: Optional[float] = Field(default=None, ge=0, description="Fresh snow in centimeters")
    density_percent: Optional[float] = Field(
        default=None, ge=0, le=100,
        description="Snow density as percentage (0-100)"
    )
    avalanche_risk: Optional[int] = Field(
        default=None, ge=1, le=5,
        description="EAWS avalanche risk level (1-5)"
    )
    surface_hardness: Optional[str] = Field(
        default=None,
        description="Surface hardness: piste, crust, powder, wind-slab, spring, wet"
    )
    quality: Optional[str] = Field(
        default=None,
        description="Snow quality: excellent, good, fair, poor, variable"
    )

    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "depth_cm": 180,
                "fresh_cm": 25,
                "density_percent": 85,
                "avalanche_risk": 2,
                "surface_hardness": "piste",
                "quality": "excellent"
            }
        }


class AirQuality(BaseModel):
    """Air quality index and pollutant levels."""

    aqi: float = Field(..., ge=0, description="Air Quality Index (0-500+)")
    level: str = Field(
        ...,
        description="AQI level: Good, Fair, Moderate, Poor, Very Poor"
    )
    pm25: Optional[float] = Field(default=None, ge=0, description="PM2.5 (µg/m³)")
    pm10: Optional[float] = Field(default=None, ge=0, description="PM10 (µg/m³)")
    no2: Optional[float] = Field(default=None, ge=0, description="NO₂ (ppb)")
    o3: Optional[float] = Field(default=None, ge=0, description="O₃ (ppb)")
    so2: Optional[float] = Field(default=None, ge=0, description="SO₂ (ppb)")
    co: Optional[float] = Field(default=None, ge=0, description="CO (ppm)")
    pollen_birch: Optional[int] = Field(default=None, ge=0, description="Birch pollen (0-5)")
    pollen_graminea: Optional[int] = Field(default=None, ge=0, description="Graminea pollen (0-5)")
    pollen_mugwort: Optional[int] = Field(default=None, ge=0, description="Mugwort pollen (0-5)")

    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "aqi": 42.0,
                "level": "Good",
                "pm25": 8.5,
                "pm10": 15.2,
                "no2": 25.3,
                "o3": 45.1,
                "so2": 3.2,
                "co": 0.8,
                "pollen_birch": 2,
                "pollen_graminea": 1,
                "pollen_mugwort": 0
            }
        }


class Weather(BaseModel):
    """Comprehensive weather information."""

    timestamp: datetime = Field(..., description="Observation/forecast timestamp")
    description: str = Field(..., description="Weather description (e.g., 'Sunny', 'Rainy')")
    code: Optional[int] = Field(default=None, description="WMO weather code")
    temperature: Temperature = Field(..., description="Temperature data")
    humidity_percent: Optional[float] = Field(
        default=None, ge=0, le=100,
        description="Relative humidity (0-100%)"
    )
    wind_speed_kmh: Optional[float] = Field(
        default=None, ge=0,
        description="Wind speed in km/h"
    )
    wind_direction_deg: Optional[float] = Field(
        default=None, ge=0, le=360,
        description="Wind direction in degrees (0-360)"
    )
    wind_gust_kmh: Optional[float] = Field(default=None, ge=0, description="Wind gust in km/h")
    pressure_hpa: Optional[float] = Field(default=None, description="Atmospheric pressure (hPa)")
    precipitation_mm: Optional[float] = Field(default=None, ge=0, description="Precipitation (mm)")
    visibility_m: Optional[float] = Field(default=None, ge=0, description="Visibility (meters)")
    cloud_cover_percent: Optional[float] = Field(
        default=None, ge=0, le=100,
        description="Cloud cover (0-100%)"
    )
    solar_radiation: Optional[float] = Field(default=None, ge=0, description="Solar radiation (W/m²)")
    uv_index: Optional[float] = Field(default=None, ge=0, description="UV index")
    snow_conditions: Optional[SnowConditions] = Field(default=None, description="Snow data if alpine")
    air_quality: Optional[AirQuality] = Field(default=None, description="Air quality data")

    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "timestamp": "2024-01-20T14:00:00Z",
                "description": "Sunny",
                "code": 1,
                "temperature": {
                    "value": 12.5,
                    "min": 8.2,
                    "max": 15.3,
                    "apparent": 11.8
                },
                "humidity_percent": 65,
                "wind_speed_kmh": 12,
                "wind_direction_deg": 220,
                "pressure_hpa": 1013.25,
                "precipitation_mm": 0,
                "cloud_cover_percent": 20
            }
        }
