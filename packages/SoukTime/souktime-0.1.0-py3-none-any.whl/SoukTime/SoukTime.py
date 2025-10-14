# datetime.py - full wrapper, override only current time

from _datetime import (
    date as _date,
    datetime as _datetime,
    time as _time,
    timedelta as _timedelta,
    timezone as _timezone,
    tzinfo as _tzinfo,
    UTC as _UTC,
    datetime_CAPI as _datetime_CAPI,
)
import sys

# --- Override date ---
class date(_date):
    @classmethod
    def today(cls):
        return cls(2000, 1, 1)


# --- Override datetime ---
class datetime(_datetime):
    @classmethod
    def now(cls, tz=None):
        return cls(2000, 1, 1, 0, 0, 0)

    @classmethod
    def utcnow(cls):
        return cls(2000, 1, 1, 0, 0, 0)

    @classmethod
    def today(cls):
        return cls(2000, 1, 1, 0, 0, 0)


# --- Re-export everything else unchanged ---
time = _time
timedelta = _timedelta
timezone = _timezone
tzinfo = _tzinfo
UTC = _UTC
datetime_CAPI = _datetime_CAPI

# constants
MINYEAR = _date.min.year
MAXYEAR = _date.max.year

# module metadata
__all__ = [
    "date", "time", "datetime", "timedelta", "timezone", "tzinfo", "UTC",
    "MINYEAR", "MAXYEAR", "datetime_CAPI", "sys"
]

__builtins__ = __builtins__