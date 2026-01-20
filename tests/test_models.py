"""Tests for shared data models."""

import pytest
from datetime import date, datetime
from swiss_ai_mcp_commons import (
    Coordinates,
    Location,
    Region,
    Weather,
    Temperature,
    SnowConditions,
    Price,
    FareOption,
    PricingInfo,
    DateRange,
    TimeRange,
)


class TestCoordinates:
    """Test geographic coordinates model."""

    def test_valid_coordinates(self, sample_coordinates):
        """Test valid Swiss coordinates."""
        assert sample_coordinates.latitude == 46.947
        assert sample_coordinates.longitude == 7.447
        assert sample_coordinates.altitude_m == 541

    def test_coordinates_validation(self):
        """Test coordinate validation."""
        # Valid Swiss coordinates
        coords = Coordinates(latitude=45.0, longitude=8.0)
        assert coords.latitude == 45.0

    def test_latitude_out_of_range(self):
        """Test invalid latitude."""
        with pytest.raises(ValueError):
            Coordinates(latitude=91.0, longitude=7.0)

        with pytest.raises(ValueError):
            Coordinates(latitude=-91.0, longitude=7.0)

    def test_longitude_out_of_range(self):
        """Test invalid longitude."""
        with pytest.raises(ValueError):
            Coordinates(latitude=46.0, longitude=181.0)

        with pytest.raises(ValueError):
            Coordinates(latitude=46.0, longitude=-181.0)


class TestRegion:
    """Test Swiss region model."""

    def test_valid_region(self, sample_region):
        """Test valid region."""
        assert sample_region.canton == "BE"
        assert sample_region.district == "Bern-Mittelland"
        assert sample_region.municipality == "Bern"

    def test_canton_normalization(self):
        """Test canton code normalization to uppercase."""
        region = Region(canton="be")
        assert region.canton == "BE"

    def test_invalid_canton(self):
        """Test invalid canton code."""
        with pytest.raises(ValueError):
            Region(canton="XX")

    def test_all_swiss_cantons(self, swiss_cantons):
        """Test all valid Swiss cantons."""
        for canton_code in swiss_cantons:
            region = Region(canton=canton_code)
            assert region.canton == canton_code


class TestLocation:
    """Test location model."""

    def test_valid_location(self, sample_location):
        """Test valid location."""
        assert sample_location.name == "Bern"
        assert sample_location.country == "CH"
        assert sample_location.type == "city"

    def test_country_normalization(self):
        """Test country code normalization."""
        location = Location(
            name="Zurich",
            coordinates=Coordinates(latitude=47.3, longitude=8.5),
            country="ch",
        )
        assert location.country == "CH"

    def test_location_json_schema(self, sample_location):
        """Test location can be serialized to JSON."""
        json_data = sample_location.model_dump_json()
        assert "Bern" in json_data
        assert "46.947" in json_data

    def test_location_with_population(self):
        """Test location with population."""
        location = Location(
            name="Zurich",
            coordinates=Coordinates(latitude=47.3, longitude=8.5),
            population=400000,
        )
        assert location.population == 400000


class TestTemperature:
    """Test temperature model."""

    def test_valid_temperature(self, sample_temperature):
        """Test valid temperature."""
        assert sample_temperature.value == 15.2
        assert sample_temperature.min == 8.5
        assert sample_temperature.max == 19.3

    def test_min_max_relationship(self):
        """Test temperature min/max relationship."""
        # Pydantic doesn't validate relationships by default
        # This test documents expected behavior
        temp = Temperature(value=10, min=5, max=15)
        assert temp.min <= temp.value <= temp.max


class TestWeather:
    """Test weather model."""

    def test_valid_weather(self, sample_weather):
        """Test valid weather data."""
        assert sample_weather.description == "Sunny"
        assert sample_weather.humidity_percent == 65
        assert sample_weather.wind_speed_kmh == 12

    def test_weather_with_snow(self, sample_weather):
        """Test weather with snow conditions."""
        snow = SnowConditions(depth_cm=50, fresh_cm=10)
        weather = Weather(
            timestamp=sample_weather.timestamp,
            description="Snowy",
            temperature=sample_weather.temperature,
            snow_conditions=snow,
        )
        assert weather.snow_conditions.depth_cm == 50

    def test_humidity_range(self):
        """Test humidity validation."""
        weather = Weather(
            timestamp=datetime.now(),
            description="Test",
            temperature=Temperature(value=10),
            humidity_percent=50,
        )
        assert 0 <= weather.humidity_percent <= 100

        with pytest.raises(ValueError):
            Weather(
                timestamp=datetime.now(),
                description="Test",
                temperature=Temperature(value=10),
                humidity_percent=101,
            )


class TestSnowConditions:
    """Test snow conditions model."""

    def test_valid_snow_conditions(self):
        """Test valid snow data."""
        snow = SnowConditions(
            depth_cm=180,
            fresh_cm=25,
            density_percent=85,
            avalanche_risk=2,
        )
        assert snow.depth_cm == 180
        assert snow.fresh_cm == 25

    def test_depth_non_negative(self):
        """Test depth must be non-negative."""
        with pytest.raises(ValueError):
            SnowConditions(depth_cm=-1)

    def test_avalanche_risk_range(self):
        """Test avalanche risk level validation."""
        for risk in [1, 2, 3, 4, 5]:
            snow = SnowConditions(depth_cm=100, avalanche_risk=risk)
            assert snow.avalanche_risk == risk

        with pytest.raises(ValueError):
            SnowConditions(depth_cm=100, avalanche_risk=6)


class TestPrice:
    """Test price model."""

    def test_valid_price(self, sample_price):
        """Test valid price."""
        assert sample_price.amount == 125.50
        assert sample_price.currency == "CHF"

    def test_price_display(self, sample_price):
        """Test price display format."""
        display = sample_price.display
        assert "CHF" in display
        assert "125.50" in display

    def test_default_currency(self):
        """Test default CHF currency."""
        price = Price(amount=100)
        assert price.currency == "CHF"

    def test_price_non_negative(self):
        """Test price must be non-negative."""
        with pytest.raises(ValueError):
            Price(amount=-10)


class TestFareOption:
    """Test fare option model."""

    def test_valid_fare_option(self):
        """Test valid fare option."""
        base = Price(amount=89.00)
        total = Price(amount=99.50)
        fare = FareOption(
            base_price=base,
            total_price=total,
            fare_class="Economy",
        )
        assert fare.base_price.amount == 89.00
        assert fare.total_price.amount == 99.50

    def test_fare_with_discount(self):
        """Test fare with rail card discount."""
        base = Price(amount=100)
        total = Price(amount=75)
        fare = FareOption(
            base_price=base,
            total_price=total,
            rail_card_discount=25.0,
        )
        assert fare.rail_card_discount == 25.0

    def test_baggage_allowance(self):
        """Test baggage allowance."""
        fare = FareOption(
            base_price=Price(amount=100),
            total_price=Price(amount=100),
            baggage_included=2,
        )
        assert fare.baggage_included == 2


class TestPricingInfo:
    """Test pricing information model."""

    def test_valid_pricing_info(self, sample_pricing_info):
        """Test valid pricing information."""
        assert sample_pricing_info.standard_price.amount == 125.50
        assert sample_pricing_info.currency == "CHF"

    def test_best_price_with_discount(self):
        """Test best_price property with discount."""
        standard = Price(amount=100)
        discounted = Price(amount=75)
        pricing = PricingInfo(
            standard_price=standard,
            discounted_price=discounted,
        )
        assert pricing.best_price.amount == 75

    def test_best_price_without_discount(self, sample_pricing_info):
        """Test best_price property without discount."""
        assert sample_pricing_info.best_price.amount == 125.50

    def test_savings_amount(self):
        """Test savings calculation."""
        standard = Price(amount=100)
        discounted = Price(amount=75)
        pricing = PricingInfo(
            standard_price=standard,
            discounted_price=discounted,
        )
        assert pricing.savings_amount == 25

    def test_savings_percent(self):
        """Test savings percentage."""
        pricing = PricingInfo(
            standard_price=Price(amount=100),
            savings_percent=25.0,
        )
        assert pricing.savings_percent == 25.0


class TestDateRange:
    """Test date range model."""

    def test_valid_date_range(self, sample_date_range):
        """Test valid date range."""
        assert sample_date_range.start_date == date(2024, 7, 15)
        assert sample_date_range.end_date == date(2024, 7, 22)

    def test_days_property(self, sample_date_range):
        """Test days property calculation."""
        assert sample_date_range.days == 8  # 15-22 inclusive

    def test_end_before_start(self):
        """Test end date must be after start date."""
        with pytest.raises(ValueError):
            DateRange(
                start_date=date(2024, 7, 22),
                end_date=date(2024, 7, 15),
            )

    def test_same_day_range(self):
        """Test same day date range."""
        dr = DateRange(
            start_date=date(2024, 7, 15),
            end_date=date(2024, 7, 15),
        )
        assert dr.days == 1

    def test_is_current_past_future(self):
        """Test temporal properties."""
        past_range = DateRange(
            start_date=date(2020, 1, 1),
            end_date=date(2020, 1, 31),
        )
        assert past_range.is_past

        future_range = DateRange(
            start_date=date(2099, 1, 1),
            end_date=date(2099, 1, 31),
        )
        assert future_range.is_future


class TestTimeRange:
    """Test time range model."""

    def test_valid_time_range(self):
        """Test valid time range."""
        from time import time as time_func
        from datetime import time
        tr = TimeRange(
            start_time=time(9, 0),
            end_time=time(17, 30),
        )
        assert tr.start_time == time(9, 0)
        assert tr.end_time == time(17, 30)

    def test_end_after_start(self):
        """Test end time must be after start time."""
        from datetime import time
        with pytest.raises(ValueError):
            TimeRange(
                start_time=time(17, 30),
                end_time=time(9, 0),
            )
