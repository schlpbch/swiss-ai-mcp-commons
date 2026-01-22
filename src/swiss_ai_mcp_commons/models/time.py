"""Time-related data models for Swiss MCPs."""

from pydantic import BaseModel, Field, field_validator, ConfigDict
from datetime import datetime, date, time
from typing import Optional


class TimeRange(BaseModel):
    """Time range with validation."""

    start_time: time = Field(..., description="Start time (HH:MM:SS)")
    end_time: time = Field(..., description="End time (HH:MM:SS)")
    duration_minutes: Optional[int] = Field(default=None, ge=0, description="Duration in minutes")

    @field_validator('end_time')
    @classmethod
    def validate_times(cls, v, info):
        """Ensure end time is after start time."""
        if 'start_time' in info.data and v <= info.data['start_time']:
            raise ValueError('end_time must be after start_time')
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "start_time": "09:00:00",
                "end_time": "17:30:00",
                "duration_minutes": 510
            }
        }
    )

    def __str__(self) -> str:
        """String representation of time range."""
        hours = self.duration_minutes // 60 if self.duration_minutes else 0
        mins = self.duration_minutes % 60 if self.duration_minutes else 0
        duration_str = f", {hours}h{mins}m" if self.duration_minutes else ""
        return f"TimeRange({self.start_time.strftime('%H:%M')} - {self.end_time.strftime('%H:%M')}{duration_str})"


class DateRange(BaseModel):
    """Date range for trip planning."""

    start_date: date = Field(..., description="Start date (YYYY-MM-DD)")
    end_date: date = Field(..., description="End date (YYYY-MM-DD)")
    duration_days: Optional[int] = Field(default=None, ge=0, description="Trip duration in days")

    @field_validator('end_date')
    @classmethod
    def validate_dates(cls, v, info):
        """Ensure end date is after start date."""
        if 'start_date' in info.data and v < info.data['start_date']:
            raise ValueError('end_date must be after or equal to start_date')
        return v

    @property
    def days(self) -> int:
        """Calculate number of days in range."""
        return (self.end_date - self.start_date).days + 1

    @property
    def is_past(self) -> bool:
        """Check if date range is in the past."""
        return self.end_date < date.today()

    @property
    def is_future(self) -> bool:
        """Check if date range is in the future."""
        return self.start_date > date.today()

    @property
    def is_current(self) -> bool:
        """Check if today is within the date range."""
        today = date.today()
        return self.start_date <= today <= self.end_date

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "start_date": "2024-07-15",
                "end_date": "2024-07-22",
                "duration_days": 8
            }
        }
    )

    def __str__(self) -> str:
        """String representation of date range."""
        days = self.days
        status = "past" if self.is_past else "current" if self.is_current else "future"
        return f"DateRange({self.start_date} to {self.end_date}, {days} days, {status})"
