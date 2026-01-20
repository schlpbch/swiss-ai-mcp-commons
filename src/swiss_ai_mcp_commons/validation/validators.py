"""Input validation utilities for Swiss MCPs."""

from datetime import date, datetime, timedelta
from typing import Optional
from .exceptions import ValidationError


def validate_date_range(
    start_date: date,
    end_date: date,
    min_days: int = 0,
    max_days: int = 365,
    allow_past: bool = False,
) -> tuple[date, date]:
    """Validate date range parameters.

    Args:
        start_date: Trip start date
        end_date: Trip end date
        min_days: Minimum duration in days (0 = same day allowed)
        max_days: Maximum duration in days
        allow_past: Whether to allow past dates

    Returns:
        Tuple of validated (start_date, end_date)

    Raises:
        ValidationError: If dates are invalid
    """
    today = date.today()

    # Check for past dates
    if not allow_past and start_date < today:
        raise ValidationError(
            "Start date cannot be in the past",
            field="start_date",
            value=start_date,
        )

    # Check end is after start
    if end_date < start_date:
        raise ValidationError(
            "End date must be after start date",
            field="end_date",
            value=end_date,
        )

    # Calculate duration
    duration = (end_date - start_date).days

    # Check minimum duration
    if duration < min_days:
        raise ValidationError(
            f"Trip duration must be at least {min_days} days",
            field="duration",
            value=duration,
        )

    # Check maximum duration
    if duration > max_days:
        raise ValidationError(
            f"Trip duration cannot exceed {max_days} days",
            field="duration",
            value=duration,
        )

    return start_date, end_date


def validate_currency_code(currency: str) -> str:
    """Validate ISO 4217 currency code.

    Args:
        currency: Currency code (e.g., 'CHF', 'USD', 'EUR')

    Returns:
        Uppercase currency code

    Raises:
        ValidationError: If currency code is invalid
    """
    # Common currency codes used in Swiss context
    valid_currencies = {
        'CHF', 'EUR', 'USD', 'GBP', 'JPY', 'AUD', 'CAD', 'CNY', 'SEK', 'NOK',
        'DKK', 'PLN', 'CZK', 'HUF', 'RON', 'BGN', 'HRK', 'RUB', 'TRY', 'INR',
        'BRL', 'MXN', 'ZAR', 'SGD', 'HKD', 'NZD', 'KRW', 'THB', 'MYR', 'PHP',
        'IDR', 'VND', 'AED', 'SAR', 'QAR', 'ILS', 'ARS', 'CLP', 'COP', 'PEN',
        'UYU', 'EGP', 'OMR', 'KWD', 'BHD', 'JOD', 'LBP'
    }

    upper_code = currency.upper()

    if len(upper_code) != 3:
        raise ValidationError(
            "Currency code must be 3 characters",
            field="currency",
            value=currency,
        )

    if upper_code not in valid_currencies:
        raise ValidationError(
            f"Invalid or unsupported currency code: {currency}",
            field="currency",
            value=currency,
        )

    return upper_code


def validate_swiss_canton(canton: str) -> str:
    """Validate Swiss canton code.

    Args:
        canton: Canton code (e.g., 'BE', 'ZH', 'VD')

    Returns:
        Uppercase canton code

    Raises:
        ValidationError: If canton code is invalid
    """
    valid_cantons = {
        'AG', 'AI', 'AR', 'BE', 'BL', 'BS', 'FR', 'GE', 'GL', 'GR',
        'JU', 'LU', 'NE', 'NW', 'OW', 'SG', 'SH', 'SO', 'SZ', 'TG',
        'TI', 'UR', 'VD', 'VS', 'ZG', 'ZH'
    }

    upper_code = canton.upper()

    if len(upper_code) != 2:
        raise ValidationError(
            "Canton code must be 2 characters",
            field="canton",
            value=canton,
        )

    if upper_code not in valid_cantons:
        raise ValidationError(
            f"Invalid Swiss canton code: {canton}",
            field="canton",
            value=canton,
        )

    return upper_code


def validate_email(email: str) -> str:
    """Validate email address format.

    Args:
        email: Email address

    Returns:
        Lowercase email address

    Raises:
        ValidationError: If email is invalid
    """
    email = email.strip().lower()

    if len(email) < 5 or len(email) > 254:
        raise ValidationError(
            "Email must be between 5 and 254 characters",
            field="email",
            value=email,
        )

    if "@" not in email:
        raise ValidationError(
            "Email must contain @ symbol",
            field="email",
            value=email,
        )

    local, domain = email.rsplit("@", 1)

    if not local or not domain:
        raise ValidationError(
            "Email format is invalid",
            field="email",
            value=email,
        )

    if "." not in domain:
        raise ValidationError(
            "Email domain must contain a dot",
            field="email",
            value=email,
        )

    return email


def validate_phone(phone: str, country: str = "CH") -> str:
    """Validate phone number format.

    Args:
        phone: Phone number
        country: Country code for validation context

    Returns:
        Cleaned phone number

    Raises:
        ValidationError: If phone is invalid
    """
    # Remove common formatting characters but keep track of +
    has_plus = "+" in phone
    cleaned = "".join(c for c in phone if c.isdigit())

    if country == "CH":
        # Swiss numbers: +41 or 0 followed by 9 digits
        if has_plus:
            # International format: +41 followed by 9 digits
            if len(cleaned) != 11:  # 41 + 9 digits
                raise ValidationError(
                    "Invalid Swiss phone number (should be +41 + 9 digits)",
                    field="phone",
                    value=phone,
                )
        elif cleaned.startswith("0"):
            # Local format: 0 followed by 9 digits
            if len(cleaned) != 10:  # 0 + 9 digits
                raise ValidationError(
                    "Invalid Swiss phone number (should be 0 + 9 digits)",
                    field="phone",
                    value=phone,
                )
        else:
            raise ValidationError(
                "Swiss phone must start with +41 or 0",
                field="phone",
                value=phone,
            )
    else:
        # Basic validation: at least 7 digits
        if len(cleaned) < 7:
            raise ValidationError(
                "Phone number must contain at least 7 digits",
                field="phone",
                value=phone,
            )

    return cleaned


def validate_price(amount: float, min_price: float = 0, max_price: float = 1000000) -> float:
    """Validate price amount.

    Args:
        amount: Price amount
        min_price: Minimum allowed price
        max_price: Maximum allowed price

    Returns:
        Validated price amount

    Raises:
        ValidationError: If price is invalid
    """
    if amount < min_price:
        raise ValidationError(
            f"Price cannot be less than {min_price}",
            field="amount",
            value=amount,
        )

    if amount > max_price:
        raise ValidationError(
            f"Price cannot exceed {max_price}",
            field="amount",
            value=amount,
        )

    return round(amount, 2)
