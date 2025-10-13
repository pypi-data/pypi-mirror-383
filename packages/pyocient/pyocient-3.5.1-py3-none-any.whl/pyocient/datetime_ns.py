import datetime
from typing import Dict, Optional


class datetime_ns(datetime.datetime):
    """
    Enhanced datetime class with nanosecond precision.
    """

    # Store nanoseconds as an additional attribute
    _ns: int = 0

    def __new__(
        cls,
        year: int,
        month: int,
        day: int,
        hour: int = 0,
        minute: int = 0,
        second: int = 0,
        microsecond: int = 0,
        tzinfo: Optional[datetime.tzinfo] = None,
        nanosecond: Optional[int] = None,
        *,
        fold: int = 0,
    ) -> "datetime_ns":
        """
        Create a new datetime_ns object with nanosecond precision.

        Args:
            year: Year value
            month: Month value (1-12)
            day: Day value (1-31)
            hour: Hour value (0-23)
            minute: Minute value (0-59)
            second: Second value (0-59)
            microsecond: Microsecond value (0-999999)
            tzinfo: Timezone info
            nanosecond: Nanosecond value (0-999)
            fold: Fold value (0 or 1)

        Returns:
            A new datetime_ns instance
        """
        # Validate nanosecond range
        if nanosecond is not None and not 0 <= nanosecond < 1000:
            raise ValueError("nanosecond must be in 0..999")

        # Create the datetime object
        obj = datetime.datetime.__new__(cls, year, month, day, hour, minute, second, microsecond, tzinfo, fold=fold)

        # Add nanosecond attribute
        obj._ns = nanosecond if nanosecond is not None else 0

        return obj

    @property
    def nanosecond(self) -> int:
        """
        Get the nanosecond value (0-999).

        Returns:
            The nanosecond part of the datetime
        """
        return self._ns

    @classmethod
    def utcfromtimestamp(cls, t: float) -> "datetime_ns":
        """
        Create a datetime_ns object from a timestamp, preserving nanosecond precision.

        Args:
            t: UNIX timestamp (float with nanosecond precision)

        Returns:
            A datetime_ns object with nanosecond precision
        """
        # Extract whole seconds and fractional part
        seconds = int(t)
        fractional = t - seconds

        # Convert to microseconds and nanoseconds
        total_ns = int(fractional * 1_000_000_000)
        microseconds = total_ns // 1000
        nanoseconds = total_ns % 1000

        # Create base datetime using the parent method but with our class
        base_dt = super().utcfromtimestamp(seconds)

        # Create new datetime_ns with microseconds and nanoseconds
        return cls(
            base_dt.year,
            base_dt.month,
            base_dt.day,
            base_dt.hour,
            base_dt.minute,
            base_dt.second,
            microseconds,
            base_dt.tzinfo,
            nanoseconds,
            fold=base_dt.fold,
        )

    def isoformat(self, sep: str = "T", timespec: str = "auto") -> str:
        """
        Return the datetime as an ISO 8601 formatted string with nanosecond support.

        Args:
            sep: Separator between date and time parts
            timespec: Precision specification ('auto', 'hours', 'minutes', 'seconds',
                      'milliseconds', 'microseconds', or 'nanoseconds')

        Returns:
            ISO formatted string with specified precision
        """
        if timespec == "nanoseconds":
            # Format with nanoseconds
            base = super().isoformat(sep, "microseconds")
            # Add nanoseconds to the microseconds part
            body, _, fractional = base.rpartition(".")
            return f"{body}.{fractional[:6]}{self._ns:03d}"
            return base
        elif timespec == "auto" and self._ns:
            # For 'auto', include nanoseconds if non-zero
            base = super().isoformat(sep, "microseconds")
            body, _, fractional = base.rpartition(".")
            return f"{body}.{fractional[:6]}{self._ns:03d}"
        else:
            # Use standard formatting for other specs
            return super().isoformat(sep, timespec)

    def timestamp(self) -> float:
        """
        Return UNIX timestamp (seconds since epoch) with nanosecond precision.

        Returns:
            Float timestamp with nanosecond precision
        """
        # Get the base timestamp from parent
        base_timestamp = super().timestamp()

        # Add nanosecond precision
        ns_part = self._ns / 1_000_000_000
        return base_timestamp + ns_part

    @classmethod
    def from_timestamp_ns(cls, timestamp_ns: int, tz: datetime.tzinfo = datetime.timezone.utc) -> "datetime_ns":
        """
        Create a datetime_ns object from a nanosecond timestamp (integer).

        Args:
            timestamp_ns: Nanoseconds since Unix epoch (January 1, 1970)
            tz: Optional timezone, if None UTC is used

        Returns:
            A datetime_ns object with nanosecond precision
        """
        # Calculate seconds and nanoseconds parts without floating point conversion
        seconds = timestamp_ns // 1_000_000_000
        nanoseconds_remainder = timestamp_ns % 1_000_000_000
        microseconds = nanoseconds_remainder // 1_000
        nanoseconds = nanoseconds_remainder % 1_000

        # Create base datetime from seconds timestamp
        if tz == datetime.timezone.utc:
            base_dt = datetime.datetime.utcfromtimestamp(seconds)
        else:
            base_dt = datetime.datetime.fromtimestamp(seconds, tz)

        # Add microseconds separately
        base_dt = base_dt.replace(microsecond=microseconds)

        # Create new datetime_ns with nanoseconds
        return cls(
            base_dt.year,
            base_dt.month,
            base_dt.day,
            base_dt.hour,
            base_dt.minute,
            base_dt.second,
            base_dt.microsecond,
            base_dt.tzinfo,
            nanoseconds,
            fold=base_dt.fold,
        )

    def timestamp_ns(self) -> int:
        """
        Return UNIX timestamp as nanoseconds since epoch (integer).

        Returns:
            Integer timestamp in nanoseconds
        """
        # Get the base timestamp in seconds
        seconds = int(super().timestamp())

        # Convert seconds to nanoseconds and add microseconds and nanoseconds
        return seconds * 1_000_000_000 + self.microsecond * 1_000 + self._ns

    def __str__(self) -> str:
        """
        String representation including nanoseconds if present.

        Returns:
            String representation of the datetime with nanoseconds
        """
        if self._ns:
            return self.isoformat(" ", timespec="nanoseconds")
        else:
            return super().__str__()

    def __repr__(self) -> str:
        """
        Formal string representation including nanoseconds.

        Returns:
            Formal string representation with nanoseconds
        """
        base_repr = super().__repr__()

        # Add nanosecond parameter if non-zero
        if self._ns:
            # Find the closing parenthesis
            insert_pos = base_repr.rfind(")")
            return f"{base_repr[:insert_pos]}, nanosecond={self._ns}{base_repr[insert_pos:]}"
        return base_repr

    def __copy__(self) -> "datetime_ns":
        """Create and return a copy of the current object."""
        return datetime_ns(
            self.year,
            self.month,
            self.day,
            self.hour,
            self.minute,
            self.second,
            self.microsecond,
            self.tzinfo,
            self.nanosecond,
            fold=self.fold,
        )

    def __deepcopy__(self, memo: Dict[int, object]) -> "datetime_ns":
        """
        Create and return a deep copy of the current object.

        This is the same as a normal copy as datetime_ns does not have any attributes that are mutable aside from
        tzinfo, and tzinfo objects are not meant to be copied.
        """
        return self.__copy__()
