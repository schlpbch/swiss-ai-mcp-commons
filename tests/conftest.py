"""Shared test fixtures and configuration."""

import pytest
from datetime import date, datetime, time
from swiss_ai_mcp_commons import (
    Location,
    Coordinates,
    Region,
    Weather,
    Temperature,
    Price,
    PricingInfo,
    DateRange,
)


@pytest.fixture
def sample_coordinates():
    """Sample Swiss coordinates (Bern)."""
    return Coordinates(
        latitude=46.947,
        longitude=7.447,
        altitude_m=541,
    )


@pytest.fixture
def sample_region():
    """Sample Swiss region (Bern)."""
    return Region(
        canton="BE",
        district="Bern-Mittelland",
        municipality="Bern",
    )


@pytest.fixture
def sample_location(sample_coordinates, sample_region):
    """Sample location (Bern, Switzerland)."""
    return Location(
        name="Bern",
        coordinates=sample_coordinates,
        region=sample_region,
        country="CH",
        type="city",
        description="Capital of Switzerland",
        population=134392,
        elevation_m=541,
    )


@pytest.fixture
def sample_temperature():
    """Sample temperature data."""
    return Temperature(
        value=15.2,
        min=8.5,
        max=19.3,
        apparent=14.1,
        dew_point=10.2,
    )


@pytest.fixture
def sample_weather(sample_temperature):
    """Sample weather data."""
    return Weather(
        timestamp=datetime(2024, 1, 20, 14, 0, 0),
        description="Sunny",
        code=1,
        temperature=sample_temperature,
        humidity_percent=65,
        wind_speed_kmh=12,
        wind_direction_deg=220,
        pressure_hpa=1013.25,
        cloud_cover_percent=20,
    )


@pytest.fixture
def sample_price():
    """Sample price."""
    return Price(
        amount=125.50,
        currency="CHF",
    )


@pytest.fixture
def sample_pricing_info(sample_price):
    """Sample pricing information."""
    return PricingInfo(
        standard_price=sample_price,
        currency="CHF",
        pricing_type="one-way",
    )


@pytest.fixture
def sample_date_range():
    """Sample date range (7 days)."""
    return DateRange(
        start_date=date(2024, 7, 15),
        end_date=date(2024, 7, 22),
    )


@pytest.fixture
def swiss_cantons():
    """List of valid Swiss cantons."""
    return [
        'AG', 'AI', 'AR', 'BE', 'BL', 'BS', 'FR', 'GE', 'GL', 'GR',
        'JU', 'LU', 'NE', 'NW', 'OW', 'SG', 'SH', 'SO', 'SZ', 'TG',
        'TI', 'UR', 'VD', 'VS', 'ZG', 'ZH'
    ]
