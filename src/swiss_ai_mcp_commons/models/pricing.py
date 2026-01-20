"""Pricing and fare data models for Swiss MCPs."""

from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal


class Price(BaseModel):
    """Single price with currency."""

    amount: float = Field(..., ge=0, description="Price amount")
    currency: str = Field(default="CHF", description="ISO 4217 currency code")
    formatted: Optional[str] = Field(default=None, description="Formatted price string (e.g., 'CHF 125.50')")

    @property
    def display(self) -> str:
        """Get formatted price display."""
        if self.formatted:
            return self.formatted
        return f"{self.currency} {self.amount:.2f}"

    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "amount": 125.50,
                "currency": "CHF",
                "formatted": "CHF 125.50"
            }
        }


class FareOption(BaseModel):
    """Single fare option with class and restrictions."""

    base_price: Price = Field(..., description="Base fare price")
    total_price: Price = Field(..., description="Total price including taxes/fees")
    fare_class: str = Field(
        default="Economy",
        description="Fare class: Economy, Business, First, Comfort"
    )
    service_class: str = Field(
        default="M",
        description="GDS booking class (A-Z, single letter)"
    )
    restrictions: Optional[str] = Field(default=None, description="Fare restrictions")
    advance_purchase_days: Optional[int] = Field(
        default=None, ge=0,
        description="Days in advance required for this fare"
    )
    refundable: bool = Field(default=False, description="Whether fare is refundable")
    changeable: bool = Field(default=False, description="Whether flight/dates can be changed")
    seats_available: Optional[int] = Field(default=None, ge=0, description="Seats available at this fare")
    baggage_included: Optional[int] = Field(default=None, ge=0, description="Baggage allowance (pieces)")
    rail_card_discount: Optional[float] = Field(
        default=None, ge=0, le=100,
        description="Discount percentage for rail cards (0-100)"
    )

    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "base_price": {
                    "amount": 89.00,
                    "currency": "CHF"
                },
                "total_price": {
                    "amount": 99.50,
                    "currency": "CHF"
                },
                "fare_class": "Economy",
                "service_class": "M",
                "refundable": False,
                "changeable": False,
                "seats_available": 5,
                "rail_card_discount": 25.0
            }
        }


class PricingInfo(BaseModel):
    """Complete pricing information for a product/service."""

    standard_price: Price = Field(..., description="Standard/published price")
    discounted_price: Optional[Price] = Field(default=None, description="Discounted price if available")
    fare_options: list[FareOption] = Field(default_factory=list, description="Available fare options")
    taxes_fees: Optional[Price] = Field(default=None, description="Total taxes and fees")
    currency: str = Field(default="CHF", description="Primary currency for pricing")
    pricing_type: str = Field(
        default="one-way",
        description="Pricing type: one-way, round-trip, multi-city, package"
    )
    valid_until: Optional[str] = Field(default=None, description="When this pricing expires (ISO 8601)")
    discount_code: Optional[str] = Field(default=None, description="Applied discount code if any")
    savings_percent: Optional[float] = Field(
        default=None, ge=0, le=100,
        description="Savings percentage vs standard price"
    )

    @property
    def best_price(self) -> Price:
        """Get the best available price."""
        return self.discounted_price or self.standard_price

    @property
    def savings_amount(self) -> Optional[float]:
        """Calculate savings amount."""
        if self.discounted_price:
            return self.standard_price.amount - self.discounted_price.amount
        return None

    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "standard_price": {
                    "amount": 125.00,
                    "currency": "CHF"
                },
                "discounted_price": {
                    "amount": 93.75,
                    "currency": "CHF"
                },
                "currency": "CHF",
                "pricing_type": "one-way",
                "discount_code": "EARLY25",
                "savings_percent": 25.0,
                "fare_options": [
                    {
                        "base_price": {"amount": 89.00, "currency": "CHF"},
                        "total_price": {"amount": 99.50, "currency": "CHF"},
                        "fare_class": "Economy",
                        "refundable": False
                    }
                ]
            }
        }
