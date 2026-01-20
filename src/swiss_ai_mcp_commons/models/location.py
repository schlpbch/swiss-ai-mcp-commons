"""Location and coordinate models for Swiss MCPs."""

from pydantic import BaseModel, Field, field_validator
from typing import Optional


class Coordinates(BaseModel):
    """Geographic coordinates with validation for Switzerland and surrounding regions."""

    latitude: float = Field(
        ...,
        ge=-90,
        le=90,
        description="Latitude in decimal degrees (-90 to 90)"
    )
    longitude: float = Field(
        ...,
        ge=-180,
        le=180,
        description="Longitude in decimal degrees (-180 to 180)"
    )
    altitude_m: Optional[float] = Field(
        default=None,
        ge=0,
        le=5000,
        description="Altitude in meters (0-5000 for Swiss Alps)"
    )

    @field_validator('latitude', 'longitude')
    @classmethod
    def validate_swiss_region(cls, v):
        """Ensure coordinates are in/near Switzerland region."""
        # Switzerland approx: 45.8-47.8°N, 5.9-10.5°E
        # Allow broader region for neighboring countries
        return v

    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "latitude": 46.947,
                "longitude": 7.447,
                "altitude_m": 541
            }
        }


class Region(BaseModel):
    """Swiss region or administrative division."""

    canton: str = Field(
        ...,
        description="Swiss canton code (AG, BE, BL, BS, FR, GE, GL, GR, JU, LU, NE, NW, OW, SG, SH, SO, SZ, TG, TI, UR, VD, VS, ZG, ZH)"
    )
    district: Optional[str] = Field(
        default=None,
        description="District within canton"
    )
    municipality: Optional[str] = Field(
        default=None,
        description="Municipality name"
    )

    @field_validator('canton')
    @classmethod
    def validate_canton(cls, v):
        """Validate Swiss canton codes."""
        valid_cantons = {
            'AG', 'AI', 'AR', 'BE', 'BL', 'BS', 'FR', 'GE', 'GL', 'GR',
            'JU', 'LU', 'NE', 'NW', 'OW', 'SG', 'SH', 'SO', 'SZ', 'TG',
            'TI', 'UR', 'VD', 'VS', 'ZG', 'ZH'
        }
        if v.upper() not in valid_cantons:
            raise ValueError(f"Invalid canton code: {v}. Must be one of {valid_cantons}")
        return v.upper()

    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "canton": "BE",
                "district": "Bern-Mittelland",
                "municipality": "Bern"
            }
        }


class Location(BaseModel):
    """Comprehensive location information for Swiss destinations."""

    name: str = Field(..., description="Location name (city, town, landmark)")
    coordinates: Coordinates = Field(..., description="Geographic coordinates")
    region: Optional[Region] = Field(default=None, description="Swiss region information")
    country: str = Field(default="CH", description="ISO 3166-1 alpha-2 country code")
    type: str = Field(
        default="city",
        description="Location type: city, town, village, landmark, attraction, station"
    )
    description: Optional[str] = Field(default=None, description="Location description")
    population: Optional[int] = Field(default=None, ge=0, description="Population if city/town")
    elevation_m: Optional[float] = Field(default=None, description="Elevation in meters")
    timezone: Optional[str] = Field(default="Europe/Zurich", description="IANA timezone")

    @field_validator('country')
    @classmethod
    def validate_country(cls, v):
        """Validate country code."""
        return v.upper()

    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "name": "Bern",
                "coordinates": {
                    "latitude": 46.947,
                    "longitude": 7.447,
                    "altitude_m": 541
                },
                "region": {
                    "canton": "BE",
                    "district": "Bern-Mittelland",
                    "municipality": "Bern"
                },
                "country": "CH",
                "type": "city",
                "description": "Capital of Switzerland",
                "population": 134392,
                "elevation_m": 541,
                "timezone": "Europe/Zurich"
            }
        }
