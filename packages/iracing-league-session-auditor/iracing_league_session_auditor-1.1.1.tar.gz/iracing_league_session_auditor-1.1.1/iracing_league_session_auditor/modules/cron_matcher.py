"""
Cron matching utility for comparing time values against cron expressions.
"""

import datetime
from typing import final, cast


@final
class CronMatcher:
    """
    Utility class to match a timestamp against a cron expression with a tolerance.

    This is used for validating that session launch times occur at expected times.
    """

    def __init__(self, cron_expr: str = "30 20 * * 2", minute_tolerance: int = 15):
        """
        Initialize the CronMatcher with a cron expression and tolerance.

        Args:
            cron_expr: Cron expression in format "minute hour day_of_month month day_of_week"
            minute_tolerance: Number of minutes before/after the cron time that is considered valid
        """
        self.cron_expr = cron_expr
        self.minute_tolerance = minute_tolerance
        # Parse cron fields
        fields = cron_expr.strip().split()
        if len(fields) != 5:
            raise ValueError(f"Invalid cron expression: {cron_expr}")
        (
            self.cron_minute,
            self.cron_hour,
            self.cron_dom,
            self.cron_month,
            self.cron_wday,
        ) = fields

    @staticmethod
    def _parse_field(field: str, min_val: int, max_val: int) -> set[int]:
        """Parse a cron field and return the set of valid values."""
        if field == "*":
            return set(range(min_val, max_val + 1))
        vals = cast(set[int], set())
        for part in field.split(","):
            if "-" in part:
                start, end = map(int, part.split("-"))
                vals.update(range(start, end + 1))
            else:
                vals.add(int(part))
        return vals

    @staticmethod
    def _parse_cron_weekdays(field: str) -> set[int]:
        """
        Parse the weekday field of a cron expression.

        Converts from cron weekday format (0=Sunday) to Python weekday format (0=Monday).
        """
        # Cron: 0=Sunday, 1=Monday, ..., 6=Saturday
        # Python: 0=Monday, ..., 6=Sunday
        vals = cast(set[int], set())
        if field == "*":
            return set(range(0, 7))
        for part in field.split(","):
            if "-" in part:
                start, end = map(int, part.split("-"))
                for cron_wd in range(start, end + 1):
                    py_wd = (cron_wd - 1) % 7
                    vals.add(py_wd)
            else:
                cron_wd = int(part)
                py_wd = (cron_wd - 1) % 7
                vals.add(py_wd)
        return vals

    def _nearest_cron_time(self, dt: datetime.datetime):
        """Find the nearest time that matches the cron expression."""
        # Only supports minute, hour, and weekday fields for simplicity
        minutes = self._parse_field(self.cron_minute, 0, 59)
        hours = self._parse_field(self.cron_hour, 0, 23)
        weekdays = self._parse_cron_weekdays(self.cron_wday)
        # Find the closest time in the past or future matching the cron
        # Search up to 1 week in both directions
        best_dt = None
        best_delta = None
        for offset in range(-7 * 24 * 60, 7 * 24 * 60 + 1):
            candidate = dt + datetime.timedelta(minutes=offset)
            if (
                candidate.minute in minutes
                and candidate.hour in hours
                and candidate.weekday() in weekdays
            ):
                delta = abs((candidate - dt).total_seconds()) / 60
                if best_delta is None or delta < best_delta:
                    best_delta = delta
                    best_dt = candidate
                    if best_delta == 0:
                        break
        return best_dt, best_delta

    def to_json(self) -> dict[str, str | int]:
        """Return a serialized representation of the CronMatcher."""
        return {"cron": self.cron_expr, "margin": self.minute_tolerance}

    def __call__(self, value: str) -> tuple[bool, str]:
        """
        Check if a timestamp is within tolerance of the cron schedule.

        Args:
            value: ISO format timestamp string (e.g. "2023-01-01T12:30:00Z")

        Returns:
            Tuple of (bool, str) where the bool indicates if the time is valid
            and the string provides a descriptive message
        """
        try:
            dt = datetime.datetime.fromisoformat(value.replace("Z", "+00:00"))
            nearest, delta = self._nearest_cron_time(dt)
            if delta is not None and delta <= self.minute_tolerance:
                return (
                    True,
                    f"Launch time OK: {dt.strftime('%A %Y-%m-%d %H:%M %Z')} (nearest cron: {nearest.strftime('%A %Y-%m-%d %H:%M %Z') if nearest else nearest}, delta {delta:.1f} min)",
                )
            else:
                return (
                    False,
                    f"Time not within {self.minute_tolerance} min of cron ({self.cron_expr}): {dt.strftime('%A %Y-%m-%d %H:%M %Z')} (nearest: {nearest.strftime('%A %Y-%m-%d %H:%M %Z') if nearest else nearest}, delta {delta:.1f} min)",
                )
        except Exception as call_exception:
            return False, f"Invalid date format: {value} ({call_exception})"
